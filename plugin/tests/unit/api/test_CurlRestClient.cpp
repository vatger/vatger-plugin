#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "api/CurlRestClient.h"
#include "tests/mocks/MockLogger.h"

TEST(CurlRestClientTest, TestGet) {
    api::CurlRestClient client;

    auto response =
        client.get("https://raw.githubusercontent.com/VATGER-Nav/loa/refs/heads/production/dist/agreements.json");

    ASSERT_TRUE(response.body.length() > 0);
}
