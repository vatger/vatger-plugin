#include "SilentPushbackModule.h"

#include <chrono>

#include "services/SilentRequestService.h"

using namespace modules;
using namespace std::chrono_literals;

SilentPushbackModule::SilentPushbackModule(std::shared_ptr<logging::ILogger> logger,
                                           std::shared_ptr<IBackgroundExecutor> executer)
    : m_logger(logger), m_executer(executer) {
    if (m_executer) {
        m_executer->postEvery(2s, [this]() { this->updateRequests(); });
    }

    m_service = std::make_shared<SilentRequestService>();
}

SilentPushbackModule::~SilentPushbackModule() {}

bool SilentPushbackModule::pilotHasPushbackRequest(const std::string& callsign) {
    if (this->pilotHasAnyRequest(callsign) == false) {
        return false;
    }

    const auto request = m_requests[callsign];

    if (request.request_type == RequestType::PUSHBACK) {
        return true;
    }

    return false;
}

bool SilentPushbackModule::pilotHasTaxiRequest(const std::string& callsign) {
    if (this->pilotHasAnyRequest(callsign) == false) {
        return false;
    }

    const auto request = m_requests[callsign];

    if (request.request_type == RequestType::TAXI) {
        return true;
    }

    return false;
}

void SilentPushbackModule::updateRequests() {
    const auto requests = this->m_service->getSilentRequests();

    std::map<std::string, SilentRequest> newRequests;
    for (const auto& request : requests) {
        newRequests[request.callsign] = request;
    }

    std::lock_guard guard(m_requestLock);
    m_requests = std::move(newRequests);
}

bool SilentPushbackModule::pilotHasAnyRequest(const std::string& callsign) {
    auto it = m_requests.find(callsign);
    if (it == m_requests.end()) return false;
    return true;
}
