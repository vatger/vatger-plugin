#include "SilentRequestModule.h"

#include <chrono>
#include <nlohmann/json.hpp>

using namespace vatger;
using namespace silentrequests;

SilentRequestModule::SilentRequestModule(std::shared_ptr<IBackgroundExecutor> executor,
                                         std::shared_ptr<interfaces::IRestClient> rest_client)
    : executor_(executor), rest_client_(rest_client) {}

SilentRequestModule::~SilentRequestModule() {
    if (task_id_.has_value()) {
        executor_->cancel(task_id_.value());
    }
}

void SilentRequestModule::init(vatger::IPlugin* plugin) {
    m_plugin = plugin;
    task_id_ = executor_->postEvery(std::chrono::seconds(5), std::bind(&SilentRequestModule::update, this));

    for (const auto& tag_item : tag_items_) {
        m_plugin->RegisterModuleOnGetTagItem(tag_item, this);
    }
}

void SilentRequestModule::OnConfigChange(const config::PluginConfig& config) {
    std::unique_lock config_lock(config_mutex_);
    base_url_ = config.server_url;

    color_pushback_request_ =
        IModule::RGB{config.pushback_request_color.r, config.pushback_request_color.g, config.pushback_request_color.b};
    color_taxi_request_ =
        IModule::RGB{config.taxi_request_color.r, config.taxi_request_color.g, config.taxi_request_color.b};
}

void SilentRequestModule::handleOnCompileCommand(const std::string& command) {}

void SilentRequestModule::OnActiveAirportsChange(const std::list<std::string> icaos) {
    std::lock_guard lock(airports_mutex_);
    airports_ = icaos;
}

void SilentRequestModule::update() {
    m_plugin->DisplayMessage("Running update", "SR");
    std::lock_guard airport_lock(airports_mutex_);
    std::map<std::string, SilentRequestDTO> silent_requests;
    for (auto& icao : airports_) {
        std::shared_lock config_lock(config_mutex_);
        auto response = rest_client_->get(base_url_ + "/api/v1/silent-request/" + icao);

        if (response.statusCode != 200) {
            continue;
        }

        auto response_dtos = nlohmann::json::parse(response.body).get<std::vector<SilentRequestDTO>>();

        for (auto& response_dto : response_dtos) {
            silent_requests.emplace(response_dto.callsign, std::move(response_dto));
        }
    }

    std::lock_guard request_lock(silent_requests_mutex_);
    silent_requests_ = silent_requests;
}

std::optional<IModule::TagRenderData> SilentRequestModule::handleOnGetTagItem(const IModule::TagData& data,
                                                                              int item_code) {
    (void)item_code;

    std::lock_guard request_lock(silent_requests_mutex_);
    auto it = silent_requests_.find(data.callsign);
    if (it == silent_requests_.end()) {
        return std::nullopt;  // no request to show
    }

    const auto request = it->second;

    std::shared_lock config_lock(config_mutex_);  // lock the config, since we are reading colors from it
    IModule::TagRenderData tag_render_data;
    switch (static_cast<TagItems>(item_code)) {
        case TagItems::REQUEST_TYPE: {
            tag_render_data.item_string = request.type == SilentRequestType::PUSHBACK ? "TX" : "PB";
            tag_render_data.text_color =
                request.type == SilentRequestType::PUSHBACK ? color_pushback_request_ : color_taxi_request_;

            break;
        }
        case TagItems::REQUEST_TYPE_DELAY: {
            tag_render_data.item_string = request.type == SilentRequestType::PUSHBACK ? "TX" : "PB";
            const auto now = std::chrono::utc_clock::now();
            const auto diff = std::chrono::duration_cast<std::chrono::minutes>(now - request.requested_at);
            tag_render_data.item_string += " " + std::to_string(diff.count());
            tag_render_data.text_color =
                request.type == SilentRequestType::PUSHBACK ? color_pushback_request_ : color_taxi_request_;

            break;
        }
        default:
            break;
    };

    return tag_render_data;
}