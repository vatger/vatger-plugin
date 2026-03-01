#pragma once
#include <functional>

struct IBackgroundExecutor {
    virtual ~IBackgroundExecutor() = default;
    virtual void post(std::function<void()> task) = 0;
};