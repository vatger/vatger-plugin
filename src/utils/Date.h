#pragma once

#include <chrono>
#include <string>

#pragma warning(push, 0)
#include "EuroScopePlugIn.h"
#pragma warning(pop)

namespace utils {

class Date {
   public:
    Date() = delete;
    Date(const Date &) = delete;
    Date(Date &&) = delete;
    Date &operator=(const Date &) = delete;
    Date &operator=(Date &&) = delete;

    /// @brief Converts std::chrono::utc_clock::time_point to an ISO-formatted string.
    /// @param timepoint std::chrono::utc_clock::time_point to be converted.
    /// @return ISO-formatted string representing the converted timestamp.
    static std::string timestampToIsoString(const std::chrono::utc_clock::time_point &timepoint) {
        if (timepoint.time_since_epoch().count() >= 0) {
            std::stringstream stream;
            stream << std::format("{0:%FT%T}", timepoint);
            auto timestamp = stream.str();
            timestamp = timestamp.substr(0, timestamp.length() - 4) + "Z";
            return timestamp;
        } else {
            return "1969-12-31T23:59:59.999Z";
        }
    }

    /// @brief Converts an ISO-formatted string to std::chrono::utc_clock::time_point.
    /// @param timestamp ISO-formatted string representing the timestamp.
    /// @return std::chrono::utc_clock::time_point representing the converted timestamp.
    static std::chrono::utc_clock::time_point isoStringToTimestamp(const std::string &timestamp) {
        std::chrono::utc_clock::time_point retval;
        std::stringstream stream;

        stream << timestamp.substr(0, timestamp.length() - 1);
        std::chrono::from_stream(stream, "%FT%T", retval);

        return retval;
    }
};
}  // namespace utils