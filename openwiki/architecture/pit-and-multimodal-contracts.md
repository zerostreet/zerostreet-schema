---
type: architecture-contract
title: Point-in-Time 검증 및 멀티모달 임베딩 스키마
description: 3중 타임스탬프 기반 시점 누수 차단 불변식과 구독 티어별 Matryoshka 임베딩(z_mm) 및 적법 원천 데이터 계약을 설명합니다.
tags: [point-in-time, lookahead-bias, multimodal, mrl, pydantic-v2, opendart]
verified:
  - by: openwiki/0.7.2
    at: 2026-11-21T17:03:53.516Z
sources:
  - id: openwiki-source-8b0ea8a07e0fe75e78ef57fa
    resource: repo://src/zerostreet_schema/enums.py
  - id: openwiki-source-96119d5ee85bb3ffcff11d7a
    resource: repo://src/zerostreet_schema/multimodal.py
  - id: openwiki-source-6ed392b0a2f19b4525ae93d8
    resource: repo://src/zerostreet_schema/pit.py
generated: { by: "antigravity", at: "2026-11-21T17:03:53.516Z" }
---

# Point-in-Time 검증 및 멀티모달 임베딩 스키마

`zerostreet-schema`는 ZeroStreet 생태계 전체에서 미래 참조(Look-Ahead Bias)를 차단하고 `AlphaSmith(Model A)`가 생성한 멀티모달 임베딩(`z_mm`)과 적법 원천 데이터를 `HyperAlpha-VLA(Model B)` 및 `AlphaGraph`로 안전하게 전달하기 위한 Pydantic v2 데이터 계약을 정의합니다.

---

## 1. Point-in-Time 3중 타임스탬프 불변식 (`pit.py`)

모든 시점 민감 타임스탬프는 반드시 `tzinfo`가 포함된 timezone-aware `datetime`이어야 하며, 순수(naive) 시각이 들어오면 `ensure_timezone_aware`가 즉시 `PointInTimeError(ValueError)`를 발생시킵니다.

```text
event_ts (사건/결산 기준일)  <=  published_ts (외부 공시·발표 시각)  <=  available_ts (모델 투입 가능 시각)  <=  as_of_ts (추론 기준 시각)
```

| 구성 요소 | 역할 및 검증 규칙 | 실패 시 동작 |
| :--- | :--- | :--- |
| **`PointInTimeStamp`** | `event_ts <= published_ts <= available_ts` 3중 시간 순서 검증 | `PointInTimeError` (`ValidationError` 래핑) |
| **`assert_no_lookahead`** | 개별 레코드 `available_ts <= as_of_ts` 단언 | `PointInTimeError` 직접 발생 |
| **`filter_pit_records`** | 배치 내 `available_ts <= as_of_ts` 조건을 만족하는 관측 가능 레코드만 추출 | 미래 레코드 자동 배제 |

---

## 2. 구독 티어별 MRL 차원 및 원천 데이터 소스 정책 (`enums.py`)

`SubscriptionTier`에 따라 `allowed_embedding_dims`가 허용하는 Matryoshka Representation Learning(MRL) 임베딩 차원과 재배포 가능한 원천 데이터 소스(`AllowedDataSource`)가 결정됩니다.

| 구독 티어 (`SubscriptionTier`) | 허용 `embedding_dim` | 비고 |
| :--- | :--- | :--- |
| **`developer`** | `{0, 32}` | 로컬 수치(OHLCV) 블랙아웃 모드(`0`) 또는 기본 32차원 요약 |
| **`sovereign_pro`** | `{0, 32, 128}` | 중차원 멀티모달 임베딩(`128d`) + 공시/AI 팩트 |
| **`founding_100`** | `{0, 32, 128}` | Sovereign Pro와 동일한 128차원 권한 |
| **`alpha_ultra`** | `{0, 32, 128, 256}` | 풀 256차원 멀티모달 임베딩 및 거시/선물 데이터 |

재배포 및 저작권 리스크 차단을 위해 `PublicFilingItem` 및 `MacroContextPayload`는 `AllowedDataSource`(`OpenDART`, `SEC_EDGAR`, `BOK_ECOS`, `FRED`, `BOK_ECOS_FRED`, `PUBLIC_EXCHANGE`, `AI_EXTRACTED_FACTS`)만 허용합니다.

---

## 3. 멀티모달 배치 계약 (`multimodal.py`)

<!-- openwiki: mermaid parse failed and this diagram was converted to a text fence so it does not break rendering. Fix the diagram source and restore the mermaid fence. Parser error: Heuristic: an unescaped angle bracket inside a label breaks rendering; rephrase the label. -->
```text
flowchart LR
    BATCH["MultimodalFeatureBatch (as_of_ts, tier, embedding_dim)"] --> TIER_CHK["allowed_embedding_dims(tier) 검증"]
    BATCH --> ITEMS["AssetEmbeddingItem[] 순회"]
    ITEMS --> PIT_ITEM["assert_no_lookahead(item.available_ts, as_of_ts)"]
    ITEMS --> PIT_FILING["PublicFilingItem별 available_ts/published_ts <= as_of_ts"]
    ITEMS --> BLACKOUT{"is_blackout 여부"}
    BLACKOUT -- "False" --> DIM_CHK["len(embedding_z_mm) == embedding_dim 및 유한 실수 검증"]
    BLACKOUT -- "True" --> PASS["빈 벡터 허용 (Model B [MASK_SIGNAL] 폴백)"]
```

- **결측(Blackout) 안전성**: `AssetEmbeddingItem.is_blackout=True`이면 `embedding_z_mm`가 빈 리스트여도 유효하며, `HyperAlpha-VLA`의 `DynamicEmbeddingAdapter`가 학습된 `[MASK_SIGNAL]` 토큰으로 폴백합니다. 반면 `is_blackout=False`이면 `len(embedding_z_mm) == embedding_dim`과 모든 원소의 유한성(`math.isfinite`)을 엄격히 강제합니다.
- **중첩 공시 시점 검증**: `MultimodalFeatureBatch`는 최상위 `item.available_ts`뿐만 아니라 내부 `source_data.public_filings`의 각 공시(`filing.available_ts or filing.published_ts`)까지 `as_of_ts` 이전인지 재귀적으로 검사합니다.

---

## 4. 단위 테스트 검증 범위

<!-- openwiki: broken internal link [../tests/test_pit.py] file "../tests/test_pit.py" does not exist. Fix the href or restore the target, then delete this comment. -->
- [test_pit.py](../tests/test_pit.py): 3중 타임스탬프 순서 역전 및 naive datetime 거부, `assert_no_lookahead` 경계 조건, `filter_pit_records` 필터링을 검증합니다.
<!-- openwiki: broken internal link [../tests/test_multimodal.py] file "../tests/test_multimodal.py" does not exist. Fix the href or restore the target, then delete this comment. -->
- [test_multimodal.py](../tests/test_multimodal.py): 티어-차원 불일치(`developer` + `128d`) 차단, 미래 `available_ts` 배치 차단, `is_blackout=True` 허용 및 `NaN` 원소 차단을 검증합니다.
