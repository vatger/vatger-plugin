#include "plugin.h"

#include "Version.h"
#include "log/ConsoleLogger.h"
#include "log/SqlLiteLogger.h"
#include "utils/File.h"

namespace vatger {
VatgerPlugin::VatgerPlugin()
    : CPlugIn(EuroScopePlugIn::COMPATIBILITY_CODE, PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR, PLUGIN_LICENSE) {
    m_logger = std::make_shared<logging::ConsoleLogger>();

    DisplayMessage("Version " + std::string(PLUGIN_VERSION) + " loaded", "Initialisation");
    m_logger->info("Version " + std::string(PLUGIN_VERSION) + " loaded");
}
VatgerPlugin::~VatgerPlugin() {}

void VatgerPlugin::DisplayMessage(const std::string &message, const std::string &sender) {
    DisplayUserMessage(PLUGIN_NAME, sender.c_str(), message.c_str(), true, false, false, false, false);
}
}  // namespace vatger