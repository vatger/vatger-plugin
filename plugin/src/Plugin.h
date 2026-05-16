#pragma once

#pragma warning(push, 0)
#include "EuroScopePlugIn.h"
#pragma warning(pop)

#include <memory>
#include <string>

#include "auth/IAuthService.h"
#include "log/ILogger.h"

namespace vatger {
class VatgerPlugin : public EuroScopePlugIn::CPlugIn {
   private:
    std::shared_ptr<logging::ILogger> m_logger;

   public:
    VatgerPlugin();
    ~VatgerPlugin();

    void DisplayMessage(const std::string &message, const std::string &sender = "VatgerPlugin");

    bool OnCompileCommand(const char *sCommandLine) override;

   private:
    std::unique_ptr<interfaces::IAuthService> m_authService;
};
}  // namespace vatger
