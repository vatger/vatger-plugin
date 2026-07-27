#include "AuthService.h"

#include <nlohmann/json.hpp>

using json = nlohmann::json;
using namespace auth;

AuthService::AuthService(std::shared_ptr<interfaces::IRestClient> restClient,
                         std::shared_ptr<interfaces::ISystem> system, std::string baseUrl,
                         std::chrono::milliseconds pollingInterval)
    : m_restClient(std::move(restClient)),
      m_system(system),
      m_baseUrl(std::move(baseUrl)),
      m_pollingInterval(pollingInterval) {}

AuthService::~AuthService() {}

bool AuthService::isAuthenticated() {
    if (!m_token.has_value()) {
        validateToken();
    }
    return m_token.has_value();
}

std::optional<std::string> AuthService::getToken() {
    if (!m_token.has_value()) {
        validateToken();
    }
    return m_token;
}

AuthFlowResult AuthService::startAuthFlow() {
    std::shared_lock lock(config_mutex_);
    const std::unordered_map<std::string, std::string> headers = {{"Content-Type", "application/json"}};
    const auto response = m_restClient->post(m_baseUrl + "/api/v1/plugin-token/start", "", headers);

    if (response.statusCode != 200) {
        return AuthFlowResult::error(AuthFlowStatus::NetworkError,
                                     "Server returned " + std::to_string(response.statusCode));
    }

    try {
        m_pluginTokenStartDTO = json::parse(response.body).get<PluginTokenStartDTO>();
    } catch (const json::exception& e) {
        return AuthFlowResult::error(AuthFlowStatus::ParseError,
                                     std::string("Failed to parse start response: ") + e.what());
    }

    if (!m_pluginTokenStartDTO.has_value()) {
        return AuthFlowResult::error(AuthFlowStatus::ParseError, "Failed to parse start response");
    }

    const auto dto = m_pluginTokenStartDTO.value();
    m_system->openUrl(dto.userRedirectUrl);
    m_pollingThread = std::jthread([this, dto](std::stop_token st) { pollToken(st, dto); });

    return AuthFlowResult::ok(dto.userRedirectUrl);
}

void AuthService::validateToken() {
    m_token = m_system->getDeviceToken();
    if (!m_token.has_value()) return;

    std::shared_lock lock(config_mutex_);
    const std::unordered_map<std::string, std::string> headers = {{"Authorization", "Bearer " + m_token.value()}};
    const auto response = m_restClient->get(m_baseUrl + "/api/v1/plugin-token/me", headers);

    if (response.statusCode != 200) {
        m_token.reset();
        return;
    }

    PluginTokenIntrospectionDTO response_dto;
    try {
        response_dto = json::parse(response.body).get<PluginTokenIntrospectionDTO>();
    } catch (const json::exception& e) {
        m_token.reset();
        return;
    }

    if (!response_dto.active) {
        m_token.reset();
    }
}

void AuthService::pollToken(std::stop_token stopToken, PluginTokenStartDTO dto) {
    json body;
    body["secret"] = dto.pollingSecret;
    const std::string bodyStr = body.dump();
    const std::string pollingUrl = dto.pollingUrl;
    const std::unordered_map<std::string, std::string> headers = {{"Content-Type", "application/json"}};

    while (!stopToken.stop_requested()) {
        {
            std::unique_lock lock(m_cvMutex);
            m_cv.wait_for(lock, stopToken, m_pollingInterval, [&stopToken] { return stopToken.stop_requested(); });
        }

        if (stopToken.stop_requested()) break;

        const auto response = m_restClient->post(pollingUrl, bodyStr, headers);

        if (response.statusCode != 200) {
            continue;
        }

        PluginTokenPollDTO response_dto;
        try {
            response_dto = json::parse(response.body).get<PluginTokenPollDTO>();
        } catch (const json::exception& e) {
            continue;
        }

        if (!response_dto.ready) continue;

        m_system->saveDeviceToken(response_dto.token);
        m_token = response_dto.token;
        m_pluginTokenStartDTO.reset();
        break;
    }
}

void AuthService::init(vatger::IPlugin* plugin) {
    m_plugin = plugin;
    m_plugin->RegisterModuleOnCompileCommand("auth", this);
};

void AuthService::OnConfigChange(const config::PluginConfig& config) {
    std::unique_lock lock(config_mutex_);
    m_baseUrl = config.server_url;
}

void AuthService::handleOnCompileCommand(const std::string& command) {
    // FIXME: use BackgroundExecuter to avoid small EuroScope freezes
    if (command == "status") {
        const auto isAuthenticated = this->isAuthenticated();
        if (isAuthenticated) {
            m_plugin->DisplayMessage("Plugin is authenticated", "Auth");
        } else {
            m_plugin->DisplayMessage("Plugin is not authenticated", "Auth");
        }
    } else if (command == "start") {
        m_plugin->DisplayMessage("Starting Auth Flow", "Auth");
        this->startAuthFlow();
    }
};