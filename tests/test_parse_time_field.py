import pytest
import re
from datetime import timedelta


TIMEDELTA_NAMES = {
    "w": "weeks",
    "d": "days",
    "h": "hours",
    "m": "minutes",
    "s": "seconds",
    "ms": "milliseconds",
    "us": "microseconds",
}


def parse_time_field(txt: str) -> float:
    """
    Parses a time field from a NextFlow report and returns time in seconds
    """
    total_td = None
    for m in re.finditer(r"\b([\+\-\d\.e]+)([a-df-z]+)\b", txt):
        number, unit = m.groups()
        td_name = TIMEDELTA_NAMES.get(unit)
        if not td_name:
            msg = f"Unexpected time unit '{unit}' in time field '{txt}'"
            raise ValueError(msg)
        td = timedelta(**{td_name: float(number)})
        if total_td:
            total_td += td
        else:
            total_td = td

    if total_td is None:
        msg = f"Failed to parse time from field '{txt}'"
        raise ValueError(msg)

    return total_td.total_seconds()


def test_parse_time_field():
    field_seconds = {
        "0s": 0.0,
        "1m": 60.0,
        "1ms": 0.001,
        "3.7s": 3.7,
        "5.0e-3s": 0.005,
        "3m 4s": 184.0,
        "2d 4h 36ms": 187200.036,
        "4us 1m 1m": 120.000004,
    }
    for txt, secs in field_seconds.items():
        assert parse_time_field(txt) == secs
    with pytest.raises(ValueError, match=r"Unexpected time unit"):
        parse_time_field("3y")
    with pytest.raises(ValueError, match=r"Failed to parse time from field"):
        parse_time_field("")
