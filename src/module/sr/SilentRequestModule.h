#pragma once

#include <list>
#include <map>
#include <memory>
#include <mutex>
#include <nlohmann/json.hpp>
#include <string>

#include "api/IRestClient.h"
#include "core/IBackGroundExecuter.h"
#include "module/IModule.h"
#include "module/IPlugin.h"
#include "utils/Date.h"

static std::chrono::utc_clock::time_point isoStringToTimestamp(const std::string& timestamp) {
    std::chrono::sys_time<std::chrono::seconds> tp;

    std::istringstream ss(timestamp);
    ss >> std::chrono::parse("%FT%T%Z", tp);

    return std::chrono::utc_clock::from_sys(tp);
}

namespace silentrequests {
enum class SilentRequestType { TAXI, PUSHBACK };

struct SilentRequestDTO {
    std::string callsign;
    std::string departure_icao;
    SilentRequestType type;
    std::chrono::utc_clock::time_point requested_at;
};

inline void from_json(const nlohmann::json& j, SilentRequestDTO& dto) {
    j.at("callsign").get_to(dto.callsign);
    j.at("departure_icao").get_to(dto.departure_icao);

    std::string type;
    j.at("type").get_to(type);
    if (type == "TAXI")
        dto.type = SilentRequestType::TAXI;
    else if (type == "PUSHBACK")
        dto.type = SilentRequestType::PUSHBACK;
    std::string ts;
    j.at("requested_at").get_to(ts);

    dto.requested_at = utils::Date::isoStringToTimestamp(ts);
}

class SilentRequestModule : public vatger::IModule {
   public:
   private:
    vatger::IPlugin* m_plugin = nullptr;

    std::shared_ptr<IBackgroundExecutor> executor_;
    std::shared_ptr<interfaces::IRestClient> rest_client_;

    void update();
    std::optional<IBackgroundExecutor::TaskId> task_id_ = std::nullopt;

    std::mutex airports_mutex_;
    std::list<std::string> airports_;
    std::mutex silent_requests_mutex_;
    std::map<std::string, SilentRequestDTO> silent_requests_;

   public:
    SilentRequestModule(std::shared_ptr<IBackgroundExecutor> executer,
                        std::shared_ptr<interfaces::IRestClient> restClient);
    ~SilentRequestModule();

    void init(vatger::IPlugin* plugin) override;
    void handleOnCompileCommand(const std::string& command) override;

    void OnActiveAirportsChange(const std::list<std::string> icaos) override;
};
}  // namespace silentrequests
