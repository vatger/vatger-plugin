#pragma once

#include <json/json.h>

#include <memory>
#include <vector>

#include "api/CurlRestClient.h"
#include "api/IRestclient.h"
#include "interfaces/services/ISilentRequestService.h"
#include "log/ILogger.h"
#include "types/SilentRequest.h"

class SilentRequestService : public ISilentRequestService {
   private:
    std::shared_ptr<logging::ILogger> m_logger;
    std::shared_ptr<interfaces::IRestClient> rest;

   public:
    SilentRequestService();
    ~SilentRequestService();

    std::vector<SilentRequest> getSilentRequests() override;
};

SilentRequestService::SilentRequestService() {
    this->rest = std::make_shared<api::CurlRestClient>(std::make_shared<logging::ConsoleLogger>());
}

SilentRequestService::~SilentRequestService() {}

std::vector<SilentRequest> SilentRequestService::getSilentRequests() {
    const auto response = this->rest->get("https://plugin.vatsim-germany.org/api/v1/request");

    const auto body = response.body;

    Json::CharReaderBuilder builder;
    Json::Value root;
    std::string errs;
    {
        std::unique_ptr<Json::CharReader> reader(builder.newCharReader());
        const char* begin = body.data();
        const char* end = begin + body.size();

        if (!reader->parse(begin, end, &root, &errs)) {
            throw std::runtime_error("Failed to parse JSON response: " + errs);
        }
    }

    if (root.isNull()) {
        return {};
    }

    if (!root.isArray()) {
        throw std::runtime_error("No array");
    }

    std::vector<SilentRequest> requests;
    for (const auto& item : root) {
        if (!item.isObject()) {
            continue;
        }

        if (!item.isMember("request_type") || !item.isMember("callsign") || !item.isMember("airport_icao")) {
            continue;
        }

        if (!item["request_type"].isString() || !item["callsign"].isString() || !item["airport_icao"].isString()) {
            continue;
        }

        const std::string requestType = item["request_type"].asString();

        if (requestType != "PUSHBACK" && requestType != "TAXI") {
            continue;
        }

        SilentRequest sr;
        sr.request_type = (requestType == "PUSHBACK") ? RequestType::PUSHBACK : RequestType::TAXI;
        sr.callsign = item["callsign"].asString();
        sr.icao = item["airport_icao"].asString();

        requests.push_back(std::move(sr));
    }

    return requests;
}
