from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from zerostreet_schema import (
    DaemonStatus,
    KillCriterion,
    RunTrace,
    RunTraceRef,
    SourceFactsSnapshot,
    ThesisManifest,
)


def test_run_trace_zero_trust_valid_and_blocks_secrets():
    trace = RunTrace(
        run_id="run_20261122_090500",
        policy_checkpoint_id="usr_ckpt_v4_cvar10",
        multimodal_tensor_version="zerolens_v2_mrl",
        daemon_status=DaemonStatus.COMPLETED,
        positions_weights={"005930.KS": 0.25, "SPY": 0.45, "TLT": 0.30},
        target_vs_filled_diff_bps={"005930.KS": -1.2, "SPY": 0.4, "TLT": -0.8},
        execution_slippage_bps=2.4,
        guardrail_checks_passed=True,
        hitl_approved_latency_sec=14.2,
    )
    assert trace.guardrail_checks_passed is True

    # extra="forbid" blocks unknown fields such as total_krw or account_number
    with pytest.raises(ValidationError):
        RunTrace(
            run_id="run_bad",
            policy_checkpoint_id="ckpt_1",
            daemon_status=DaemonStatus.COMPLETED,
            guardrail_checks_passed=True,
            total_krw=50000000,
        )

    # Rejects sensitive keys inside positions_weights
    with pytest.raises(ValidationError, match="Forbidden sensitive key"):
        RunTrace(
            run_id="run_bad_key",
            policy_checkpoint_id="ckpt_1",
            daemon_status=DaemonStatus.COMPLETED,
            positions_weights={"kis_app_key": 0.5, "CASH": 0.5},
            guardrail_checks_passed=True,
        )

    # Rejects portfolio sum > 1.0001
    with pytest.raises(ValidationError, match="Sum of positions_weights"):
        RunTrace(
            run_id="run_bad_sum",
            policy_checkpoint_id="ckpt_1",
            daemon_status=DaemonStatus.COMPLETED,
            positions_weights={"ASSET_A": 0.7, "ASSET_B": 0.6},
            guardrail_checks_passed=True,
        )


def test_thesis_manifest_v2_valid():
    now_ts = datetime(2026, 11, 22, 8, 30, tzinfo=UTC)
    manifest = ThesisManifest(
        generated_at=now_ts,
        ticker="KRX:005930",
        corp_name="삼성전자",
        run_trace_ref=RunTraceRef(
            run_id="run_20261122_090500",
            policy_checkpoint_id="usr_ckpt_v4_cvar10",
            multimodal_tensor_version="zerolens_v2_mrl",
            target_weight_delta=0.045,
        ),
        source_facts_snapshot=SourceFactsSnapshot(
            available_ts=now_ts,
            event_tags=["EARNINGS_BEAT"],
            guidance_tone_score=0.68,
            risk_flag_score=0.12,
        ),
        core_fact_summary=["영업이익률 전분기 대비 개선(+145bps)"],
        devils_advocate_risks=["환율 변동성 확대 시 외국인 매물 출회 가능성"],
        quantitative_kill_criteria=[
            KillCriterion(
                metric="foreign_net_buy_zscore_20d",
                operator="<=",
                threshold=-1.0,
                description="외국인 20일 수급 강도 Z-Score 반전 시 재검토",
            )
        ],
    )
    assert manifest.schema_version == "2.0"
