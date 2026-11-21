"""제로 트러스트 RunTrace 텔레메트리 및 alpha-wiki ThesisManifest v2.0 스키마 모듈."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from zerostreet_schema.enums import DaemonStatus
from zerostreet_schema.pit import ensure_timezone_aware

FORBIDDEN_SECRET_FIELDS: frozenset[str] = frozenset(
    {
        "account_number",
        "kis_cano",
        "app_key",
        "kis_app_key",
        "app_secret",
        "kis_app_secret",
        "total_krw",
        "total_balance_krw",
        "order_amount_krw",
        "api_key",
        "secret_key",
    }
)


class RunTrace(BaseModel):
    """AlphaGraph 실행 종료 후 로컬 저장 및 선택적 클라우드 전송용 제로 트러스트 스냅샷."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    policy_checkpoint_id: str = Field(min_length=1)
    multimodal_tensor_version: str = Field(default="blackout_ohlcv_only", min_length=1)
    daemon_status: DaemonStatus
    positions_weights: dict[str, float] = Field(default_factory=dict)
    target_vs_filled_diff_bps: dict[str, float] = Field(default_factory=dict)
    execution_slippage_bps: float = Field(default=0.0, ge=0.0)
    guardrail_checks_passed: bool
    hitl_approved_latency_sec: float = Field(default=0.0, ge=0.0)
    recorded_at: datetime | None = None

    @model_validator(mode="after")
    def _validate_weights_and_zero_trust(self) -> "RunTrace":
        for key in (*self.positions_weights.keys(), *self.target_vs_filled_diff_bps.keys()):
            if key.lower() in FORBIDDEN_SECRET_FIELDS:
                raise ValueError(f"Forbidden sensitive key detected in RunTrace: {key}")

        for asset, weight in self.positions_weights.items():
            if not (0.0 <= weight <= 1.0 + 1e-6):
                raise ValueError(f"Weight for {asset} must be within [0.0, 1.0], got {weight}.")

        if self.positions_weights:
            total_weight = sum(self.positions_weights.values())
            if total_weight > 1.0001:
                raise ValueError(
                    f"Sum of positions_weights must be <= 1.0001 (got {total_weight:.6f})."
                )

        if self.recorded_at is not None:
            ensure_timezone_aware(self.recorded_at, "recorded_at")
        return self


class KillCriterion(BaseModel):
    """정량적 가설 무효화 조건(Quantitative Kill Criterion)."""

    metric: str = Field(min_length=1)
    operator: Literal["<=", ">=", "<", ">", "=="]
    threshold: float
    description: str = Field(min_length=1)


class RunTraceRef(BaseModel):
    """ThesisManifest가 참조하는 AlphaGraph 실행 메타데이터."""

    run_id: str = Field(min_length=1)
    policy_checkpoint_id: str = Field(min_length=1)
    multimodal_tensor_version: str = Field(min_length=1)
    target_weight_delta: float


class SourceFactsSnapshot(BaseModel):
    """ThesisManifest 내 Point-in-Time 검증 완료 팩트 스냅샷."""

    available_ts: datetime
    event_tags: list[str] = Field(default_factory=list)
    guidance_tone_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    risk_flag_score: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_ts(self) -> "SourceFactsSnapshot":
        ensure_timezone_aware(self.available_ts, "available_ts")
        return self


class ThesisManifest(BaseModel):
    """alpha-wiki v2.0 구조화 리서치 및 HITL 브리핑 매니페스트 (thesis_manifest.json)."""

    schema_version: str = Field(default="2.0")
    generated_at: datetime
    ticker: str = Field(min_length=1)
    corp_name: str = Field(min_length=1)
    run_trace_ref: RunTraceRef | None = None
    source_facts_snapshot: SourceFactsSnapshot
    core_fact_summary: list[str] = Field(min_length=1)
    devils_advocate_risks: list[str] = Field(min_length=1)
    quantitative_kill_criteria: list[KillCriterion] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_generated_at(self) -> "ThesisManifest":
        ensure_timezone_aware(self.generated_at, "generated_at")
        return self
