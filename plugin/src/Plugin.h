#pragma once

#pragma warning(push, 0)
#include "EuroScopePlugIn.h"
#pragma warning(pop)

#include <memory>
#include <string>

#include "auth/IAuthService.h"
#include "log/ILogger.h"
#include "module/IModule.h"
#include "module/IPlugin.h"

namespace vatger {
class VatgerPlugin : public EuroScopePlugIn::CPlugIn, public IPlugin {
   private:
    std::shared_ptr<logging::ILogger> m_logger;

   public:
    VatgerPlugin();
    ~VatgerPlugin();

    void DisplayMessage(const std::string &message, const std::string &sender = "VatgerPlugin");

    bool OnCompileCommand(const char *sCommandLine) override;

   private:
    std::unique_ptr<interfaces::IAuthService> m_authService;

    void RegisterModuleOnCompileCommand(const std::string &preword, IModule *module) override;
    std::unordered_map<std::string, IModule *> m_compileCommands;
};
}  // namespace vatger
