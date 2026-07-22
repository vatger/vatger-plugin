#include "AuthService.h"

#include <nlohmann/json.hpp>

using json = nlohmann::json;
using namespace auth;

AuthService::AuthService(std::unique_ptr<interfaces::IRestClient> restClient,
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
    const auto response = m_restClient->post(m_baseUrl + "/api/v1/plugin-token/start", "");

    if (response.statusCode != 200) {
        return AuthFlowResult::error(AuthFlowStatus::NetworkError,
                                     "Server returned " + std::to_string(response.statusCode));
    }

    m_pluginTokenStartDTO = json::parse(response.body).get<PluginTokenStartDTO>();

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

    const std::unordered_map<std::string, std::string> headers = {{"Authorization", "Bearer " + m_token.value()}};
    const auto response = m_restClient->get(m_baseUrl + "/api/v1/plugin-token/me", headers);

    if (response.statusCode != 200) {
        m_token.reset();
        return;
    }

    const auto response_dto = json::parse(response.body).get<PluginTokenIntrospectionDTO>();
    if (!response_dto.active) {
        m_token.reset();
    }
}

void AuthService::pollToken(std::stop_token stopToken, PluginTokenStartDTO dto) {
    json body;
    body["secret"] = dto.pollingSecret;
    const std::string bodyStr = body.dump();
    const std::string pollingUrl = dto.pollingUrl;

    while (!stopToken.stop_requested()) {
        {
            std::unique_lock lock(m_cvMutex);
            m_cv.wait_for(lock, stopToken, m_pollingInterval, [&stopToken] { return stopToken.stop_requested(); });
        }

        if (stopToken.stop_requested()) break;

        const auto response = m_restClient->post(pollingUrl, bodyStr);
        const auto response_dto = json::parse(response.body).get<PluginTokenPollDTO>();

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