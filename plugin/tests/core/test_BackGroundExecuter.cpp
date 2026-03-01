#include <gtest/gtest.h>

#include <future>
#include <memory>

#include "core/BackGroundExecuter.h"
#include "tests/mocks/MockLogger.h"

TEST(BackgroundExecutorTests, PostedTaskRuns) {
    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::promise<void> done;
    auto future = done.get_future();

    executor.post([&done] { done.set_value(); });

    EXPECT_EQ(future.wait_for(std::chrono::seconds(1)), std::future_status::ready);
}

TEST(BackgroundExecutorTests, PostedTaskChangesState) {
    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::promise<void> done;
    auto future = done.get_future();

    int value = 0;
    std::mutex mutex;

    executor.post([&] {
        {
            std::lock_guard<std::mutex> lock(mutex);
            value = 42;
        }
        done.set_value();
    });

    ASSERT_EQ(future.wait_for(std::chrono::seconds(1)), std::future_status::ready);

    std::lock_guard<std::mutex> lock(mutex);
    EXPECT_EQ(value, 42);
}

TEST(BackgroundExecutorTests, TasksRunInPostedOrder) {
    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::mutex mutex;
    std::vector<int> results;

    std::promise<void> done;
    auto future = done.get_future();

    executor.post([&] {
        std::lock_guard<std::mutex> lock(mutex);
        results.push_back(1);
    });

    executor.post([&] {
        std::lock_guard<std::mutex> lock(mutex);
        results.push_back(2);
    });

    executor.post([&] {
        {
            std::lock_guard<std::mutex> lock(mutex);
            results.push_back(3);
        }
        done.set_value();
    });

    ASSERT_EQ(future.wait_for(std::chrono::seconds(1)), std::future_status::ready);

    std::lock_guard<std::mutex> lock(mutex);
    EXPECT_EQ(results.size(), 3u);
    EXPECT_EQ(results[0], 1);
    EXPECT_EQ(results[1], 2);
    EXPECT_EQ(results[2], 3);
}