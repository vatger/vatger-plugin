#include "plugin.h"

#include <numeric>
#include <typeinfo>

#include "Version.h"
#include "api/CurlRestClient.h"
#include "auth/AuthService.h"
#include "config/ConfigLoader.h"
#include "config/PluginConfig.h"
#include "core/BackGroundExecuter.h"
#include "log/ConsoleLogger.h"
#include "log/SqliteLogger.h"
#include "module/sr/SilentRequestModule.h"
#include "system/WindowsSystem.h"
#include "utils/File.h"
#include "utils/String.h"

namespace vatger {
VatgerPlugin::VatgerPlugin()
    : CPlugIn(EuroScopePlugIn::COMPATIBILITY_CODE, PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR, PLUGIN_LICENSE) {
    m_logger = std::make_shared<logging::ConsoleLogger>();

    DisplayMessage("Version " + std::string(PLUGIN_VERSION) + " loaded", "Initialisation");
    m_logger->info("Version " + std::string(PLUGIN_VERSION) + " loaded");

    // get the dll-path
    char path[MAX_PATH + 1] = {0};
    GetModuleFileNameA((HINSTANCE)&__ImageBase, path, MAX_PATH);
    PathRemoveFileSpecA(path);
    const auto dllPath = std::string(path);
    config::PluginConfig config;
    config::ConfigLoader loader;
    if (false == loader.parse(dllPath + "/settings.txt", config) || false == config.valid) {
        std::string message = "settings.txt:" + std::to_string(loader.errorLine()) + ": " + loader.errorMessage();
        DisplayMessage(message, "Config");
    } else {
        DisplayMessage("loaded", "Config");
    }

    auto executer = std::make_shared<BackgroundExecutor>(m_logger);
    auto system = std::make_shared<WindowsSystem>();
    auto restClient = std::make_shared<api::CurlRestClient>();
    m_authService = std::make_unique<auth::AuthService>(restClient, system);

    sr_module_ = std::make_unique<silentrequests::SilentRequestModule>(executer, restClient);

    m_modules.push_back(dynamic_cast<vatger::IModule *>(m_authService.get()));
    m_modules.push_back(dynamic_cast<vatger::IModule *>(sr_module_.get()));
    for (const auto &module : m_modules) {
        module->init(this);
    }

    // ensure airports are set on startup
    OnAirportRunwayActivityChanged();
}
VatgerPlugin::~VatgerPlugin() {}

void VatgerPlugin::DisplayMessage(const std::string &message, const std::string &sender) {
    DisplayUserMessage(PLUGIN_NAME, sender.c_str(), message.c_str(), true, false, false, false, false);
}

bool VatgerPlugin::OnCompileCommand(const char *sCommandLine) {
    const std::string_view command(sCommandLine);

    if (!command.starts_with(".VATGER") && !command.starts_with(".vatger")) {
        return false;
    }

    std::vector<std::string> parts;
    std::string part;
    std::istringstream stream{std::string(command)};
    while (stream >> part) {
        parts.push_back(part);
    }

    if (parts.size() < 2) {
        return true;
    }

    std::string preword = parts[1];
    std::transform(preword.begin(), preword.end(), preword.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });

    auto it = m_compileCommands.find(preword);
    if (it != m_compileCommands.end()) {
        // rejoin remaining parts as the command line passed to the module
        std::string remainingCommand;
        for (size_t i = 2; i < parts.size(); ++i) {
            if (i > 2) remainingCommand += ' ';
            remainingCommand += parts[i];
        }
        it->second->handleOnCompileCommand(remainingCommand);
        return true;
    }

    DisplayMessage("Unknown command: " + preword);
    return true;
}

void VatgerPlugin::OnGetTagItem(EuroScopePlugIn::CFlightPlan FlightPlan, EuroScopePlugIn::CRadarTarget RadarTarget,
                                int ItemCode, int TagData, char sItemString[16], int *pColorCode, COLORREF *pRGB,
                                double *pFontSize) {
    (void)RadarTarget;
    (void)TagData;
    (void)pFontSize;

    if (FlightPlan.IsValid() == false) {
        return;
    }

    auto it = tagItemToModule_.find(ItemCode);
    if (it == tagItemToModule_.end()) {
        return;  // no module owns this item code
    }

    IModule::TagData data;
    data.callsign = FlightPlan.GetCallsign();

    const auto render_data = it->second->handleOnGetTagItem(data, ItemCode);

    if (!render_data) {
        return;  // module owns this item code, but did not return data to show
    }
    std::strcpy(sItemString, render_data->item_string.c_str());

    if (render_data->text_color) {
        *pColorCode = EuroScopePlugIn::TAG_COLOR_RGB_DEFINED;
        *pRGB = RGB(render_data->text_color->r, render_data->text_color->g, render_data->text_color->b);
    } else {
        *pColorCode = EuroScopePlugIn::TAG_COLOR_DEFAULT;
    }
}

void VatgerPlugin::RegisterModuleOnGetTagItem(TagItemDefinition item, IModule *module) {
    const auto [it, inserted] = tagItemToModule_.emplace(item.code, module);
    if (!inserted) {
        // TODO: handle two modules claiming the same ItemCode
        m_logger->error("Two modules tried registering item code" + std::to_string(item.code) +
                        ", conflicting module: " + typeid(*module).name());
        return;
    }
    RegisterTagItemType(item.name.c_str(), item.code);
}

void VatgerPlugin::RegisterModuleOnCompileCommand(const std::string &preword, IModule *module) {
    std::string normalizedPreword = preword;
    std::transform(normalizedPreword.begin(), normalizedPreword.end(), normalizedPreword.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });

    auto [it, inserted] = m_compileCommands.emplace(normalizedPreword, module);
    if (!inserted) {
        m_logger->error("CompileCommand Preword " + normalizedPreword + " already taken");
    }
}

void VatgerPlugin::OnAirportRunwayActivityChanged() {
    std::list<std::string> activeAirports;

    EuroScopePlugIn::CSectorElement airport;
    for (airport = this->SectorFileElementSelectFirst(EuroScopePlugIn::SECTOR_ELEMENT_AIRPORT);
         airport.IsValid() == true;
         airport = this->SectorFileElementSelectNext(airport, EuroScopePlugIn::SECTOR_ELEMENT_AIRPORT)) {
        // skip airport if it is not selected as active airport for departures or arrivals
        if (false == airport.IsElementActive(true, 0) && false == airport.IsElementActive(false, 0)) continue;

        // get the airport ICAO
        auto airportICAO = utils::String::FindIcao(utils::String::Trim(airport.GetName()));
        // skip airport if no ICAO has been found
        if (airportICAO == "") continue;

        // check if the airport has been added already, add if it does not exist
        if (std::find(activeAirports.begin(), activeAirports.end(), airportICAO) == activeAirports.end()) {
            activeAirports.push_back(airportICAO);
        }
    }

    if (activeAirports.empty()) {
        m_logger->info("Airport/Runway Change, no active airports");
    } else {
        m_logger->info("Airport/Runway Change, active airports: " +
                       std::accumulate(std::next(activeAirports.begin()), activeAirports.end(), activeAirports.front(),
                                       [](const std::string &acc, const std::string &str) { return acc + " " + str; }));
    }

    for (const auto &module : m_modules) {
        module->OnActiveAirportsChange(activeAirports);
    }
}

}  // namespace vatger
