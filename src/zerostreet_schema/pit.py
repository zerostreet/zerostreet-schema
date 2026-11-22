"""Point-in-Time triple-timestamp validators preventing look-ahead bias.

Point-in-Time 3중 타임스탬프 기반 시점 누수(Look-Ahead Bias) 방지 검증 유틸리티입니다.
"""

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, Field, model_validator

T = TypeVar("T")


class PointInTimeError(ValueError):
    """Raised when look-ahead bias or timestamp chronology is violated.

    시점 누수(Look-Ahead Bias) 또는 타임스탬프 순서 위반 시 발생하는 예외입니다.
    """


def ensure_timezone_aware(dt: datetime, field_name: str) -> datetime:
    """Validate that a datetime carries tzinfo and a non-None UTC offset.

    datetime 객체가 timezone-aware(tzinfo 및 오프셋 포함)인지 검증합니다.
    """
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise PointInTimeError(f"{field_name} must be timezone-aware (got naive datetime: {dt!r}).")
    return dt


class PointInTimeStamp(BaseModel):
    """Triple-timestamp contract (event -> publication -> model availability).

    금융 원천 데이터의 3중 타임스탬프(사건 발생 -> 공시 발표 -> 모델 투입 가능) 계약입니다.
    """

    event_ts: datetime = Field(description="실적 기준일 또는 사건 발생 시각 (tz-aware)")
    published_ts: datetime = Field(description="공시/발표가 외부에 실제 공개된 시각 (tz-aware)")
    available_ts: datetime = Field(description="실전 모델/백테스트에 투입 가능한 가장 이른 시각 (tz-aware)")

    @model_validator(mode="after")
    def _validate_chronology(self) -> "PointInTimeStamp":
        ensure_timezone_aware(self.event_ts, "event_ts")
        ensure_timezone_aware(self.published_ts, "published_ts")
        ensure_timezone_aware(self.available_ts, "available_ts")

        if self.event_ts > self.published_ts:
            raise PointInTimeError(
                f"Point-in-Time order violated: event_ts ({self.event_ts.isoformat()}) "
                f"> published_ts ({self.published_ts.isoformat()})."
            )
        if self.published_ts > self.available_ts:
            raise PointInTimeError(
                f"Point-in-Time order violated: published_ts ({self.published_ts.isoformat()}) "
                f"> available_ts ({self.available_ts.isoformat()})."
            )
        return self


def assert_no_lookahead(
    available_ts: datetime,
    as_of_ts: datetime,
    asset_id: str = "",
) -> None:
    """Assert available_ts <= as_of_ts to block future information leakage.

    available_ts <= as_of_ts 불변식을 검증하여 미래 시점 데이터 참조를 차단합니다.
    """
    ensure_timezone_aware(available_ts, "available_ts")
    ensure_timezone_aware(as_of_ts, "as_of_ts")
    if available_ts > as_of_ts:
        prefix = f"[{asset_id}] " if asset_id else ""
        raise PointInTimeError(
            f"{prefix}Look-ahead bias detected: available_ts ({available_ts.isoformat()}) "
            f"> as_of_ts ({as_of_ts.isoformat()})."
        )


def filter_pit_records(
    records: Iterable[T],
    as_of_ts: datetime,
    ts_getter: Callable[[T], datetime],
) -> list[T]:
    """Filter records observable at or before as_of_ts (available_ts <= as_of_ts).

    as_of_ts 시점 기준 관측 가능한(available_ts <= as_of_ts) 레코드만 필터링합니다.
    """
    ensure_timezone_aware(as_of_ts, "as_of_ts")
    visible: list[T] = []
    for record in records:
        rec_ts = ensure_timezone_aware(ts_getter(record), "record.available_ts")
        if rec_ts <= as_of_ts:
            visible.append(record)
    return visible
