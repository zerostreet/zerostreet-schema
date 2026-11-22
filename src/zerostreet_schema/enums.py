"""Shared ZeroStreet enumerations and subscription-tier policies.

ZeroStreet 공통 열거형 및 과금 티어 정책 모듈입니다.
"""

from enum import StrEnum


class SubscriptionTier(StrEnum):
    """ZeroStreet B2A subscription tier enumeration.

    ZeroStreet 서비스 구독 티어 열거형입니다.
    """

    DEVELOPER = "developer"
    SOVEREIGN_PRO = "sovereign_pro"
    ALPHA_ULTRA = "alpha_ultra"
    FOUNDING_100 = "founding_100"


_TIER_EMBEDDING_DIMS: dict[SubscriptionTier, frozenset[int]] = {
    SubscriptionTier.DEVELOPER: frozenset({0, 32}),
    SubscriptionTier.SOVEREIGN_PRO: frozenset({0, 32, 128}),
    SubscriptionTier.FOUNDING_100: frozenset({0, 32, 128}),
    SubscriptionTier.ALPHA_ULTRA: frozenset({0, 32, 128, 256}),
}


def allowed_embedding_dims(tier: SubscriptionTier | str) -> frozenset[int]:
    """Return allowed Matryoshka (MRL) embedding dimensions for a tier.

    구독 티어에서 허용되는 MRL 임베딩 차원 집합을 반환합니다.
    """
    resolved = SubscriptionTier(tier)
    return _TIER_EMBEDDING_DIMS[resolved]


class AllowedDataSource(StrEnum):
    """Whitelisted data sources verified for lawful redistribution.

    저작권 및 재배포 적법성이 검증된 허용 원천 데이터 소스입니다.
    """

    OPENDART = "OpenDART"
    SEC_EDGAR = "SEC_EDGAR"
    BOK_ECOS = "BOK_ECOS"
    FRED = "FRED"
    BOK_ECOS_FRED = "BOK_ECOS_FRED"
    PUBLIC_EXCHANGE = "PUBLIC_EXCHANGE"
    AI_EXTRACTED_FACTS = "AI_EXTRACTED_FACTS"


class DaemonStatus(StrEnum):
    """Termination states for the local AlphaGraph execution daemon.

    AlphaGraph 로컬 실행 데몬의 종료 상태 열거형입니다.
    """

    COMPLETED = "COMPLETED"
    BLOCKED_BY_GUARDRAIL = "BLOCKED_BY_GUARDRAIL"
    REJECTED_BY_HITL = "REJECTED_BY_HITL"
    KILLED = "KILLED"
    FAILED = "FAILED"


class HorizonMaskMode(StrEnum):
    """Attention masking modes across multi-horizon portfolio blocks in HyperAlpha-VLA.

    HyperAlpha-VLA 다기간 포트폴리오 블록 간 어텐션 마스킹 모드입니다.
    """

    BIDIRECTIONAL_PORTFOLIO = "bidirectional_portfolio"
    CAUSAL_PORTFOLIO = "causal_portfolio"
    BACKWARD_DP = "backward_dp"
