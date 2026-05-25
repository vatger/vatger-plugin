#pragma once

#include <chrono>
#include <condition_variable>
#include <memory>
#include <optional>
#include <string>
#include <thread>

#include "api/IRestClient.h"
#include "auth/AuthTypes.h"
#include "auth/IAuthService.h"
#include "module/IModule.h"
#include "module/IPlugin.h"
#include "system/ISystem.h"

namespace auth {

class AuthService : public interfaces::IAuthService, public vatger::IModule {
   public:
    AuthService(std::unique_ptr<interfaces::IRestClient> restClient, std::shared_ptr<interfaces::ISystem> system,
                std::string baseUrl = "http://localhost:8000",
                std::chrono::milliseconds pollingInterval = std::chrono::seconds(5));
    ~AuthService();

    bool isAuthenticated() override;
    std::optional<std::string> getToken() override;
    AuthFlowResult startAuthFlow() override;

    void init(vatger::IPlugin* plugin) override;
    void handleOnCompileCommand(const std::string& command) override;

   private:
    void validateToken();
    void pollToken(std::stop_token stopToken, PluginTokenStartDTO dto);

    std::unique_ptr<interfaces::IRestClient> m_restClient;
    std::shared_ptr<interfaces::ISystem> m_system;

    std::optional<std::string> m_token;
    std::optional<PluginTokenStartDTO> m_pluginTokenStartDTO;
    std::string m_baseUrl;

    std::jthread m_pollingThread;
    std::chrono::milliseconds m_pollingInterval;
    std::condition_variable_any m_cv;
    std::mutex m_cvMutex;

    vatger::IPlugin* m_plugin = nullptr;
};

}  // namespace auth