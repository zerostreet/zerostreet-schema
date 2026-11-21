---
type: quickstart
title: zerostreet-schema 빠른 시작 및 아키텍처 맵
description: ZeroStreet 생태계의 표준 Pydantic v2 계약 패키지인 zerostreet-schema의 구조, 설치/검증 절차 및 상세 아키텍처 문서 경로를 안내합니다.
tags: [quickstart, zerostreet-schema, pydantic-v2, contracts, uv]
verified:
  - by: openwiki/0.7.2
    at: 2026-11-21T17:03:53.516Z
sources:
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-ff9f237687ae6937ad228647
    resource: repo://src/zerostreet_schema/__init__.py
generated: { by: "antigravity", at: "2026-11-21T17:03:53.516Z" }
---

# zerostreet-schema 빠른 시작 및 아키텍처 맵

`zerostreet-schema` (`v0.1.0`, MIT)는 **ZeroStreet (`주식회사 제로스트리트`)** 생태계 전체(`hyperalpha-vla`, `alphagraph`, `alphasmith`, `zerostreet-skills`)가 공유하는 표준 Pydantic v2 데이터 계약 패키지입니다. 시점 누수(Look-Ahead Bias) 차단, 티어별 Matryoshka 멀티모달 임베딩 차원 정책, 사용자 개별 RL 정책 컴파일 스키마, 제로 트러스트 텔레메트리를 단일 패키지로 제공합니다.

---

## 1. 작업별 문서 라우팅 맵

| 탐색 주제 | 문서 경로 | 핵심 내용 |
| :--- | :--- | :--- |
| **시점 누수 방지 & 멀티모달 스키마** | [Point-in-Time 검증 및 멀티모달 임베딩 스키마](architecture/pit-and-multimodal-contracts.md) | 3중 타임스탬프(`PointInTimeStamp`), `assert_no_lookahead`, `SubscriptionTier`별 MRL 차원(`0/32/128/256`), `MultimodalFeatureBatch` |
| **정책 컴파일 & 제로 트러스트 텔레메트리** | [사용자 정책 계약 및 제로트러스트 텔레메트리 스키마](architecture/policy-and-telemetry-contracts.md) | `RLRewardWeights`, `UserPolicyConfig`, `RunTrace` (`extra="forbid"` & 금지 키), `ThesisManifest` `v2.0` |

---

## 2. 패키지 모듈 구조 (`src/zerostreet_schema/`)

| 모듈 | 주요 공개 심볼 | 역할 |
| :--- | :--- | :--- |
| `enums.py` | `SubscriptionTier`, `allowed_embedding_dims`, `AllowedDataSource`, `DaemonStatus`, `HorizonMaskMode` | 구독 티어, 적법 원천 데이터 소스, 데몬 상태 및 어텐션 마스킹 열거형 |
| `pit.py` | `PointInTimeError`, `PointInTimeStamp`, `ensure_timezone_aware`, `assert_no_lookahead`, `filter_pit_records` | 3중 타임스탬프 및 `available_ts <= as_of_ts` 시점 누수 검증 |
| `multimodal.py` | `PublicFilingItem`, `MacroContextPayload`, `AIExtractedFactsPayload`, `SourceDataPayload`, `AssetEmbeddingItem`, `MultimodalFeatureBatch` | `Model A -> Model B` 임베딩(`z_mm`) 및 정제 원천 데이터 계약 |
| `policy.py` | `RLRewardWeights`, `UserPolicyConfig`, `PolicyCompileRequest`, `PolicyCompileResult` | 사용자 개별 Policy Head 컴파일 설정 및 요청/응답 |
| `telemetry.py` | `FORBIDDEN_SECRET_FIELDS`, `RunTrace`, `KillCriterion`, `RunTraceRef`, `SourceFactsSnapshot`, `ThesisManifest` | 제로 트러스트 실행 추적 및 `alpha-wiki` 매니페스트 |

---

## 3. 설치 및 로컬 검증 절차

`pyproject.toml`은 `hatchling` 빌드 백엔드와 `uv` 기반 `dependency-groups.dev`(`pytest`, `ruff`)를 사용합니다.

```bash
uv sync --dev
uv run ruff check .
uv run pytest -q
```

다른 ZeroStreet 하위 리포지토리(`hyperalpha-vla`, `alphagraph`, `alphasmith`, `zerostreet-skills`)에서는 `[tool.uv.sources]`의 로컬 editable 경로(`path = "../zerostreet-schema"`)를 통해 동일한 스키마 계약을 공유합니다.
