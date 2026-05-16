#include "plugin.h"

#include "Version.h"
#include "api/CurlRestClient.h"
#include "auth/AuthService.h"
#include "log/ConsoleLogger.h"
#include "log/SqlLiteLogger.h"
#include "system/WindowsSystem.h"
#include "utils/File.h"

namespace vatger {
VatgerPlugin::VatgerPlugin()
    : CPlugIn(EuroScopePlugIn::COMPATIBILITY_CODE, PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR, PLUGIN_LICENSE) {
    m_logger = std::make_shared<logging::ConsoleLogger>();

    DisplayMessage("Version " + std::string(PLUGIN_VERSION) + " loaded", "Initialisation");
    m_logger->info("Version " + std::string(PLUGIN_VERSION) + " loaded");

    auto system = std::make_shared<WindowsSystem>();
    auto restClient = std::make_unique<api::CurlRestClient>();
    m_authService = std::make_unique<auth::AuthService>(std::move(restClient), system);

    const auto isAuthenticated = m_authService->isAuthenticated();
    if (isAuthenticated) {
        DisplayMessage("Plugin is authenticated", "Auth");
    } else {
        DisplayMessage("Plugin is not authenticated", "Auth");
    }
}
VatgerPlugin::~VatgerPlugin() {}

void VatgerPlugin::DisplayMessage(const std::string &message, const std::string &sender) {
    DisplayUserMessage(PLUGIN_NAME, sender.c_str(), message.c_str(), true, false, false, false, false);
}

bool VatgerPlugin::OnCompileCommand(const char *sCommandLine) {
    const std::string_view command(sCommandLine);

    if (!command.starts_with(".VATGER") && !command.starts_with(".vatger")) {
        return false;
    }

    std::vector<std::string> parts;
    std::string part;
    std::istringstream stream{std::string(command)};
    while (stream >> part) {
        parts.push_back(part);
    }

    if (parts.size() < 2) {
        return true;
    }

    if (parts[1] == "auth" && !m_authService->isAuthenticated()) {
        auto result = m_authService->startAuthFlow();
        if (result.status == auth::AuthFlowStatus::Success) {
            DisplayMessage("Starting Auth Flow, opening URL in browser. URL: " + result.redirectUrl, "Auth");
        } else {
            DisplayMessage("ERROR: Starting Auth Flow. Error message: " + result.errorMessage, "Auth");
        }
        return true;
    }

    return true;
}

}  // namespace vatger