#pragma once

#include <vector>

#include "types/SilentRequest.h"

class ISilentRequestService {
   public:
    virtual std::vector<SilentRequest> getSilentRequests() = 0;
};
