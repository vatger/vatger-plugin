#pragma once

#include <chrono>
#include <condition_variable>
#include <memory>
#include <optional>
#include <shared_mutex>
#include <string>
#include <thread>

#include "api/IRestClient.h"
#include "auth/AuthTypes.h"
#include "auth/IAuthModule.h"
#include "config/PluginConfig.h"
#include "module/IModule.h"
#include "module/IPlugin.h"
#include "system/ISystem.h"

namespace auth {

class AuthModule : public interfaces::IAuthModule, public vatger::IModule {
   public:
    AuthModule(std::shared_ptr<interfaces::IRestClient> restClient, std::shared_ptr<interfaces::ISystem> system,
               std::string baseUrl = "https://plugin.vatger.de",
               std::chrono::milliseconds pollingInterval = std::chrono::seconds(5));
    ~AuthModule();

    bool isAuthenticated() override;
    std::optional<std::string> getToken() override;
    AuthFlowResult startAuthFlow() override;

    void init(vatger::IPlugin* plugin) override;
    void OnConfigChange(const config::PluginConfig& config) override;
    void handleOnCompileCommand(const std::string& command) override;

   private:
    void validateToken();
    void pollToken(std::stop_token stopToken, PluginTokenStartDTO dto);

    std::shared_ptr<interfaces::IRestClient> m_restClient;
    std::shared_ptr<interfaces::ISystem> m_system;

    std::optional<std::string> m_token;
    std::optional<PluginTokenStartDTO> m_pluginTokenStartDTO;
    std::shared_mutex config_mutex_;
    std::string m_baseUrl;

    std::jthread m_pollingThread;
    std::chrono::milliseconds m_pollingInterval;
    std::condition_variable_any m_cv;
    std::mutex m_cvMutex;

    vatger::IPlugin* m_plugin = nullptr;
};

}  // namespace auth