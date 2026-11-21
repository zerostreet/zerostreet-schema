"""Model A -> Model B 멀티모달 임베딩 및 적법 원천 데이터 스키마 모듈."""

import math
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from zerostreet_schema.enums import AllowedDataSource, SubscriptionTier, allowed_embedding_dims
from zerostreet_schema.pit import PointInTimeError, assert_no_lookahead, ensure_timezone_aware


class PublicFilingItem(BaseModel):
    """공공·공시 원천 레코드(OpenDART / SEC EDGAR 등)."""

    source: AllowedDataSource = Field(description="허용된 공공·공시 원천 데이터 소스")
    filing_id: str = Field(min_length=1, description="공시 접수번호 또는 고유 ID")
    title: str = Field(min_length=1, description="공시 보고서 제목")
    event_ts: datetime | None = Field(default=None, description="사건/결산 기준 시각")
    published_ts: datetime = Field(description="실제 공시 발표 시각 (tz-aware)")
    available_ts: datetime | None = Field(default=None, description="모델 투입 가능 시각")
    key_metrics: dict[str, float | int | str] = Field(
        default_factory=dict, description="정량 재무/공시 지표"
    )
    source_url: str | None = Field(default=None, description="공시 원문 참조 URL")

    @model_validator(mode="after")
    def _validate_timestamps(self) -> "PublicFilingItem":
        ensure_timezone_aware(self.published_ts, "published_ts")
        if self.event_ts is not None:
            ensure_timezone_aware(self.event_ts, "event_ts")
            if self.event_ts > self.published_ts:
                raise PointInTimeError("PublicFilingItem: event_ts cannot exceed published_ts.")
        if self.available_ts is not None:
            ensure_timezone_aware(self.available_ts, "available_ts")
            if self.published_ts > self.available_ts:
                raise PointInTimeError("PublicFilingItem: published_ts cannot exceed available_ts.")
        return self


class MacroContextPayload(BaseModel):
    """한국은행 ECOS / FRED 거시경제 지표 요약 페이로드."""

    source: AllowedDataSource = Field(default=AllowedDataSource.BOK_ECOS_FRED)
    us10y_2y_spread_bps: float | None = None
    krw_usd_20d_zscore: float | None = None
    extra_indicators: dict[str, float] = Field(default_factory=dict)


class AIExtractedFactsPayload(BaseModel):
    """AI 에이전트가 공공 원천에서 자체 생성한 구조화 2차 팩트(유료 언론 기사 전문 복제 금지)."""

    event_tags: list[str] = Field(default_factory=list)
    guidance_tone_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    risk_flag_score: float = Field(default=0.0, ge=0.0, le=1.0)
    agent_brief_ko: str = Field(default="", description="한국어 팩트 브리핑 요약")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceDataPayload(BaseModel):
    """Model A가 z_mm과 함께 공급하는 정제 원천 데이터 페이로드."""

    public_filings: list[PublicFilingItem] = Field(default_factory=list)
    macro_context: MacroContextPayload | None = None
    ai_extracted_facts: AIExtractedFactsPayload | None = None


class AssetEmbeddingItem(BaseModel):
    """개별 자산/지수 단위 멀티모달 임베딩 및 원천 데이터 항목."""

    asset_id: str = Field(min_length=1, description="자산 식별자 (예: KRX:005930, US:SPY)")
    event_ts: datetime | None = Field(default=None, description="사건 기준 시각")
    published_ts: datetime | None = Field(default=None, description="공시/발표 시각")
    available_ts: datetime = Field(description="모델 투입 가능 시각 (tz-aware)")
    is_blackout: bool = Field(
        default=False, description="True일 경우 Model B DynamicEmbeddingAdapter가 [MASK_SIGNAL] 사용"
    )
    embedding_z_mm: list[float] = Field(default_factory=list, description="MRL 멀티모달 상태 텐서")
    source_data: SourceDataPayload = Field(default_factory=SourceDataPayload)

    @field_validator("embedding_z_mm")
    @classmethod
    def _validate_finite_embedding(cls, values: list[float]) -> list[float]:
        for idx, val in enumerate(values):
            if not math.isfinite(val):
                raise ValueError(f"embedding_z_mm[{idx}] must be finite (got {val!r}).")
        return values

    @model_validator(mode="after")
    def _validate_pit_triad(self) -> "AssetEmbeddingItem":
        ensure_timezone_aware(self.available_ts, "available_ts")
        if self.published_ts is not None:
            ensure_timezone_aware(self.published_ts, "published_ts")
            if self.published_ts > self.available_ts:
                raise PointInTimeError(
                    f"[{self.asset_id}] published_ts ({self.published_ts.isoformat()}) "
                    f"> available_ts ({self.available_ts.isoformat()})."
                )
        if self.event_ts is not None:
            ensure_timezone_aware(self.event_ts, "event_ts")
            upper_ts = self.published_ts or self.available_ts
            if self.event_ts > upper_ts:
                raise PointInTimeError(
                    f"[{self.asset_id}] event_ts ({self.event_ts.isoformat()}) "
                    f"> upper timestamp ({upper_ts.isoformat()})."
                )
        return self


class MultimodalFeatureBatch(BaseModel):
    """GET /v1/features/multimodal 표준 응답 배치 스키마."""

    schema_version: str = Field(default="1.0.0")
    as_of_ts: datetime = Field(description="추론 또는 백테스트 기준 시각 (tz-aware)")
    tier: SubscriptionTier = Field(description="구독 티어")
    embedding_model_version: str = Field(default="zs_mm_enc_v1_mrl", min_length=1)
    embedding_dim: int = Field(ge=0, description="요청 티어에 맞는 MRL 임베딩 차원 (0/32/128/256)")
    items: list[AssetEmbeddingItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_batch_invariants(self) -> "MultimodalFeatureBatch":
        ensure_timezone_aware(self.as_of_ts, "as_of_ts")
        allowed_dims = allowed_embedding_dims(self.tier)
        if self.embedding_dim not in allowed_dims:
            raise ValueError(
                f"embedding_dim={self.embedding_dim} is not allowed for tier={self.tier.value}. "
                f"Allowed: {sorted(allowed_dims)}."
            )

        for item in self.items:
            assert_no_lookahead(item.available_ts, self.as_of_ts, asset_id=item.asset_id)
            for filing in item.source_data.public_filings:
                filing_avail = filing.available_ts or filing.published_ts
                assert_no_lookahead(filing_avail, self.as_of_ts, asset_id=item.asset_id)

            if not item.is_blackout and len(item.embedding_z_mm) != self.embedding_dim:
                raise ValueError(
                    f"[{item.asset_id}] embedding_z_mm length ({len(item.embedding_z_mm)}) "
                    f"does not match embedding_dim ({self.embedding_dim})."
                )
        return self
