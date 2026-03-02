#pragma once

#include <chrono>
#include <cstdint>
#include <functional>

struct IBackgroundExecutor {
    using TaskId = std::uint64_t;

    virtual ~IBackgroundExecutor() = default;

    /// @brief Runs task async & asap
    virtual TaskId post(std::function<void()> task) = 0;

    /// @brief run once after delay
    virtual TaskId postAfter(std::chrono::milliseconds delay, std::function<void()> task) = 0;

    /// @brief runs a task periodically.
    /// @param runImmediately If true runs job once ASAP then periodically
    virtual TaskId postEvery(std::chrono::milliseconds period, std::function<void()> task,
                             bool runImmediately = false) = 0;

    /// @brief Cancels a scheduled / periodic task
    virtual bool cancel(TaskId id) = 0;
};