"""User-defined Policy Head compilation configuration and Foundry contracts.

사용자 개별 Policy Head 컴파일 설정 및 Foundry 요청/응답 계약 모듈입니다.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from zerostreet_schema.enums import HorizonMaskMode, SubscriptionTier


class RLRewardWeights(BaseModel):
    """User-supplied differentiable trajectory RL objective weights (at least one > 0).

    사용자가 직접 지정하는 미분 가능 궤적 RL 목적함수 가중치(최소 1개 이상 양수 필수)입니다.
    """

    excess_return_20: float = Field(default=0.0, ge=0.0)
    return_20: float = Field(default=0.0, ge=0.0)
    fip_return_20: float = Field(default=0.0, ge=0.0)
    sortino_20: float = Field(default=0.0, ge=0.0)
    sharpe_20: float = Field(default=0.0, ge=0.0)
    information_ratio_20: float = Field(default=0.0, ge=0.0)
    active_sortino_20: float = Field(default=0.0, ge=0.0)
    cvar_20: float = Field(default=0.0, ge=0.0)
    mdd_20: float = Field(default=0.0, ge=0.0)
    vol_20: float = Field(default=0.0, ge=0.0)
    max_weight_limit: float = Field(default=0.0, ge=0.0)
    quadratic_turnover_coeff: float = Field(default=0.0, ge=0.0)

    @model_validator(mode="after")
    def _validate_non_zero_objective(self) -> "RLRewardWeights":
        objective_total = (
            self.excess_return_20
            + self.return_20
            + self.fip_return_20
            + self.sortino_20
            + self.sharpe_20
            + self.information_ratio_20
            + self.active_sortino_20
            + self.cvar_20
            + self.mdd_20
            + self.vol_20
        )
        if objective_total <= 0.0:
            raise ValueError(
                "RLRewardWeights requires at least one positive (> 0) objective weight."
            )
        return self


class UserPolicyConfig(BaseModel):
    """Mandatory user-supplied configuration for Policy Head compilation.

    사용자 에이전트가 반드시 명시적으로 공급해야 하는 Policy Head 컴파일 설정입니다.
    """

    target_universe: list[str] = Field(
        min_length=2,
        description="투자 대상 자산 심볼 목록 (예: ['ASSET_A', 'ASSET_B', 'CASH'], 최소 2개 필수)",
    )
    rl_reward_weights: RLRewardWeights
    portfolio_horizon: int = Field(default=20, ge=1, le=64)
    horizon_mask_mode: HorizonMaskMode = Field(default=HorizonMaskMode.BIDIRECTIONAL_PORTFOLIO)
    weights_output_mode: Literal["entmax15", "sparsemax", "softmax"] = Field(default="entmax15")
    max_single_weight: float = Field(default=0.60, gt=0.0, le=1.0)
    benchmark_asset: str | None = Field(default=None, description="초과수익/IR 계산용 벤치마크 심볼")

    @field_validator("target_universe")
    @classmethod
    def _validate_unique_universe(cls, universe: list[str]) -> list[str]:
        cleaned = [symbol.strip() for symbol in universe if symbol.strip()]
        if len(cleaned) < 2:
            raise ValueError("target_universe must contain at least 2 non-empty asset symbols.")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("target_universe must not contain duplicate asset symbols.")
        return cleaned


class PolicyCompileRequest(BaseModel):
    """Request payload for AlphaSmith Serverless RL Foundry compilation.

    AlphaSmith Serverless RL Foundry 컴파일 요청 스키마입니다.
    """

    user_id: str = Field(min_length=1)
    tier: SubscriptionTier = Field(default=SubscriptionTier.SOVEREIGN_PRO)
    policy_config: UserPolicyConfig
    backbone_version: str = Field(default="zerosteer-backbone-v1")
    multimodal_tensor_version: str = Field(default="zerolens_v2_mrl")
    compile_steps: int = Field(default=20, ge=1, le=2000)


class PolicyCompileResult(BaseModel):
    """Completed result schema from AlphaSmith Foundry policy compilation.

    AlphaSmith Foundry 컴파일 완료 결과 스키마입니다.
    """

    job_id: str = Field(min_length=1)
    policy_checkpoint_id: str = Field(min_length=1)
    status: Literal["QUEUED", "RUNNING", "COMPLETED", "FAILED"]
    checkpoint_sha256: str | None = None
    artifact_uri: str | None = None
    compiled_at: datetime | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
