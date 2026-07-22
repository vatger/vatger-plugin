#include "WindowsSystem.h"

#include <Windows.h>
#include <shellapi.h>

bool WindowsSystem::openUrl(const std::string& url) {
    HINSTANCE result = ShellExecuteA(nullptr, "open", url.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
    return reinterpret_cast<intptr_t>(result) > 32;  // >32 means success
}

bool WindowsSystem::saveDeviceToken(const std::string& token) {
    HKEY hKey;
    LONG result = RegCreateKeyExA(HKEY_CURRENT_USER, "SOFTWARE\\VATGER_PLUGIN", 0, nullptr, REG_OPTION_NON_VOLATILE,
                                  KEY_SET_VALUE, nullptr, &hKey, nullptr);
    if (result != ERROR_SUCCESS) return false;

    result = RegSetValueExA(hKey, "DeviceToken", 0, REG_SZ, reinterpret_cast<const BYTE*>(token.c_str()),
                            static_cast<DWORD>(token.size() + 1));
    RegCloseKey(hKey);
    return result == ERROR_SUCCESS;
}

std::optional<std::string> WindowsSystem::getDeviceToken() {
    HKEY hKey;
    LONG result = RegOpenKeyExA(HKEY_CURRENT_USER, "SOFTWARE\\VATGER_PLUGIN", 0, KEY_QUERY_VALUE, &hKey);
    if (result != ERROR_SUCCESS) return std::nullopt;

    char buffer[512];
    DWORD bufferSize = sizeof(buffer);
    DWORD type = REG_SZ;
    result = RegQueryValueExA(hKey, "DeviceToken", nullptr, &type, reinterpret_cast<BYTE*>(buffer), &bufferSize);
    RegCloseKey(hKey);

    if (result != ERROR_SUCCESS) return std::nullopt;
    return std::string(buffer);
}
