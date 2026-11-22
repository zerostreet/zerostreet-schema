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


class EntityType(StrEnum):
    """First-class financial target unit processed by ZeroLens and served via AlphaSmith.

    ZeroLens가 정보를 처리·압축하고 AlphaSmith가 서빙하는 금융 객체 단위 열거형입니다.
    """

    EQUITY = "equity"
    INDEX = "index"
    MACRO = "macro"
    SECTOR = "sector"
    FUTURES = "futures"


_LEGACY_ENTITY_ALIASES: dict[str, EntityType] = {
    "asset": EntityType.EQUITY,
    "market_index": EntityType.INDEX,
}


def normalize_entity_type(value: EntityType | str) -> EntityType:
    """Normalize an EntityType enum or case-insensitive/legacy alias into EntityType.

    EntityType 열거형이나 대소문자·레거시 별칭('asset', 'market_index')을 정규화합니다.
    """
    if isinstance(value, EntityType):
        return value
    raw = str(value).strip().lower()
    if raw in _LEGACY_ENTITY_ALIASES:
        return _LEGACY_ENTITY_ALIASES[raw]
    try:
        return EntityType(raw)
    except ValueError as exc:
        valid = ", ".join(et.value for et in EntityType)
        raise ValueError(
            f"Unknown entity_type={value!r}. Expected one of: {valid}."
        ) from exc


def infer_entity_type(entity_id: str) -> EntityType:
    """Infer target EntityType from standardized symbol prefixes (IDX/MACRO/FX/SEC/FUT).

    표준 심볼 접두어(IDX:/MACRO:/FX:/SEC:/SECTOR:/FUT:)로부터 객체 단위를 추론합니다.
    """
    upper = entity_id.strip().upper()
    if upper.startswith("IDX:"):
        return EntityType.INDEX
    if upper.startswith(("MACRO:", "FX:")):
        return EntityType.MACRO
    if upper.startswith(("SEC:", "SECTOR:")):
        return EntityType.SECTOR
    if upper.startswith("FUT:"):
        return EntityType.FUTURES
    return EntityType.EQUITY


def default_modalities_for_entity(entity_type: EntityType | str) -> dict[str, bool]:
    """Return default 5-modality availability flags conditioned on EntityType.

    객체 단위(EntityType)별 기본 5대 모달리티(ts/filing/macro/fact/text) 가용 맵을
    반환합니다.
    """
    resolved = normalize_entity_type(entity_type)
    has_filing = resolved in {EntityType.EQUITY, EntityType.SECTOR}
    return {
        "ts": True,
        "filing": has_filing,
        "macro": True,
        "fact": True,
        "text": True,
    }
