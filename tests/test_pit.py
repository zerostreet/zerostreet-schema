from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from zerostreet_schema.pit import (
    PointInTimeError,
    PointInTimeStamp,
    assert_no_lookahead,
    filter_pit_records,
)


def test_point_in_time_stamp_valid():
    t0 = datetime(2026, 9, 30, 0, 0, tzinfo=UTC)
    t1 = datetime(2026, 11, 14, 7, 10, tzinfo=UTC)
    t2 = datetime(2026, 11, 14, 22, 50, tzinfo=UTC)
    stamp = PointInTimeStamp(event_ts=t0, published_ts=t1, available_ts=t2)
    assert stamp.available_ts == t2


def test_point_in_time_stamp_rejects_naive_and_reversed():
    naive = datetime(2026, 11, 14, 7, 10)
    aware = datetime(2026, 11, 14, 7, 10, tzinfo=UTC)
    with pytest.raises(ValidationError, match="timezone-aware"):
        PointInTimeStamp(event_ts=naive, published_ts=aware, available_ts=aware)

    with pytest.raises(ValidationError, match="event_ts"):
        PointInTimeStamp(
            event_ts=aware + timedelta(days=1),
            published_ts=aware,
            available_ts=aware + timedelta(days=2),
        )

    with pytest.raises(ValidationError, match="published_ts"):
        PointInTimeStamp(
            event_ts=aware - timedelta(days=1),
            published_ts=aware + timedelta(hours=1),
            available_ts=aware,
        )


def test_assert_no_lookahead_and_filter():
    as_of = datetime(2026, 11, 21, 8, 30, tzinfo=UTC)
    assert_no_lookahead(as_of - timedelta(minutes=40), as_of, asset_id="KRX:005930")

    with pytest.raises(PointInTimeError, match="Look-ahead bias"):
        assert_no_lookahead(as_of + timedelta(minutes=1), as_of, asset_id="KRX:005930")

    rows = [
        {"id": "past", "ts": as_of - timedelta(hours=2)},
        {"id": "exact", "ts": as_of},
        {"id": "future", "ts": as_of + timedelta(seconds=1)},
    ]
    visible = filter_pit_records(rows, as_of, lambda r: r["ts"])
    assert [r["id"] for r in visible] == ["past", "exact"]
