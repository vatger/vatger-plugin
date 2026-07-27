#pragma once

#include <string>
#include <unordered_map>

namespace config {
struct Color {
    uint8_t r, g, b;
};

struct PluginConfig {
    bool valid = true;
    std::string server_url = "https://plugin.vatger.de";
    std::unordered_map<std::string, std::string> extra;

    Color pushback_request_color = {245, 239, 13};
    Color taxi_request_color = {0, 128, 0};
};
}  // namespace config