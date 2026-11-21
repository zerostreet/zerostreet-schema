# zerostreet-schema

ZeroStreet (`주식회사 제로스트리트`) 생태계 전 계층(`HyperAlpha-VLA`, `AlphaGraph`, `AlphaSmith`, `ZeroStreet Architect Skills`)이 공유하는 **Pydantic v2 표준 데이터 계약 및 Point-in-Time 시점 누수(Look-Ahead Bias) 차단 라이브러리**입니다.

## 핵심 제공 기능

1. **Point-in-Time 3중 타임스탬프 검증 (`pit.py`)**:
   - `event_ts <= published_ts <= available_ts` 및 `available_ts <= as_of_ts` 규칙으로 미래 시점 정보 참조를 원천 차단합니다.
2. **멀티모달 임베딩·원천 데이터 계약 (`multimodal.py`)**:
   - `SubscriptionTier`별 Matryoshka 차원(`0 / 32 / 128 / 256`)과 재배포 적법 소스(`OpenDART`, `SEC_EDGAR`, `BOK_ECOS`, `FRED`, `AI_EXTRACTED_FACTS`)를 검증합니다.
3. **사용자 개별 정책 컴파일 계약 (`policy.py`)**:
   - `UserPolicyConfig`는 최소 2개 고유 심볼과 1개 이상의 0보다 큰 목적함수 가중치를 강제합니다.
4. **제로 트러스트 텔레메트리 & 리서치 매니페스트 (`telemetry.py`)**:
   - `RunTrace` (`extra="forbid"`)는 계좌번호·증권사 API 키·원화 총액 등 민감 필드를 금지합니다.
   - `ThesisManifest` (`schema_version="2.0"`)는 `alpha-wiki`와 `AlphaGraph` 간의 구조화 가설 검증 스키마를 제공합니다.

## 로컬 검증

```bash
uv sync --dev
uv run ruff check .
uv run pytest -q
```
