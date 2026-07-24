#pragma once

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
};
}  // namespace vatger