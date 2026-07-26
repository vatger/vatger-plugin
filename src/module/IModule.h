#pragma once

#include <optional>
#include <string>

#include "module/IPlugin.h"

namespace vatger {

class IModule {
   public:
    virtual ~IModule() = default;

    virtual void init(IPlugin* plugin) = 0;
    virtual void handleOnCompileCommand(const std::string& command) = 0;

    /// @brief gets called when the RunwayDialog closes
    /// @param icaos the list of active airports
    virtual void OnActiveAirportsChange(const std::list<std::string> icaos) {};

    struct RGB {
        std::uint8_t r, g, b;
    };
    struct TagData {
        std::string callsign;
    };
    struct TagRenderData {
        std::string item_string;
        std::optional<RGB> text_color;
    };
    virtual std::optional<TagRenderData> handleOnGetTagItem(const TagData& data, int item_code) {
        (void)data;
        (void)item_code;
        return std::nullopt;
    };
};
}  // namespace vatger