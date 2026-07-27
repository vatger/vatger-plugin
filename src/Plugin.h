#pragma once

#pragma warning(push, 0)
#include "EuroScopePlugIn.h"
#pragma warning(pop)

#include <memory>
#include <string>

#include "auth/IAuthModule.h"
#include "log/ILogger.h"
#include "module/IModule.h"
#include "module/IPlugin.h"
#include "module/sr/SilentRequestModule.h"

namespace vatger {
class VatgerPlugin : public EuroScopePlugIn::CPlugIn, public IPlugin {
   private:
    std::shared_ptr<logging::ILogger> m_logger;

   public:
    VatgerPlugin();
    ~VatgerPlugin();

    void DisplayMessage(const std::string &message, const std::string &sender = "VatgerPlugin");

    bool OnCompileCommand(const char *sCommandLine) override;
    void OnAirportRunwayActivityChanged() override;
    void OnGetTagItem(EuroScopePlugIn::CFlightPlan FlightPlan, EuroScopePlugIn::CRadarTarget RadarTarget, int ItemCode,
                      int TagData, char sItemString[16], int *pColorCode, COLORREF *pRGB, double *pFontSize) override;

   private:
    std::unique_ptr<interfaces::IAuthModule> m_authService;
    std::unique_ptr<silentrequests::SilentRequestModule> sr_module_;

    std::vector<vatger::IModule *> m_modules;

    void RegisterModuleOnCompileCommand(const std::string &preword, IModule *module) override;
    std::unordered_map<std::string, IModule *> m_compileCommands;
    void RegisterModuleOnGetTagItem(TagItemDefinition item, IModule *module) override;
    std::unordered_map<int, IModule *> tagItemToModule_;
};
}  // namespace vatger
