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

    std::vector<vatger::IModule *> m_modules;
    m_modules.push_back(dynamic_cast<vatger::IModule *>(m_authService.get()));
    for (const auto &module : m_modules) {
        module->init(this);
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

    std::string preword = parts[1];
    std::transform(preword.begin(), preword.end(), preword.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });

    auto it = m_compileCommands.find(preword);
    if (it != m_compileCommands.end()) {
        // rejoin remaining parts as the command line passed to the module
        std::string remainingCommand;
        for (size_t i = 2; i < parts.size(); ++i) {
            if (i > 2) remainingCommand += ' ';
            remainingCommand += parts[i];
        }
        it->second->handleOnCompileCommand(remainingCommand);
        return true;
    }

    DisplayMessage("Unknown command: " + preword);
    return true;
}

void VatgerPlugin::RegisterModuleOnCompileCommand(const std::string &preword, IModule *module) {
    std::string normalizedPreword = preword;
    std::transform(normalizedPreword.begin(), normalizedPreword.end(), normalizedPreword.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });

    auto [it, inserted] = m_compileCommands.emplace(normalizedPreword, module);
    if (!inserted) {
        m_logger->error("CompileCommand Preword " + normalizedPreword + " already taken");
    }
}

}  // namespace vatger
