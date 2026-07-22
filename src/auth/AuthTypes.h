#pragma once

#include <nlohmann/json.hpp>

namespace auth {
struct PluginTokenStartDTO {
    std::string userRedirectUrl;
    std::string pollingUrl;
    std::string pollingSecret;
};

inline void from_json(const nlohmann::json& j, PluginTokenStartDTO& dto) {
    j.at("userRedirectUrl").get_to(dto.userRedirectUrl);
    j.at("pollingUrl").get_to(dto.pollingUrl);
    j.at("pollingSecret").get_to(dto.pollingSecret);
}

struct PluginTokenPollDTO {
    bool ready = false;
    std::string token;
};

inline void from_json(const nlohmann::json& j, PluginTokenPollDTO& dto) {
    j.at("ready").get_to(dto.ready);
    j.at("token").get_to(dto.token);
}

struct PluginTokenIntrospectionDTO {
    bool active;
    std::string userId;
};

inline void from_json(const nlohmann::json& j, PluginTokenIntrospectionDTO& dto) {
    j.at("active").get_to(dto.active);
    j.at("user_id").get_to(dto.userId);
}

enum class AuthFlowStatus {
    Success,
    NetworkError,
    ParseError,
};

struct AuthFlowResult {
    AuthFlowStatus status;
    std::string redirectUrl;
    std::string errorMessage;

    static AuthFlowResult ok(std::string redirectUrl) { return {AuthFlowStatus::Success, std::move(redirectUrl), ""}; }

    static AuthFlowResult error(AuthFlowStatus status, std::string message) { return {status, "", std::move(message)}; }
};

}  // namespace auth
