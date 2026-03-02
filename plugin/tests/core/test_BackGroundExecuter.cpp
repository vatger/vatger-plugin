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

TEST(BackgroundExecutorTests, ExceptionInTaskIsCaughtAndNextTaskStillRuns) {
    auto logger = std::make_shared<mocks::MockLogger>();

    BackgroundExecutor executor(logger);

    std::promise<void> done;
    auto future = done.get_future();

    executor.post([] { throw std::runtime_error("Error"); });
    executor.post([&done] { done.set_value(); });

    EXPECT_EQ(future.wait_for(std::chrono::seconds(1)), std::future_status::ready);
}

TEST(BackgroundExecutorTests, PostAfterDoesNotRunImmediately) {
    using namespace std::chrono_literals;

    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::promise<void> done;
    auto future = done.get_future();

    executor.postAfter(200ms, [&done] { done.set_value(); });

    EXPECT_EQ(future.wait_for(50ms), std::future_status::timeout);
    EXPECT_EQ(future.wait_for(500ms), std::future_status::ready);
}

TEST(BackgroundExecutorTests, PostAfterRunsOnlyOnce) {
    using namespace std::chrono_literals;

    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::atomic<int> count = 0;
    std::promise<void> done;
    auto future = done.get_future();

    executor.postAfter(50ms, [&] {
        if (++count == 1) {
            done.set_value();
        }
    });

    ASSERT_EQ(future.wait_for(1s), std::future_status::ready);

    std::this_thread::sleep_for(150ms);
    EXPECT_EQ(count.load(), 1);
}

TEST(BackgroundExecutorTests, PostEveryRunsRepeatedly) {
    using namespace std::chrono_literals;

    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::atomic<int> count = 0;
    std::promise<void> done;
    auto future = done.get_future();

    auto id = executor.postEvery(50ms, [&] {
        if (++count == 3) {
            done.set_value();
        }
    });

    ASSERT_NE(id, 0u);
    EXPECT_EQ(future.wait_for(1s), std::future_status::ready);
}

TEST(BackgroundExecutorTests, PostEveryRunImmediatelyRunsRightAway) {
    using namespace std::chrono_literals;

    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::promise<void> done;
    auto future = done.get_future();
    std::atomic<bool> fired = false;

    auto id = executor.postEvery(
        500ms,
        [&] {
            if (!fired.exchange(true)) {
                done.set_value();
            }
        },
        true);

    EXPECT_EQ(future.wait_for(100ms), std::future_status::ready);
    EXPECT_TRUE(executor.cancel(id));
}

TEST(BackgroundExecutorTests, CancelPreventsDelayedTaskFromRunning) {
    using namespace std::chrono_literals;

    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::atomic<int> count = 0;

    auto id = executor.postAfter(200ms, [&] { ++count; });

    EXPECT_TRUE(executor.cancel(id));

    std::this_thread::sleep_for(300ms);
    EXPECT_EQ(count.load(), 0);
}

TEST(BackgroundExecutorTests, CancelStopsPeriodicTask) {
    using namespace std::chrono_literals;

    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    std::atomic<int> count = 0;
    std::promise<void> ranTwice;
    auto future = ranTwice.get_future();

    auto id = executor.postEvery(50ms, [&] {
        int current = ++count;
        if (current == 2) {
            ranTwice.set_value();
        }
    });

    ASSERT_EQ(future.wait_for(1s), std::future_status::ready);

    EXPECT_TRUE(executor.cancel(id));
    int snapshot = count.load();

    std::this_thread::sleep_for(200ms);
    EXPECT_EQ(count.load(), snapshot);
}

TEST(BackgroundExecutorTests, CancelUnknownTaskReturnsFalse) {
    auto logger = std::make_shared<mocks::MockLogger>();
    BackgroundExecutor executor(logger);

    EXPECT_FALSE(executor.cancel(999999));
}

TEST(BackgroundExecutorTests, ThrowingTaskDoesNotKillScheduler) {
    using namespace std::chrono_literals;

    auto logger = std::make_shared<mocks::MockLogger>();

    BackgroundExecutor executor(logger);

    std::promise<void> done;
    auto future = done.get_future();

    executor.post([] { throw std::runtime_error("Error"); });
    executor.postAfter(50ms, [&done] { done.set_value(); });

    EXPECT_EQ(future.wait_for(1s), std::future_status::ready);
}