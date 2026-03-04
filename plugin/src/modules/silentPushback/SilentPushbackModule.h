#pragma once

#include <map>
#include <memory>
#include <mutex>
#include <string>

#include "interfaces/core/IBackGroundExecuter.h"
#include "interfaces/modules/ISilentPushbackModule.h"
#include "interfaces/services/ISilentRequestService.h"
#include "log/ILogger.h"
#include "types/SilentRequest.h"

namespace modules {
class SilentPushbackModule : public modules::ISilentPushbackModule {
   public:
    SilentPushbackModule(std::shared_ptr<logging::ILogger> logger, std::shared_ptr<IBackgroundExecutor> executer);
    ~SilentPushbackModule();

    bool pilotHasPushbackRequest(const std::string& callsign) override;
    bool pilotHasTaxiRequest(const std::string& callsign) override;

   private:
    std::mutex m_requestLock;
    std::map<std::string, SilentRequest> m_requests;
    void updateRequests();
    bool pilotHasAnyRequest(const std::string& callsign);

    std::shared_ptr<logging::ILogger> m_logger;
    std::shared_ptr<IBackgroundExecutor> m_executer;
    std::shared_ptr<ISilentRequestService> m_service;
};
}  // namespace modules
