import json

import pytest
import requests

from gateways.vatsim.datafeed_dto import DatafeedModel

pytestmark = pytest.mark.unit


def test_from_api():
    data = requests.get("https://data.vatsim.net/v3/vatsim-data.json").json()

    DatafeedModel(**data)


def test_from_example():
    data = """{
  "general": {
    "version": 3,
    "update_timestamp": "1970-01-01T00:00:00.000000Z",
    "connected_clients": 0,
    "unique_users": 0
  },
  "pilots": [
    {
      "cid": 1234567,
      "name": "Kennedy Steve KJFK",
      "callsign": "DAL1",
      "server": "USA-EAST",
      "pilot_rating": 0,
      "military_rating": 0,
      "latitude": 40.64222,
      "longitude": -73.76981,
      "altitude": 12,
      "groundspeed": 0,
      "transponder": "3456",
      "heading": 44,
      "qnh_i_hg": 29.92,
      "qnh_mb": 1013,
      "flight_plan": {
        "flight_rules": "I",
        "aircraft": "B764/H-SDE3FGHIM3RWXY/LB1",
        "aircraft_faa": "B764/L",
        "aircraft_short": "B764",
        "departure": "KJFK",
        "arrival": "EGLL",
        "alternate": "EGBB",
        "deptime": "0000",
        "enroute_time": "0615",
        "fuel_time": "0745",
        "remarks": "/V/",
        "route": "GREKI DCT JUDDS DCT MARTN DCT BAREE DCT NEEKO NATX LIMRI NATX XETBO DCT EVRIN DCT INFEC DCT JETZI DCT OGLUN DCT OCTIZ P2 SIRIC SIRI1H",
        "revision_id": 1,
        "assigned_transponder": "3456"
      },
      "logon_time": "1970-01-01T00:00:00.000000Z",
      "last_updated": "1970-01-01T00:00:00.000000Z"
    }
  ],
  "controllers": [
    {
      "cid": 1234567,
      "name": "Kennedy Steve KJFK",
      "callsign": "JFK_GND",
      "frequency": "121.900",
      "facility": 0,
      "rating": 0,
      "server": "USA-EAST",
      "visual_range": 20,
      "text_atis": [
        "John F. Kennedy Ground (121.900)",
        "Online until 23:00z",
        "Feedback? nyartcc.org/feedback"
      ],
      "last_updated": "1970-01-01T00:00:00.000000Z",
      "logon_time": "1970-01-01T00:00:00.000000Z"
    }
  ],
  "atis": [
    {
      "cid": 1234567,
      "name": "Kennedy Steve KJFK",
      "callsign": "KJFK_ATIS",
      "frequency": "128.725",
      "facility": 0,
      "rating": 0,
      "server": "USA-EAST",
      "visual_range": 0,
      "atis_code": "A",
      "text_atis": [
        "KJFK ATIS INFO A 0000Z. 20004KT 10SM SCT013 BKN060 OVC082 22/20",
        "A2992 (TWO NINER NINER TWO). APCH IN USE ILS RY 22L, ILS 22R.",
        "DEPTG RY 22R... BIRD ACTIVITY VICINITY ARPT. NUM CRANES",
        "OPERATING AT JFK. OPERATE XPDR ON MODE *C ON ALL TAXIWAYS AND",
        "RUNWAYS. READBACK ALL RWY HOLD SHORT INSTRUCTIONS....ADVS YOU",
        "HAVE INFO A"
      ],
      "last_updated": "1970-01-01T00:00:00.000000Z",
      "logon_time": "1970-01-01T00:00:00.000000Z"
    }
  ],
  "servers": [
    {
      "ident": "USA-EAST",
      "hostname_or_ip": "192.0.2.10",
      "location": "New York, USA",
      "name": "USA-EAST",
      "client_connections_allowed": true,
      "is_sweatbox": false
    }
  ],
  "prefiles": [
    {
      "cid": 1234567,
      "name": "1234567",
      "callsign": "DAL1",
      "flight_plan": {
        "flight_rules": "I",
        "aircraft": "B764/H-SDE3FGHIM3RWXY/LB1",
        "aircraft_faa": "B764/L",
        "aircraft_short": "B764",
        "departure": "KJFK",
        "arrival": "EGLL",
        "alternate": "EGBB",
        "deptime": "0000",
        "enroute_time": "0615",
        "fuel_time": "0745",
        "remarks": "/V/",
        "route": "GREKI DCT JUDDS DCT MARTN DCT BAREE DCT NEEKO NATX LIMRI NATX XETBO DCT EVRIN DCT INFEC DCT JETZI DCT OGLUN DCT OCTIZ P2 SIRIC SIRI1H",
        "revision_id": 1,
        "assigned_transponder": "3456"
      },
      "last_updated": "1970-01-01T00:00:00.000000Z"
    }
  ],
  "facilities": [
    {
      "id": 0,
      "short": "FAC",
      "long_name": "Example Facility"
    }
  ],
  "ratings": [
    {
      "id": 0,
      "short_name": "EXMP",
      "long_name": "Example Rating"
    }
  ],
  "pilot_ratings": [
    {
      "id": 0,
      "short_name": "EXMP",
      "long_name": "Example Rating"
    }
  ],
  "military_ratings": [
    {
      "id": 0,
      "short_name": "EXMP",
      "long_name": "Example Rating"
    }
  ]
}"""  # noqa: E501

    DatafeedModel(**json.loads(data))
