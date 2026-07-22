#pragma once

#include <optional>
#include <string>
#include <vector>

enum class TransferType { CLIMBING, DESCENDING };
enum class ReleaseType { CLIMB, DESCEND, TURNS, FULL };

struct Agreement {
    std::optional<std::vector<std::string>> adep;
    std::optional<std::vector<std::string>> ades;
    std::optional<std::vector<std::string>> runway;
    std::optional<std::string> cop;
    std::optional<std::string> route_before;
    std::optional<std::string> route_after;
    std::optional<int> level;
    std::optional<TransferType> transfer_type;
    std::optional<int> sfl;
    std::optional<std::pair<int, std::string>> level_at;
    std::optional<std::string> qnh;
    std::optional<ReleaseType> releases;
    std::optional<std::string> remarks;
    std::optional<bool> vertical;
    std::string from_sector;
    std::string to_sector;
};