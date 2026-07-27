#pragma once

#include <optional>
#include <string>

#include "auth/AuthTypes.h"

namespace interfaces {

class IAuthModule {
   public:
    virtual ~IAuthModule() = default;

    virtual bool isAuthenticated() = 0;
    virtual std::optional<std::string> getToken() = 0;
    virtual auth::AuthFlowResult startAuthFlow() = 0;
};
}  // namespace interfaces