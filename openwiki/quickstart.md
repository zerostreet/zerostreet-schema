---
type: quickstart
title: zerostreet-schema Quickstart & Business Overview / zerostreet-schema 빠른 시작 및 비즈니스 개요
description: Introduces the Layer 0 business role, package structure, local validation, and OpenWiki routing map for zerostreet-schema. ZeroStreet 생태계의 표준 Pydantic v2 계약 패키지인 zerostreet-schema의 비즈니스 역할, 구조, 검증 절차 및 문서 맵을 안내합니다.
tags:
  - quickstart
  - zerostreet-schema
  - pydantic-v2
  - contracts
  - business-context
  - zerolens
verified:
  - by: openwiki/0.7.2
    at: 2026-11-22T09:05:44.650Z
sources:
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-ff9f237687ae6937ad228647
    resource: repo://src/zerostreet_schema/__init__.py
generated: { by: "antigravity", at: "2026-11-22T09:05:44.650Z" }
---

# zerostreet-schema Quickstart & Business Overview / 빠른 시작 및 비즈니스 개요

`zerostreet-schema` (`v0.1.0`, MIT) is the Layer 0 Pydantic v2 contract package shared across the entire **ZeroStreet (`주식회사 제로스트리트`)** stack (`zerostreet-models`, `hyperalpha-vla`, `alphagraph`, `alphasmith`, and `zerostreet-skills`).

`zerostreet-schema` (`v0.1.0`, MIT)는 **ZeroStreet (`주식회사 제로스트리트`)** 생태계 전체가 공유하는 Layer 0 표준 Pydantic v2 데이터 계약 패키지입니다.

---

## Business Role & Value Proposition / 비즈니스 역할 및 가치

### English

* **Universal Trust & Billing Boundary (Layer 0)**: Acts as the zero-weight open-source constitution connecting MIT client software (`alphagraph`, `hyperalpha-vla`, `zerostreet-skills`) to ZeroStreet's paid B2A cloud (`alphasmith`, `zerostreet-models`).
* **MRL Subscription Tier Monetization**: `SubscriptionTier` + `allowed_embedding_dims()` directly ties pricing tiers (`developer: 0/32d`, `sovereign_pro & founding_100: 0/32/128d`, `alpha_ultra: 0/32/128/256d`) to Matryoshka tensor dimensions, enabling tiered SaaS/B2A revenue over one upstream encoder.
* **Regulatory & Custody Shield**: `PointInTimeStamp` prevents look-ahead leakage, `RLRewardWeights` requires user-supplied non-zero objectives (eliminating unlicensed advisory defaults), and `RunTrace` (`extra="forbid"`) blocks brokerage secrets from leaving local custody.

### 한국어

* **오픈소스 클라이언트와 유료 클라우드를 잇는 Layer 0 신뢰·과금 계약**: MIT 공개 패키지와 유료 B2A 컨트롤 플레인(`alphasmith`, `zerostreet-models`)이 동일한 스키마 불변식을 공유하도록 보장합니다.
* **MRL 구독 티어 과금 모델 구현**: `SubscriptionTier`와 `allowed_embedding_dims()`로 티어별 허용 임베딩 차원(`0/32/128/256d`)을 강제하여 단일 인코더 기반의 계단식 B2A 수익화를 뒷받침합니다.
* **규제·보안 방화벽 내장**: `PointInTimeStamp`는 시점 누수를 차단하고, `RLRewardWeights`는 사용자 직접 목적함수 명시를 강제하며, `RunTrace`는 계좌·시크릿 유출을 원천 봉쇄합니다.

---

## 1. Documentation Routing Map / 작업별 문서 라우팅 맵

| Topic / 탐색 주제 | Document Path / 문서 경로 | Summary / 핵심 내용 |
| :--- | :--- | :--- |
| **PIT Validation & Multimodal Contracts / 시점 누수 방지 & 멀티모달 스키마** | [Point-in-Time Validation & Multimodal Contracts](./architecture/pit-and-multimodal-contracts.md) | Triple timestamps (`PointInTimeStamp`), `assert_no_lookahead`, tier MRL dims (`0/32/128/256`), `MultimodalFeatureBatch` / 3중 타임스탬프, 티어별 차원 및 배치 계약 |
| **Policy & Zero-Trust Telemetry / 정책 컴파일 & 제로 트러스트 텔레메트리** | [Policy Compilation & Zero-Trust Telemetry Contracts](./architecture/policy-and-telemetry-contracts.md) | `RLRewardWeights`, `UserPolicyConfig`, `RunTrace` (`extra="forbid"`), `ThesisManifest` `v2.0` / 사용자 정책, 금지 키 차단, 리서치 매니페스트 |

---

## 2. Package Modules / 패키지 모듈 구조 (`src/zerostreet_schema/`)

| Module / 모듈 | Key Exports / 주요 공개 심볼 | Role / 역할 |
| :--- | :--- | :--- |
| `enums.py` | `SubscriptionTier`, `allowed_embedding_dims`, `AllowedDataSource`, `DaemonStatus`, `HorizonMaskMode`, `EntityType`, `normalize_entity_type`, `infer_entity_type`, `default_modalities_for_entity` | Tiers, lawful sources, processing units (`equity`/`index`/`macro`/`sector`/`futures`), daemon status, mask modes / 구독 티어, 적법 소스, 객체 단위, 데몬 상태 및 마스킹 |
| `pit.py` | `PointInTimeError`, `PointInTimeStamp`, `ensure_timezone_aware`, `assert_no_lookahead`, `filter_pit_records` | Triple-timestamp look-ahead enforcement / 3중 타임스탬프 및 시점 누수 검증 |
| `multimodal.py` | `PublicFilingItem`, `MacroContextPayload`, `AIExtractedFactsPayload`, `SourceDataPayload`, `AssetEmbeddingItem`, `MultimodalFeatureBatch` | `ZeroLens -> Model B` tensor (`zerolens_v2_mrl`), `entity_types`, and source contracts / 임베딩(`z_mm`), 객체 단위 목록 및 원천 데이터 계약 |
| `policy.py` | `RLRewardWeights`, `UserPolicyConfig`, `PolicyCompileRequest`, `PolicyCompileResult` | Custom Policy Head compile config & jobs / 개별 Policy Head 컴파일 요청/응답 |
| `telemetry.py` | `FORBIDDEN_SECRET_FIELDS`, `RunTrace`, `KillCriterion`, `RunTraceRef`, `SourceFactsSnapshot`, `ThesisManifest` | Zero-trust execution trace & `alpha-wiki` manifest / 제로 트러스트 추적 및 매니페스트 |

---

## 3. Installation & Local Verification / 설치 및 로컬 검증 절차

`pyproject.toml` uses the `hatchling` backend and `uv` with `[dependency-groups]` (`pytest`, `ruff`). Downstream ZeroStreet repositories consume this package via editable `[tool.uv.sources]` (`path = "../zerostreet-schema"`).

`pyproject.toml`은 `hatchling` 빌드 백엔드와 `uv` 기반 개발 의존성을 사용하며, 모든 하위 저장소가 동일한 계약을 편집 가능 의존성으로 공유합니다.

```bash
uv sync --dev
uv run ruff check .
uv run pytest -q
```
