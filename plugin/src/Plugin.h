#pragma once

#pragma warning(push, 0)
#include "EuroScopePlugIn.h"
#pragma warning(pop)

#include <memory>
#include <string>

#include "interfaces/core/IBackGroundExecuter.h"
#include "interfaces/modules/ISilentPushbackModule.h"
#include "log/ILogger.h"

namespace vatger {
class VatgerPlugin : public EuroScopePlugIn::CPlugIn {
   private:
    std::shared_ptr<logging::ILogger> m_logger;
    std::shared_ptr<IBackgroundExecutor> m_executer;

    enum TagItemTypes { SilentRequest, SilentRequestPushback, SilentRequestTaxi };

    std::shared_ptr<modules::ISilentPushbackModule> m_pushback_module;

   public:
    VatgerPlugin();
    ~VatgerPlugin();

    void DisplayMessage(const std::string &message, const std::string &sender = "VatgerPlugin");

    // EuroScope events:
    void OnGetTagItem(EuroScopePlugIn::CFlightPlan FlightPlan, EuroScopePlugIn::CRadarTarget RadarTarget, int ItemCode,
                      int TagData, char sItemString[16], int *pColorCode, COLORREF *pRGB, double *pFontSize) override;
};
}  // namespace vatger
