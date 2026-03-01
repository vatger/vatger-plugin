#pragma once
#include <condition_variable>
#include <functional>
#include <mutex>
#include <queue>
#include <stop_token>
#include <thread>

#include "interfaces/core/IBackGroundExecuter.h"
#include "log/ILogger.h"

class BackgroundExecutor : public IBackgroundExecutor {
   public:
    BackgroundExecutor(std::shared_ptr<logging::ILogger> logger)
        : m_logger(std::move(logger)), m_worker([this](std::stop_token st) { run(st); }) {}

    ~BackgroundExecutor() override {
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            m_stopping = true;
        }
        m_cv.notify_all();
    }

    void post(std::function<void()> task) override {
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            m_tasks.push(std::move(task));
        }
        m_cv.notify_one();
    }

   private:
    void run(std::stop_token st) {
        while (!st.stop_requested()) {
            std::function<void()> task;

            {
                std::unique_lock<std::mutex> lock(m_mutex);
                m_cv.wait(lock, [this, &st] { return m_stopping || !m_tasks.empty() || st.stop_requested(); });

                if ((m_stopping || st.stop_requested()) && m_tasks.empty()) {
                    return;
                }

                task = std::move(m_tasks.front());
                m_tasks.pop();
            }

            try {
                task();
            } catch (...) {
                m_logger->error("BackgroundExecutor task threw an exception");
            }
        }
    }

    std::queue<std::function<void()>> m_tasks;
    std::mutex m_mutex;
    std::condition_variable m_cv;
    bool m_stopping = false;
    std::jthread m_worker;
    std::shared_ptr<logging::ILogger> m_logger;
};