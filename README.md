# zerostreet-schema (`Public · MIT · Layer 0`)

Shared Pydantic v2 data contracts and Point-in-Time look-ahead validators for the entire ZeroStreet ecosystem (`ZeroSteer`, `AlphaGraph`, `AlphaSmith`, `zerostreet-models`, and `ZeroStreet Architect Skills`).

`주식회사 제로스트리트(ZeroStreet)` 전 계층이 공유하는 **Pydantic v2 표준 데이터 계약 및 Point-in-Time 시점 누수 차단 라이브러리**입니다.

---

## Business Role & Value Proposition / 비즈니스 역할 및 가치

### English

* **Universal Trust & Billing Boundary (Layer 0)**: Acts as the zero-weight open-source constitution connecting MIT client software (`alphagraph`, `zerosteer`, `zerostreet-skills`) to ZeroStreet's paid B2A cloud (`alphasmith`, `zerostreet-models`). Every downstream API payload, embedding slice, and telemetry report is schema-validated on the client before crossing network or custody boundaries.
* **MRL Subscription Tier Monetization**: `SubscriptionTier` + `allowed_embedding_dims()` cryptographically/programmatically binds pricing tiers (`developer: 0/32d`, `sovereign_pro & founding_100: 0/32/128d`, `alpha_ultra: 0/32/128/256d`) to Matryoshka Representation Learning (MRL) tensor dimensions, allowing one upstream encoder to monetize progressive signal fidelity.
* **Regulatory & Institutional Compliance Shield**:
  * **Zero Look-Ahead Integrity**: `PointInTimeStamp` and `assert_no_lookahead()` mathematically separate `event_ts <= published_ts <= available_ts <= as_of_ts`, giving B2A agents and researchers audit-grade protection against future data leakage.
  * **Non-Advisory Guarantee**: `RLRewardWeights` and `UserPolicyConfig` reject empty/all-zero objectives so every strategy originates from the customer's own reward specification rather than a vendor default.
  * **Zero-Trust Custody Firewall**: `RunTrace` (`extra="forbid"`) explicitly rejects brokerage account numbers, KIS keys, and KRW balance amounts so sensitive credentials never leave the user's local machine.

### 한국어

* **오픈소스 클라이언트와 유료 클라우드를 잇는 Layer 0 신뢰·과금 표준 계약**: MIT 공개 패키지(`alphagraph`, `zerosteer`, `zerostreet-skills`)와 유료 컨트롤 플레인(`alphasmith`, `zerostreet-models`) 사이의 단일 진실 공급원(Single Source of Truth)입니다.
* **MRL 구독 티어 과금 체계 강제**: `SubscriptionTier`와 `allowed_embedding_dims()`가 요금제별(`developer: 0/32d`, `sovereign_pro·founding_100: 0/32/128d`, `alpha_ultra: 0/32/128/256d`) 임베딩 차원을 스키마 단계에서 통제하여, 단일 인코더 기반의 계단식(Tiered) B2A 과금을 가능하게 합니다.
* **규제·보안 방화벽 내장**:
  * **시점 누수 차단**: `event_ts <= published_ts <= available_ts <= as_of_ts` 3중 타임스탬프 불변식으로 백테스트-실전 괴리를 원천 차단합니다.
  * **자본시장법 비투자자문 원칙 강제**: `RLRewardWeights`는 최소 1개 이상의 양수 목적함수 가중치를 요구해 회사 기본 전략 배포를 원천 불가능하게 만듭니다.
  * **제로 트러스트 보안**: `RunTrace`(`extra="forbid"`)가 계좌번호·API 키·원화 예수금 필드를 거부하여 고객 자산 정보가 클라우드로 유출되지 않도록 방어합니다.

---

## Core Modules / 핵심 제공 모듈

1. **Point-in-Time Validators (`pit.py`)**: `PointInTimeStamp`, `PointInTimeError`, `ensure_timezone_aware`, `assert_no_lookahead`, `filter_pit_records`
2. **Tiered Multimodal Contracts (`enums.py`, `multimodal.py`)**: `SubscriptionTier`, `AllowedDataSource`, `PublicFilingItem`, `MacroContextPayload`, `AIExtractedFactsPayload`, `AssetEmbeddingItem`, `MultimodalFeatureBatch`
3. **Policy Compilation Contracts (`policy.py`)**: `HorizonMaskMode`, `RLRewardWeights`, `UserPolicyConfig`, `PolicyCompileRequest`, `PolicyCompileResult`
4. **Zero-Trust Telemetry & Research (`telemetry.py`)**: `DaemonStatus`, `FORBIDDEN_SECRET_FIELDS`, `RunTrace`, `KillCriterion`, `SourceFactsSnapshot`, `ThesisManifest`

## Local Verification / 로컬 검증

```bash
uv sync --dev
uv run ruff check .
uv run pytest -q
```
