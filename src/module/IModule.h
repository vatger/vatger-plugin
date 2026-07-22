#pragma once

#include <string>

#include "module/IPlugin.h"

namespace vatger {

class IModule {
   public:
    virtual ~IModule() = default;

    virtual void init(IPlugin* plugin) = 0;
    virtual void handleOnCompileCommand(const std::string& command) = 0;
};
}  // namespace vatger