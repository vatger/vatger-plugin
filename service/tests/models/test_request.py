import datetime

import pytest

from domain.request import SilentRequestModel

pytestmark = pytest.mark.unit


def test_default():
    before = datetime.datetime.now(tz=datetime.UTC)

    model = SilentRequestModel(
        request_type="PUSHBACK",
        callsign="DLH123",
        airport_icao="EDDF",
    )

    after = datetime.datetime.now(tz=datetime.UTC)

    assert isinstance(model.created_at, datetime.datetime)
    assert model.created_at.tzinfo == datetime.UTC

    assert before <= model.created_at <= after
    assert isinstance(model.request_type, str)
