#pragma once

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <queue>
#include <source_location>
#include <string>
#include <thread>
#include <utility>

#include "ILogger.h"

namespace logging {
class LoggerAsyncBase : public ILogger {
   protected:
    struct LogMessage {
        LogLevel level;
        std::string message;
        std::source_location location;
        std::chrono::system_clock::time_point timestamp;
    };

    virtual void emitLog(const LogMessage& logMsg) = 0;

    std::queue<LogMessage> m_queue_;
    std::mutex m_mutex_;
    std::condition_variable m_cv_;
    std::thread m_worker_;
    std::atomic<bool> m_running_;

    std::condition_variable m_flush_cv_;

    void processLogs() {
        while (m_running_ || !m_queue_.empty()) {
            std::unique_lock<std::mutex> lock(m_mutex_);
            m_cv_.wait(lock, [this]() { return !m_queue_.empty() || !m_running_; });

            while (!m_queue_.empty()) {
                auto log_msg = std::move(m_queue_.front());
                m_queue_.pop();
                lock.unlock();

                this->emitLog(log_msg);

                lock.lock();
            }

            m_flush_cv_.notify_all();
        }
    }

   public:
    LoggerAsyncBase() : m_running_(true), m_worker_(&LoggerAsyncBase::processLogs, this) {}
    virtual ~LoggerAsyncBase() {
        {
            std::unique_lock<std::mutex> lock(m_mutex_);
            m_running_ = false;
            m_cv_.notify_all();  // notify worker thread to exit
        }
        {
            std::unique_lock<std::mutex> lock(m_mutex_);
            m_flush_cv_.wait(lock, [this]() { return m_queue_.empty(); });
        }

        if (m_worker_.joinable()) {
            m_worker_.join();
        }
    }

    void LoggerAsyncBase::log(const LogLevel level, const std::string& message,
                              const std::source_location location = std::source_location::current()) {
        LogMessage logMsg{level, message, location, std::chrono::system_clock::now()};

        {
            std::lock_guard<std::mutex> lock(m_mutex_);
            m_queue_.push(std::move(logMsg));
        }
        m_cv_.notify_one();
    }
};
}  // namespace logging
