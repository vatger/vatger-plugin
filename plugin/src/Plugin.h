#pragma once

#pragma warning(push, 0)
#include "EuroScopePlugIn.h"
#pragma warning(pop)

#include <memory>
#include <string>

#include "log/ILogger.h"

namespace vatger {
class VatgerPlugin : public EuroScopePlugIn::CPlugIn {
   private:
    std::shared_ptr<logging::ILogger> m_logger;

   public:
    VatgerPlugin();
    ~VatgerPlugin();

    void DisplayMessage(const std::string &message, const std::string &sender = "VatgerPlugin");
};
}  // namespace vatger
