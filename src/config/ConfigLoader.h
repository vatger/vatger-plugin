#pragma once

#include <Windows.h>

#include <cstdint>
#include <string>

#include "config/PluginConfig.h"

namespace config {
/// @brief parses the config file .txt to type PluginConfig. Also provides information about errors.
class ConfigLoader {
   private:
    std::uint32_t error_line_;  /* Defines the line number the error has occurred */
    std::string error_message_; /* The error message to print */
    bool parseColor(const std::string &block, COLORREF &color, std::uint32_t line);

   public:
    ConfigLoader();

    bool errorFound() const;
    std::uint32_t errorLine() const;
    const std::string &errorMessage() const;

    bool parse(const std::string &filename, PluginConfig &config);
};
}  // namespace config