#include <gtest/gtest.h>

#include "utils/String.h"

using namespace utils;

namespace utils::tests {
TEST(StringUtilTest, Test_FindIcao_base) {
    // Test case: only ICAO code
    EXPECT_EQ(String::FindIcao("EDDK"), "EDDK");
    EXPECT_EQ(String::FindIcao("EDDF"), "EDDF");

    // Test case: ICAO code not in uppercase
    EXPECT_EQ(String::FindIcao("eddk"), "");

    // Test case: input is too short
    EXPECT_EQ(String::FindIcao("JFK"), "");

    // Test case: no ICAO code in input
    EXPECT_EQ(String::FindIcao("This is a test"), "");

    // Test case: empty string
    EXPECT_EQ(String::FindIcao(""), "");

    // Test case: spaces before and after words
    EXPECT_EQ(String::FindIcao("  EDDK  "), "EDDK");
    EXPECT_EQ(String::FindIcao("  KLAX   "), "KLAX");
}

TEST(StringUtilTest, Test_FindIcao_operators) {
    /* tests the FindIcao function based on airport names defined inside individual vACDM operators EuroScope packages*/

    // most only use ICAOs
    EXPECT_EQ(String::FindIcao("EDDK"), "EDDK");
    EXPECT_EQ(String::FindIcao("LPPT"), "LPPT");

    // some additionally include names
    EXPECT_EQ(String::FindIcao("EGLL London Heathrow"), "EGLL");
    EXPECT_EQ(String::FindIcao("EGKK London Gatwick"), "EGKK");
}
}  // namespace utils::tests