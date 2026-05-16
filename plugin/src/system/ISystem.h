#pragma once
#include <optional>
#include <string>

namespace interfaces {

/// @brief abstracts needed functions from the underlying OS
class ISystem {
   public:
    virtual ~ISystem() = default;
    virtual bool openUrl(const std::string& url) = 0;
    virtual bool saveDeviceToken(const std::string& token) = 0;
    virtual std::optional<std::string> getDeviceToken() = 0;
};

}  // namespace interfaces