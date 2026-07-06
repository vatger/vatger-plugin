#include <Windows.h>
#include <gtest/gtest.h>

#include <cstdio>
#include <filesystem>
#include <fstream>
#include <limits>
#include <random>
#include <sstream>
#include <string>

#include "config/ConfigLoader.h"
#include "config/PluginConfig.h"


using namespace config;

namespace {

class TempConfigFile {
   public:
    explicit TempConfigFile(const std::string &contents) {
        static std::mt19937 rng{std::random_device{}()};
        std::ostringstream name;
        name << "configloader_test_" << rng() << ".cfg";
        path_ = (std::filesystem::temp_directory_path() / name.str()).string();

        std::ofstream out(path_);
        out << contents;
    }

    ~TempConfigFile() { std::filesystem::remove(path_); }

    const std::string &path() const { return path_; }

   private:
    std::string path_;
};

}  // namespace

TEST(ConfigLoaderTest, InitialStateHasNoError) {
    ConfigLoader loader;
    EXPECT_FALSE(loader.errorFound());
    EXPECT_EQ(loader.errorLine(), std::numeric_limits<std::uint32_t>::max());
}

TEST(ConfigLoaderTest, MissingFileFails) {
    ConfigLoader loader;
    config::PluginConfig cfg;

    EXPECT_FALSE(loader.parse("/nonexistent/path/does-not-exist.cfg", cfg));
    EXPECT_TRUE(loader.errorFound());
    EXPECT_EQ(loader.errorLine(), 0u);
    EXPECT_EQ(loader.errorMessage(), "Unable to open the configuration file");
}

TEST(ConfigLoaderTest, ParsesServerUrl) {
    TempConfigFile file("SERVER_url = https://example.com\n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    ASSERT_TRUE(loader.parse(file.path(), cfg));
    EXPECT_FALSE(loader.errorFound());
    EXPECT_TRUE(cfg.valid);
    EXPECT_EQ(cfg.server_url, "https://example.com");
}

TEST(ConfigLoaderTest, ParsesUnknownKeysIntoExtraMap) {
    TempConfigFile file("some_key=some_value\nother_key = other value\n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    ASSERT_TRUE(loader.parse(file.path(), cfg));
    ASSERT_EQ(cfg.extra.count("some_key"), 1u);
    EXPECT_EQ(cfg.extra.at("some_key"), "some_value");
    ASSERT_EQ(cfg.extra.count("other_key"), 1u);
    EXPECT_EQ(cfg.extra.at("other_key"), "other value");
}

TEST(ConfigLoaderTest, SkipsBlankLinesAndComments) {
    TempConfigFile file(
        "# a comment\n"
        "\n"
        "   \n"
        "# SERVER_url = should_be_ignored\n"
        "key=value\n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    ASSERT_TRUE(loader.parse(file.path(), cfg));
    EXPECT_EQ(cfg.server_url, "https://plugin.vatger.de");  // untouched default
    ASSERT_EQ(cfg.extra.count("key"), 1u);
    EXPECT_EQ(cfg.extra.at("key"), "value");
}

TEST(ConfigLoaderTest, TrimsWhitespaceAroundKeyAndValue) {
    TempConfigFile file("   key   =   value with spaces   \n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    ASSERT_TRUE(loader.parse(file.path(), cfg));
    ASSERT_EQ(cfg.extra.count("key"), 1u);
    EXPECT_EQ(cfg.extra.at("key"), "value with spaces");
}

TEST(ConfigLoaderTest, RejectsLineWithoutEquals) {
    TempConfigFile file("this_line_has_no_equals_sign\n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    EXPECT_FALSE(loader.parse(file.path(), cfg));
    EXPECT_TRUE(loader.errorFound());
    EXPECT_EQ(loader.errorLine(), 1u);
    EXPECT_EQ(loader.errorMessage(), "Invalid configuration entry");
}

TEST(ConfigLoaderTest, RejectsLineWithMultipleEquals) {
    TempConfigFile file("key=value=extra\n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    EXPECT_FALSE(loader.parse(file.path(), cfg));
    EXPECT_TRUE(loader.errorFound());
    EXPECT_EQ(loader.errorLine(), 1u);
    EXPECT_EQ(loader.errorMessage(), "Invalid configuration entry");
}

TEST(ConfigLoaderTest, RejectsEmptyValue) {
    TempConfigFile file("key=\n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    EXPECT_FALSE(loader.parse(file.path(), cfg));
    EXPECT_TRUE(loader.errorFound());
    EXPECT_EQ(loader.errorLine(), 1u);
    EXPECT_EQ(loader.errorMessage(), "Invalid entry");
}

TEST(ConfigLoaderTest, ReportsCorrectLineNumberForErrorAfterValidLines) {
    TempConfigFile file(
        "SERVER_url = https://example.com\n"
        "good_key = good_value\n"
        "bad_line_without_equals\n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    EXPECT_FALSE(loader.parse(file.path(), cfg));
    EXPECT_EQ(loader.errorLine(), 3u);
}

TEST(ConfigLoaderTest, LaterDuplicateKeyOverwritesEarlierOne) {
    TempConfigFile file("SERVER_url=https://first.example\nSERVER_url=https://second.example\n");
    ConfigLoader loader;
    config::PluginConfig cfg;

    ASSERT_TRUE(loader.parse(file.path(), cfg));
    EXPECT_EQ(cfg.server_url, "https://second.example");
}