#pragma once

#include <string>

namespace vatger {

class IModule;

/// @brief provides access to the plugin for modules so they can register their TagItems, CompileCommands
class IPlugin {
   public:
    virtual ~IPlugin() = default;

    virtual void DisplayMessage(const std::string& message, const std::string& sender = "VatgerPlugin") = 0;
    virtual void RegisterModuleOnCompileCommand(const std::string& preword, IModule* module) = 0;
};

}  // namespace vatger