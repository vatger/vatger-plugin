#pragma once
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <functional>
#include <memory>
#include <mutex>
#include <optional>
#include <queue>
#include <stop_token>
#include <thread>
#include <unordered_map>
#include <vector>

#include "interfaces/core/IBackGroundExecuter.h"
#include "log/ILogger.h"

class BackgroundExecutor : public IBackgroundExecutor {
   public:
    explicit BackgroundExecutor(std::shared_ptr<logging::ILogger> logger)
        : m_logger(std::move(logger)), m_worker([this](std::stop_token st) { run(st); }) {}

    ~BackgroundExecutor() override {
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            m_stopping = true;
        }
        m_worker.request_stop();
        m_cv.notify_all();
        if (m_worker.joinable()) {
            m_worker.join();
        }
    }

    TaskId post(std::function<void()> task) override { return scheduleAt(Clock::now(), std::nullopt, std::move(task)); }

    TaskId postAfter(std::chrono::milliseconds delay, std::function<void()> task) override {
        return scheduleAt(Clock::now() + delay, std::nullopt, std::move(task));
    }

    TaskId postEvery(std::chrono::milliseconds period, std::function<void()> task,
                     bool runImmediately = false) override {
        const auto first = runImmediately ? Clock::now() : (Clock::now() + period);
        return scheduleAt(first, period, std::move(task));
    }

    bool cancel(TaskId id) override {
        bool cancelled = false;
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            auto it = m_canceledTasks.find(id);
            if (it == m_canceledTasks.end()) return false;
            it->second->store(true, std::memory_order_relaxed);
            m_canceledTasks.erase(it);
            cancelled = true;
        }
        if (cancelled) m_cv.notify_all();
        return true;
    }

   private:
    using Clock = std::chrono::steady_clock;

    struct ScheduledTask {
        TaskId id;
        Clock::time_point next;
        std::optional<std::chrono::milliseconds> period;
        std::function<void()> fn;
        std::shared_ptr<std::atomic_bool> cancelled;
    };

    TaskId scheduleAt(Clock::time_point when, std::optional<std::chrono::milliseconds> period,
                      std::function<void()> task) {
        auto flag = std::make_shared<std::atomic_bool>(false);
        TaskId id = m_nextId.fetch_add(1, std::memory_order_relaxed);

        {
            std::lock_guard<std::mutex> lock(m_mutex);
            if (m_stopping) {
                return 0;
            }

            m_canceledTasks[id] = flag;
            m_tasks.push(ScheduledTask{id, when, period, std::move(task), flag});
        }

        m_cv.notify_all();
        return id;
    }

    void run(std::stop_token st) {
        while (true) {
            ScheduledTask task;

            {
                std::unique_lock<std::mutex> lock(m_mutex);

                while (true) {
                    if ((m_stopping || st.stop_requested())) {
                        return;
                    }

                    if (m_tasks.empty()) {
                        m_cv.wait(lock, [this, &st] { return m_stopping || st.stop_requested() || !m_tasks.empty(); });
                        continue;
                    }

                    const auto now = Clock::now();
                    const auto nextTime = m_tasks.top().next;

                    if (nextTime <= now) {
                        task = m_tasks.top();
                        m_tasks.pop();
                        break;
                    }

                    // wait until next job is due or until a new earlier job arrives/cancels/shuts down
                    m_cv.wait_until(lock, nextTime);
                }
            }

            // skip if job is cancelled
            if (task.cancelled && task.cancelled->load(std::memory_order_relaxed)) {
                continue;
            }

            // execute task
            try {
                task.fn();
            } catch (...) {
                if (m_logger) {
                    m_logger->error("BackgroundExecutor task threw an exception");
                }
            }

            // reschedule if periodic (and not shutting down/cancelled)
            if (!m_stopping && !st.stop_requested() && task.period.has_value()) {
                if (!task.cancelled->load(std::memory_order_relaxed)) {
                    // task.next = Clock::now() + *task.period; // fixed-delay (i.e. every X milliseconds +  runtime)
                    task.next += *task.period;  // fixed-rate (i.e. every X milliseconds without considering runtime)

                    std::lock_guard<std::mutex> lock(m_mutex);
                    if (!m_stopping) {
                        m_tasks.push(std::move(task));
                        m_cv.notify_all();
                    }
                }
            } else {
                std::lock_guard<std::mutex> lock(m_mutex);
                m_canceledTasks.erase(task.id);
            }
        }
    }

    struct EarlierNext {
        bool operator()(const ScheduledTask& a, const ScheduledTask& b) const {
            // priority_queue is max-heap by default, so invert for min-heap
            return a.next > b.next;
        }
    };
    std::priority_queue<ScheduledTask, std::vector<ScheduledTask>, EarlierNext> m_tasks;
    std::unordered_map<TaskId, std::shared_ptr<std::atomic_bool>> m_canceledTasks;

    std::mutex m_mutex;
    std::condition_variable m_cv;
    std::atomic_bool m_stopping{false};

    std::atomic<TaskId> m_nextId{1};

    std::shared_ptr<logging::ILogger> m_logger;
    std::jthread m_worker;
};