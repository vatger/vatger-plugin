#pragma once

#include <string>

enum class RequestType { PUSHBACK, TAXI };

struct SilentRequest {
    std::string callsign;
    RequestType request_type;
    std::string icao;
};