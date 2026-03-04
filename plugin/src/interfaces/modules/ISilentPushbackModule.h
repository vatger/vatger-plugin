#pragma once

namespace modules {

class ISilentPushbackModule {
   public:
    virtual ~ISilentPushbackModule() = default;

    virtual bool pilotHasPushbackRequest(const std::string& callsign) = 0;
    virtual bool pilotHasTaxiRequest(const std::string& callsign) = 0;
};

}  // namespace modules
