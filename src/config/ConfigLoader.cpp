#include "ConfigLoader.h"

#include <windef.h>
#include <wingdi.h>

#include <array>
#include <fstream>
#include <limits>
#include <vector>

#include "config/PluginConfig.h"
#include "utils/String.h"

using namespace config;

ConfigLoader::ConfigLoader() : error_line_(std::numeric_limits<std::uint32_t>::max()), error_message_() {}

bool ConfigLoader::errorFound() const { return std::numeric_limits<std::uint32_t>::max() != this->error_line_; }

std::uint32_t ConfigLoader::errorLine() const { return this->error_line_; }

const std::string &ConfigLoader::errorMessage() const { return this->error_message_; }

bool ConfigLoader::parseColor(const std::string &block, COLORREF &color, std::uint32_t line) {
    std::vector<std::string> colorValues = utils::String::SplitString(block, ",");

    if (colorValues.size() != 3) {
        this->error_line_ = line;
        this->error_message_ = "Invalid color config";
        return false;
    }

    std::array<std::uint8_t, 3> colors{};
    for (std::size_t i = 0; i < colors.size(); ++i) {
        colors[i] = static_cast<std::uint8_t>(std::atoi(colorValues[i].c_str()));
    }

    color = RGB(colors[0], colors[1], colors[2]);

    return true;
}

bool ConfigLoader::parse(const std::string &filename, PluginConfig &config) {
    std::ifstream stream(filename);
    if (!stream.is_open()) {
        this->error_line_ = 0;
        this->error_message_ = "Unable to open the configuration file";
        return false;
    }

    std::string line;
    std::uint32_t lineNumber = 0;

    while (std::getline(stream, line)) {
        lineNumber += 1;

        const std::string trimmed = utils::String::Trim(line);

        /* skip empty lines and comments */
        if (trimmed.empty() || trimmed.front() == '#') continue;

        const std::vector<std::string> values = utils::String::SplitString(trimmed, "=");
        if (values.size() != 2) {
            this->error_line_ = lineNumber;
            this->error_message_ = "Invalid configuration entry";
            return false;
        }

        const std::string key = utils::String::Trim(values[0]);
        const std::string value = utils::String::Trim(values[1]);

        if (value.empty()) {
            this->error_line_ = lineNumber;
            this->error_message_ = "Invalid entry";
            return false;
        }

        if (key == "SERVER_url") {
            config.server_url = value;
        } else {
            config.extra[key] = value;
        }
    }

    config.valid = true;
    return true;
}