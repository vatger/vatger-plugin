#include "SqliteLogger.h"

#include <string>

static const char kLoggingTable[] =
    "CREATE TABLE messages("
    "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "location TEXT,"
    "level INT,"
    "message TEXT"
    ");";
static const char kInsertMessage[] = "INSERT INTO messages VALUES (CURRENT_TIMESTAMP, @1, @2, @3)";

logging::SqliteLogger::SqliteLogger() { this->createLogFile(generateLogFileName()); }

logging::SqliteLogger::SqliteLogger(const std::filesystem::path& dir_path) {
    std::filesystem::path full_path = dir_path / generateLogFileName();
    this->createLogFile(full_path);
}

logging::SqliteLogger::~SqliteLogger() {
    if (nullptr != this->m_database_) sqlite3_close_v2(this->m_database_);
}

void logging::SqliteLogger::emitLog(const LoggerAsyncBase::LogMessage& log_msg) {
    sqlite3_stmt* stmt = nullptr;

    if (sqlite3_prepare_v2(this->m_database_, kInsertMessage, -1, &stmt, nullptr) != SQLITE_OK) {
        return;
    }

    std::string sender = std::filesystem::path(log_msg.location.file_name()).filename().string();

    constexpr std::string_view prefix = "src\\";
    auto pos = sender.find(prefix);
    if (pos != std::string::npos) {
        sender = sender.substr(pos + prefix.size());
    }

    sender += ":" + std::to_string(log_msg.location.line());

    sqlite3_bind_text(stmt, 1, sender.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 2, static_cast<int>(log_msg.level));
    sqlite3_bind_text(stmt, 3, log_msg.message.c_str(), -1, SQLITE_TRANSIENT);

    if (sqlite3_step(stmt) != SQLITE_DONE) {
        return;
    }

    sqlite3_clear_bindings(stmt);
    sqlite3_reset(stmt);
    sqlite3_finalize(stmt);
}

void logging::SqliteLogger::createLogFile(const std::filesystem::path& file) {
    sqlite3_open(file.string().c_str(), &this->m_database_);
    sqlite3_exec(this->m_database_, kLoggingTable, nullptr, nullptr, nullptr);
    sqlite3_exec(this->m_database_, "PRAGMA journal_mode = MEMORY", nullptr, nullptr, nullptr);
}
