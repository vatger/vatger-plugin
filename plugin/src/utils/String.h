#pragma once

#include <algorithm>
#include <string>
#include <vector>

namespace utils {
class String {
   private:
    template <typename Separator>
    static auto SplitAux(const std::string &value, Separator &&separator) -> std::vector<std::string> {
        std::vector<std::string> result;
        std::string::size_type p = 0;
        std::string::size_type q;
        while ((q = separator(value, p)) != std::string::npos) {
            result.emplace_back(value, p, q - p);
            p = q + 1;
        }
        result.emplace_back(value, p);
        return result;
    }

   public:
    String() = delete;
    String(const String &) = delete;
    String(String &&) = delete;
    String &operator=(const String &) = delete;
    String &operator=(String &&) = delete;

    /// @brief replaces all markers by replace in message
    /// @param message the message which needs to be modified
    /// @param marker the string to replace
    /// @param replace the replacement
    static __inline void StringReplace(std::string &message, const std::string &marker, const std::string &replace) {
        std::size_t pos = message.find(marker, 0);
        while (std::string::npos != pos) {
            auto it = message.cbegin() + pos;
            message.replace(it, it + marker.length(), replace);
            pos = message.find(marker, pos + marker.length());
        }
    }

    /// @brief Splits value into chunks by the defined separtors
    /// @param value the string to split up
    /// @param separators the separators to split by
    /// @return the list of splitted chunks
    static auto SplitString(const std::string &value, const std::string &separators) -> std::vector<std::string> {
        return String::SplitAux(value, [&](const std::string &v, std::string::size_type p) noexcept {
            return v.find_first_of(separators, p);
        });
    }

    /// @brief removes leading and trailing whitespaces
    /// @param value the string to trim
    /// @param spaces characters that need to be removed
    /// @return the trimmed version of value
    static auto Trim(const std::string &value, const std::string &spaces = " \t") -> std::string {
        const auto begin = value.find_first_not_of(spaces, 0);
        if (std::string::npos == begin) return "";

        const auto end = value.find_last_not_of(spaces);
        const auto range = end - begin + 1;

        return value.substr(begin, range);
    }

    /// @brief finds the ICAO in a EuroScope airport name
    /// @details There is no consistent naming defined for EuroScope airports.
    /// This means that an airport name may include only the ICAO (e.g. "EDDK") or additionally the name aswell like
    /// "EDDK Cologne-Bonn" in no paticular order. This functions finds the ICAO in this string based on two
    /// conditions.
    /// 1. The airport ICAO is 4-letters long
    /// 2. The airport ICAO is full uppercase
    /// @param input the string to find the ICAO in
    /// @return the ICAO or "" if none was found
    static auto FindIcao(std::string input) -> std::string {
        if (input.size() < 4) return "";

        // split the input into separate words
        const auto words = SplitString(input, " ");

        for (auto word : words) {
            if (word.size() == 4 && std::all_of(word.begin(), word.end(), [](char c) { return std::isupper(c); })) {
                return word;
            }
        }

        return "";  // Return an empty string if no valid ICAO code is found
    }
};
}  // namespace utils