from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from zerostreet_schema import (
    AIExtractedFactsPayload,
    AllowedDataSource,
    AssetEmbeddingItem,
    MacroContextPayload,
    MultimodalFeatureBatch,
    PublicFilingItem,
    SourceDataPayload,
    SubscriptionTier,
)


def test_multimodal_feature_batch_valid():
    as_of = datetime(2026, 11, 21, 8, 30, tzinfo=UTC)
    pub_ts = datetime(2026, 11, 14, 16, 10, tzinfo=UTC)
    avail_ts = datetime(2026, 11, 21, 7, 50, tzinfo=UTC)

    item = AssetEmbeddingItem(
        asset_id="KRX:005930",
        available_ts=avail_ts,
        is_blackout=False,
        embedding_z_mm=[0.01] * 128,
        source_data=SourceDataPayload(
            public_filings=[
                PublicFilingItem(
                    source=AllowedDataSource.OPENDART,
                    filing_id="20261114000123",
                    title="분기보고서 (2026.09)",
                    published_ts=pub_ts,
                    key_metrics={"op_margin_qoq_bps": 145},
                )
            ],
            macro_context=MacroContextPayload(us10y_2y_spread_bps=24.5, krw_usd_20d_zscore=1.12),
            ai_extracted_facts=AIExtractedFactsPayload(
                event_tags=["EARNINGS_BEAT"],
                guidance_tone_score=0.68,
                risk_flag_score=0.12,
                agent_brief_ko="3분기 영업이익률 개선 공시 확인",
            ),
        ),
    )
    batch = MultimodalFeatureBatch(
        as_of_ts=as_of,
        tier=SubscriptionTier.SOVEREIGN_PRO,
        embedding_dim=128,
        items=[item],
    )
    assert batch.embedding_dim == 128
    assert len(batch.items) == 1


def test_multimodal_rejects_tier_dim_mismatch_and_lookahead():
    as_of = datetime(2026, 11, 21, 8, 30, tzinfo=UTC)

    with pytest.raises(ValidationError, match="not allowed for tier"):
        MultimodalFeatureBatch(
            as_of_ts=as_of,
            tier=SubscriptionTier.DEVELOPER,
            embedding_dim=128,
            items=[],
        )

    with pytest.raises(ValidationError, match="Look-ahead bias"):
        MultimodalFeatureBatch(
            as_of_ts=as_of,
            tier=SubscriptionTier.ALPHA_ULTRA,
            embedding_dim=256,
            items=[
                AssetEmbeddingItem(
                    asset_id="KRX:005930",
                    available_ts=as_of + timedelta(minutes=5),
                    is_blackout=False,
                    embedding_z_mm=[0.1] * 256,
                )
            ],
        )


def test_multimodal_allows_blackout_empty_embedding_and_rejects_nan():
    as_of = datetime(2026, 11, 21, 8, 30, tzinfo=UTC)
    batch = MultimodalFeatureBatch(
        as_of_ts=as_of,
        tier=SubscriptionTier.SOVEREIGN_PRO,
        embedding_dim=128,
        items=[
            AssetEmbeddingItem(
                asset_id="KRX:000660",
                available_ts=as_of,
                is_blackout=True,
                embedding_z_mm=[],
            )
        ],
    )
    assert batch.items[0].is_blackout is True

    with pytest.raises(ValidationError, match="finite"):
        AssetEmbeddingItem(
            asset_id="KRX:000660",
            available_ts=as_of,
            embedding_z_mm=[float("nan")],
        )
