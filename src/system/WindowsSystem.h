#pragma once
#include <Windows.h>
#include <shellapi.h>

#include <optional>
#include <string>

#include "ISystem.h"

class WindowsSystem : public interfaces::ISystem {
   public:
    bool openUrl(const std::string& url) override;
    bool saveDeviceToken(const std::string& token) override;
    std::optional<std::string> getDeviceToken() override;
};
