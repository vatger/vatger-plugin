#include "SilentRequestModule.h"

#include <chrono>
#include <nlohmann/json.hpp>

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
        auto response = rest_client_->get("localhost:8022/api/v1/silent-request/" + icao);

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