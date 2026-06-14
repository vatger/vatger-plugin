
#include "ConsoleLogger.h"

#include <Windows.h>

#include <cstdio>
#include <iostream>
#include <stdexcept>

logging::ConsoleLogger::ConsoleLogger() {
    if (GetConsoleWindow() == NULL) {
        if (!AllocConsole()) {
            DWORD error_code = GetLastError();
            throw std::runtime_error("AllocConsole failed with error code: " + std::to_string(error_code));
        }
        freopen("CONOUT$", "w", stdout);
        freopen("CONOUT$", "w", stderr);
    }

    // enable support for ANSI escape sequences (colors)
    HANDLE h_out = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dw_mode = 0;
    if (GetConsoleMode(h_out, &dw_mode)) {
        dw_mode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
        SetConsoleMode(h_out, dw_mode);
    }
}

inline constexpr std::string_view logging::ConsoleLogger::logLevelToColor(const LogLevel level) {
    switch (level) {
        case LogLevel::Debug:
            return utils::colors::MAGENTA;
        case LogLevel::Info:
            return utils::colors::WHITE;
        case LogLevel::Warning:
            return utils::colors::YELLOW;
        case LogLevel::Error:
            return utils::colors::RED;
        default:
            return utils::colors::RESET;
    }
}

void logging::ConsoleLogger::emitLog(const LoggerAsyncBase::LogMessage& log_msg) {
    std::time_t now_c = std::chrono::system_clock::to_time_t(log_msg.timestamp);
    const auto level_str = logLevelToString(log_msg.level);
    const auto color = logLevelToColor(log_msg.level);

    std::string_view filename = log_msg.location.file_name();
    constexpr std::string_view prefix = "src\\";
    auto pos = filename.find(prefix);
    if (pos != std::string_view::npos) {
        filename.remove_prefix(pos + prefix.size());
    }

    std::cout << color << "[" << std::put_time(std::localtime(&now_c), "%F %T") << "] " << level_str << " (" << filename
              << ":" << log_msg.location.line() << ") - " << log_msg.message << "\033[0m" << std::endl;
}
