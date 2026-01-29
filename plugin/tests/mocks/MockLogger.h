#pragma once

#include <gmock/gmock.h>

#include "log/ILogger.h"

namespace mocks {
class MockLogger : public logging::ILogger {
   public:
    MOCK_METHOD(void, log,
                (const logging::LogLevel level, const std::string& message, const std::source_location location),
                (override));
};
}  // namespace mocks
