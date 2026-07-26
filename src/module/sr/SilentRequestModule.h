#pragma once

#include <list>
#include <map>
#include <memory>
#include <mutex>
#include <nlohmann/json.hpp>
#include <shared_mutex>
#include <string>

#include "api/IRestClient.h"
#include "config/PluginConfig.h"
#include "core/IBackGroundExecuter.h"
#include "module/IModule.h"
#include "module/IPlugin.h"
#include "utils/Date.h"

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
   private:
    vatger::IPlugin* m_plugin = nullptr;

    std::shared_ptr<IBackgroundExecutor> executor_;
    std::shared_ptr<interfaces::IRestClient> rest_client_;

    std::shared_mutex config_mutex_;
    std::string base_url_ = "https://plugin.vatger.de";
    void update();
    std::optional<IBackgroundExecutor::TaskId> task_id_ = std::nullopt;

    std::mutex airports_mutex_;
    std::list<std::string> airports_;
    std::mutex silent_requests_mutex_;
    std::map<std::string, SilentRequestDTO> silent_requests_;

    enum class TagItems : int {
        REQUEST_TYPE = 1000,
        REQUEST_TYPE_DELAY,
    };
    std::vector<vatger::IPlugin::TagItemDefinition> tag_items_ = {
        vatger::IPlugin::TagItemDefinition{static_cast<int>(TagItems::REQUEST_TYPE), "SilentRequest: request type"},
        vatger::IPlugin::TagItemDefinition{static_cast<int>(TagItems::REQUEST_TYPE_DELAY),
                                           "SilentRequest: request type with delay"},
    };

   public:
    SilentRequestModule(std::shared_ptr<IBackgroundExecutor> executer,
                        std::shared_ptr<interfaces::IRestClient> restClient);
    ~SilentRequestModule();

    void init(vatger::IPlugin* plugin) override;
    void OnConfigChange(const config::PluginConfig& config) override;
    void handleOnCompileCommand(const std::string& command) override;

    void OnActiveAirportsChange(const std::list<std::string> icaos) override;

    std::optional<TagRenderData> handleOnGetTagItem(const TagData& data, int item_code) override;
};
}  // namespace silentrequests
