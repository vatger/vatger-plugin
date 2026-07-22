#pragma once

#include <string>
#include <unordered_map>

namespace config {
struct PluginConfig {
    bool valid = true;
    std::string server_url = "https://plugin.vatger.de";
    std::unordered_map<std::string, std::string> extra;
};
}  // namespace config