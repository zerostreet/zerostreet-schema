import pytest
from pydantic import ValidationError

from zerostreet_schema import (
    HorizonMaskMode,
    PolicyCompileRequest,
    RLRewardWeights,
    SubscriptionTier,
    UserPolicyConfig,
)


def test_user_policy_config_valid():
    cfg = UserPolicyConfig(
        target_universe=["ASSET_A", "ASSET_B", "CASH"],
        rl_reward_weights=RLRewardWeights(
            excess_return_20=0.5,
            cvar_20=1.5,
            mdd_20=1.0,
            quadratic_turnover_coeff=0.3,
        ),
        portfolio_horizon=20,
        horizon_mask_mode=HorizonMaskMode.BIDIRECTIONAL_PORTFOLIO,
    )
    assert cfg.portfolio_horizon == 20
    req = PolicyCompileRequest(
        user_id="usr_01",
        tier=SubscriptionTier.SOVEREIGN_PRO,
        policy_config=cfg,
    )
    assert req.policy_config.target_universe == ["ASSET_A", "ASSET_B", "CASH"]


def test_user_policy_config_rejects_invalid_universe_or_zero_weights():
    with pytest.raises(ValidationError, match="at least one positive"):
        RLRewardWeights(quadratic_turnover_coeff=0.2)

    with pytest.raises(ValidationError, match="duplicate"):
        UserPolicyConfig(
            target_universe=["ASSET_A", "ASSET_A"],
            rl_reward_weights=RLRewardWeights(sortino_20=1.0),
        )

    with pytest.raises(ValidationError):
        UserPolicyConfig(
            target_universe=["ONLY_ONE"],
            rl_reward_weights=RLRewardWeights(sortino_20=1.0),
        )
