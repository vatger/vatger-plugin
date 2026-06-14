#pragma once

#include <sqlite3.h>

#include <filesystem>
#include <format>
#include <string>

#include "LoggerAsyncBase.h"

namespace logging {
class SqliteLogger : public LoggerAsyncBase {
   protected:
    void emitLog(const LoggerAsyncBase::LogMessage& logMsg) override;

   public:
    SqliteLogger();
    explicit SqliteLogger(const std::filesystem::path& dir_path);
    ~SqliteLogger();

   private:
    sqlite3* m_database_;

    void createLogFile(const std::filesystem::path& file);
    static std::string generateLogFileName() {
        return std::format("{:%Y%m%d%H%M%S}.log", std::chrono::utc_clock::now());
    }
};
}  // namespace logging
