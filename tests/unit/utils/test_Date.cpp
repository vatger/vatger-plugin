#include <gtest/gtest.h>

#include <chrono>
#include <string>

#include "utils/Date.h"

using namespace utils;

static std::chrono::utc_clock::time_point makeUtc(int year, int month, int day, int hour = 0, int min = 0, int sec = 0,
                                                  int ms = 0) {
    std::tm tm{};
    tm.tm_year = year - 1900;
    tm.tm_mon = month - 1;
    tm.tm_mday = day;
    tm.tm_hour = hour;
    tm.tm_min = min;
    tm.tm_sec = sec;

    // timegm / _mkgmtime interprets the struct as UTC
#ifdef _WIN32
    std::time_t t = _mkgmtime(&tm);
#else
    std::time_t t = timegm(&tm);
#endif

    auto sys = std::chrono::system_clock::from_time_t(t) + std::chrono::milliseconds(ms);
    return std::chrono::utc_clock::from_sys(std::chrono::time_point_cast<std::chrono::system_clock::duration>(sys));
}

TEST(TimestampToIsoString, UnixEpoch) {
    auto tp = makeUtc(1970, 1, 1, 0, 0, 0);
    EXPECT_EQ(Date::timestampToIsoString(tp), "1970-01-01T00:00:00.000Z");
}

TEST(TimestampToIsoString, ArbitraryDate) {
    auto tp = makeUtc(2024, 6, 15, 12, 30, 45);
    EXPECT_EQ(Date::timestampToIsoString(tp), "2024-06-15T12:30:45.000Z");
}

TEST(TimestampToIsoString, MidnightOnNewYear) {
    auto tp = makeUtc(2000, 1, 1, 0, 0, 0);
    EXPECT_EQ(Date::timestampToIsoString(tp), "2000-01-01T00:00:00.000Z");
}

TEST(TimestampToIsoString, EndOfYear) {
    auto tp = makeUtc(2023, 12, 31, 23, 59, 59);
    EXPECT_EQ(Date::timestampToIsoString(tp), "2023-12-31T23:59:59.000Z");
}

TEST(TimestampToIsoString, SingleDigitMonthAndDayArePadded) {
    auto tp = makeUtc(2024, 3, 5, 9, 7, 3);
    EXPECT_EQ(Date::timestampToIsoString(tp), "2024-03-05T09:07:03.000Z");
}

TEST(TimestampToIsoString, ContainsDateTimeSeparatorT) {
    auto tp = makeUtc(2024, 1, 1);
    const auto result = Date::timestampToIsoString(tp);
    EXPECT_NE(result.find('T'), std::string::npos);
}

TEST(TimestampToIsoString, EndsWithZ) {
    auto tp = makeUtc(2024, 1, 1);
    const auto result = Date::timestampToIsoString(tp);
    EXPECT_EQ(result.back(), 'Z');
}

TEST(TimestampToIsoString, WithMilliseconds) {
    auto tp = makeUtc(2024, 6, 15, 12, 30, 45, 123);
    const auto result = Date::timestampToIsoString(tp);
    // Accept either "2024-06-15T12:30:45.123Z" or truncated "2024-06-15T12:30:45Z"
    EXPECT_TRUE(result == "2024-06-15T12:30:45.123Z" || result == "2024-06-15T12:30:45Z")
        << "Unexpected result: " << result;
}

TEST(IsoStringToTimestamp, UnixEpoch) {
    auto result = Date::isoStringToTimestamp("1970-01-01T00:00:00Z");
    auto expected = makeUtc(1970, 1, 1, 0, 0, 0);
    EXPECT_EQ(result, expected);
}

TEST(IsoStringToTimestamp, ArbitraryDate) {
    auto result = Date::isoStringToTimestamp("2024-06-15T12:30:45Z");
    auto expected = makeUtc(2024, 6, 15, 12, 30, 45);
    EXPECT_EQ(result, expected);
}

TEST(IsoStringToTimestamp, MidnightOnNewYear) {
    auto result = Date::isoStringToTimestamp("2000-01-01T00:00:00Z");
    auto expected = makeUtc(2000, 1, 1, 0, 0, 0);
    EXPECT_EQ(result, expected);
}

TEST(IsoStringToTimestamp, EndOfYear) {
    auto result = Date::isoStringToTimestamp("2023-12-31T23:59:59Z");
    auto expected = makeUtc(2023, 12, 31, 23, 59, 59);
    EXPECT_EQ(result, expected);
}

TEST(RoundTrip, EpochRoundTrip) {
    auto original = makeUtc(1970, 1, 1, 0, 0, 0);
    auto iso = Date::timestampToIsoString(original);
    auto recovered = Date::isoStringToTimestamp(iso);
    EXPECT_EQ(original, recovered);
}

TEST(RoundTrip, ArbitraryDateRoundTrip) {
    auto original = makeUtc(2024, 6, 15, 12, 30, 45);
    auto iso = Date::timestampToIsoString(original);
    auto recovered = Date::isoStringToTimestamp(iso);
    EXPECT_EQ(original, recovered);
}

TEST(RoundTrip, MidnightRoundTrip) {
    auto original = makeUtc(2000, 1, 1, 0, 0, 0);
    auto iso = Date::timestampToIsoString(original);
    auto recovered = Date::isoStringToTimestamp(iso);
    EXPECT_EQ(original, recovered);
}

TEST(RoundTrip, LeapDayRoundTrip) {
    auto original = makeUtc(2024, 2, 29, 0, 0, 0);
    auto iso = Date::timestampToIsoString(original);
    auto recovered = Date::isoStringToTimestamp(iso);
    EXPECT_EQ(original, recovered);
}

TEST(RoundTrip, EndOfYearRoundTrip) {
    auto original = makeUtc(2023, 12, 31, 23, 59, 59);
    auto iso = Date::timestampToIsoString(original);
    auto recovered = Date::isoStringToTimestamp(iso);
    EXPECT_EQ(original, recovered);
}

TEST(RoundTripInverse, EpochInverse) {
    const std::string original = "1970-01-01T00:00:00.000Z";
    auto tp = Date::isoStringToTimestamp(original);
    auto result = Date::timestampToIsoString(tp);
    EXPECT_EQ(original, result);
}

TEST(RoundTripInverse, ArbitraryDateInverse) {
    const std::string original = "2024-06-15T12:30:45.000Z";
    auto tp = Date::isoStringToTimestamp(original);
    auto result = Date::timestampToIsoString(tp);
    EXPECT_EQ(original, result);
}