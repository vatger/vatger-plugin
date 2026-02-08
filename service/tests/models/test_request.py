import datetime

from models.request import SilentRequestModel


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
