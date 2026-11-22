"""Model A to Model B multimodal embedding and compliant source schemas.

Model A와 Model B 간 멀티모달 임베딩 및 적법 원천 데이터 스키마 모듈입니다.
"""

import math
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from zerostreet_schema.enums import (
    AllowedDataSource,
    EntityType,
    SubscriptionTier,
    allowed_embedding_dims,
    infer_entity_type,
    normalize_entity_type,
)
from zerostreet_schema.pit import PointInTimeError, assert_no_lookahead, ensure_timezone_aware


class PublicFilingItem(BaseModel):
    """Public disclosure filing record (OpenDART, SEC EDGAR, etc.).

    공공·공시 원천 레코드(OpenDART, SEC EDGAR 등) 계약입니다.
    """

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
    """Macroeconomic indicator summary payload from BOK ECOS / FRED.

    한국은행 ECOS / FRED 거시경제 지표 요약 페이로드입니다.
    """

    source: AllowedDataSource = Field(default=AllowedDataSource.BOK_ECOS_FRED)
    us10y_2y_spread_bps: float | None = None
    krw_usd_20d_zscore: float | None = None
    extra_indicators: dict[str, float] = Field(default_factory=dict)


class AIExtractedFactsPayload(BaseModel):
    """Structured secondary facts derived by AI agents (no paid article copying).

    AI 에이전트가 공공 원천에서 추출한 구조화 2차 팩트(유료 기사 원문 복제 금지)입니다.
    """

    event_tags: list[str] = Field(default_factory=list)
    guidance_tone_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    risk_flag_score: float = Field(default=0.0, ge=0.0, le=1.0)
    agent_brief_ko: str = Field(default="", description="한국어 팩트 브리핑 요약")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceDataPayload(BaseModel):
    """Cleaned source data payload delivered alongside Model A z_mm tensors.

    Model A가 z_mm 임베딩과 함께 제공하는 정제 원천 데이터 페이로드입니다.
    """

    public_filings: list[PublicFilingItem] = Field(default_factory=list)
    macro_context: MacroContextPayload | None = None
    ai_extracted_facts: AIExtractedFactsPayload | None = None


class AssetEmbeddingItem(BaseModel):
    """Per-asset multimodal embedding tensor and source data item.

    개별 자산/지수 단위 멀티모달 임베딩 및 원천 데이터 항목입니다.
    """

    asset_id: str = Field(min_length=1, description="자산 식별자 (예: KRX:005930, US:SPY)")
    entity_type: EntityType | None = Field(
        default=None,
        description="정보 처리 대상 객체 단위 (equity/index/macro/sector/futures)",
    )
    event_ts: datetime | None = Field(default=None, description="사건 기준 시각")
    published_ts: datetime | None = Field(default=None, description="공시/발표 시각")
    available_ts: datetime = Field(description="모델 투입 가능 시각 (tz-aware)")
    is_blackout: bool = Field(
        default=False, description="True일 경우 Model B DynamicEmbeddingAdapter가 [MASK_SIGNAL] 사용"
    )
    embedding_z_mm: list[float] = Field(default_factory=list, description="MRL 멀티모달 상태 텐서")
    source_data: SourceDataPayload = Field(default_factory=SourceDataPayload)

    @field_validator("entity_type", mode="before")
    @classmethod
    def _normalize_item_entity_type(cls, value: EntityType | str | None) -> EntityType | None:
        if value is None:
            return None
        return normalize_entity_type(value)

    @field_validator("embedding_z_mm")
    @classmethod
    def _validate_finite_embedding(cls, values: list[float]) -> list[float]:
        for idx, val in enumerate(values):
            if not math.isfinite(val):
                raise ValueError(f"embedding_z_mm[{idx}] must be finite (got {val!r}).")
        return values

    @model_validator(mode="after")
    def _validate_pit_triad(self) -> "AssetEmbeddingItem":
        if self.entity_type is None:
            self.entity_type = infer_entity_type(self.asset_id)
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
    """Standard response batch schema for GET /v1/features/multimodal.

    GET /v1/features/multimodal 엔드포인트의 표준 응답 배치 스키마입니다.
    """

    schema_version: str = Field(default="1.0.0")
    as_of_ts: datetime = Field(description="추론 또는 백테스트 기준 시각 (tz-aware)")
    tier: SubscriptionTier = Field(description="구독 티어")
    embedding_model_version: str = Field(default="zs_mm_enc_v1_mrl", min_length=1)
    embedding_dim: int = Field(ge=0, description="요청 티어에 맞는 MRL 임베딩 차원 (0/32/128/256)")
    entity_types: list[EntityType] = Field(
        default_factory=list,
        description="배치에 포함된 처리 대상 객체 단위 목록",
    )
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

        if self.entity_types:
            deduped: list[EntityType] = []
            for et in self.entity_types:
                norm_et = normalize_entity_type(et)
                if norm_et not in deduped:
                    deduped.append(norm_et)
            self.entity_types = deduped
            allowed_units = set(self.entity_types)
        else:
            allowed_units = set()

        inferred_units: list[EntityType] = []
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
            item_unit = item.entity_type or infer_entity_type(item.asset_id)
            if allowed_units and item_unit not in allowed_units:
                raise ValueError(
                    f"[{item.asset_id}] entity_type={item_unit.value} is not allowed in batch "
                    f"entity_types={[u.value for u in self.entity_types]}."
                )
            if item_unit not in inferred_units:
                inferred_units.append(item_unit)

        if not self.entity_types and inferred_units:
            self.entity_types = inferred_units
        return self
