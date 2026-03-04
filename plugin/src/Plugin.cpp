#include "plugin.h"

#include "Version.h"
#include "core/BackGroundExecuter.h"
#include "log/ConsoleLogger.h"
#include "log/SqlLiteLogger.h"
#include "modules/silentPushback/SilentPushbackModule.h"
#include "utils/File.h"

namespace vatger {
VatgerPlugin::VatgerPlugin()
    : CPlugIn(EuroScopePlugIn::COMPATIBILITY_CODE, PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR, PLUGIN_LICENSE) {
    m_logger = std::make_shared<logging::ConsoleLogger>();
    m_executer = std::make_shared<BackgroundExecutor>(m_logger);

    m_pushback_module = std::make_shared<modules::SilentPushbackModule>(m_logger, m_executer);

    DisplayMessage("Version " + std::string(PLUGIN_VERSION) + " loaded", "Initialisation");
    m_logger->info("Version " + std::string(PLUGIN_VERSION) + " loaded");

    RegisterTagItemType("SilentRequest", TagItemTypes::SilentRequest);
    RegisterTagItemType("SilentRequest (Pushback)", TagItemTypes::SilentRequestPushback);
    RegisterTagItemType("SilentRequst (Taxi)", TagItemTypes::SilentRequestTaxi);
}

VatgerPlugin::~VatgerPlugin() {}

void VatgerPlugin::DisplayMessage(const std::string& message, const std::string& sender) {
    DisplayUserMessage(PLUGIN_NAME, sender.c_str(), message.c_str(), true, false, false, false, false);
}

void VatgerPlugin::OnGetTagItem(EuroScopePlugIn::CFlightPlan FlightPlan, EuroScopePlugIn::CRadarTarget RadarTarget,
                                int ItemCode, int TagData, char sItemString[16], int* pColorCode, COLORREF* pRGB,
                                double* pFontSize) {
    (void)RadarTarget;
    (void)TagData;
    (void)pFontSize;

    if (FlightPlan.IsValid() == false || FlightPlan.GetSimulated() == true) {
        return;
    }
    const std::string callsign = FlightPlan.GetCallsign();
    *pColorCode = EuroScopePlugIn::TAG_COLOR_RGB_DEFINED;

    std::stringstream outputText;

    switch (static_cast<TagItemTypes>(ItemCode)) {
        case TagItemTypes::SilentRequest:
            if (this->m_pushback_module->pilotHasPushbackRequest(callsign)) {
                outputText << "REQ";
                *pRGB = RGB(0, 255, 0);
            } else if (this->m_pushback_module->pilotHasTaxiRequest(callsign)) {
                outputText << "REQ";
                *pRGB = RGB(255, 255, 0);
            }
            break;
        case TagItemTypes::SilentRequestPushback:
            outputText << (this->m_pushback_module->pilotHasPushbackRequest(callsign) ? "REQ" : "");
            *pRGB = RGB(0, 255, 0);
            break;
        case TagItemTypes::SilentRequestTaxi:
            outputText << (this->m_pushback_module->pilotHasTaxiRequest(callsign) ? "REQ" : "");
            *pRGB = RGB(255, 255, 0);
            break;
        default:
            break;
    }

    strcpy_s(sItemString, 16, outputText.str().c_str());
}
}  // namespace vatger