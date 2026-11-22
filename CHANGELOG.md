# Changelog

All notable changes to **`zerostreet-schema`** are documented in this file.
The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

이 프로젝트의 주요 변경 이력은 Keep a Changelog 1.1.0 및 SemVer 2.0.0 규격을 따릅니다.

---

## [Unreleased]

## [0.2.0] - 2026-11-22

### Added
- Multi-entity unit specialization contracts (`EntityType`: `equity`, `index`, `macro`, `sector`, `futures`, plus normalization/default helpers) across PIT multimodal data schemas.
- Updated cross-repository naming across schemas and bilingual OpenWiki documentation (`ZeroLens` and `ZeroSteer`).
- `EntityType` 기반 다중 분석 단위(종목·지수·매크로·섹터·선물) PIT 스키마 계약 추가 및 `ZeroLens`·`ZeroSteer` 공식 명칭 통일.

## [0.1.0] - 2026-11-22

### Added
- Initial release of Layer 0 Pydantic v2 contracts: `MultimodalFeatureBatch`, `AssetEmbeddingItem`, `SourceDataPayload`, `UserPolicyConfig`, `RLRewardWeights`, `HorizonMaskMode`, `RunTrace`, `ThesisManifest`, and `PointInTimeStamp` (`available_ts <= as_of_ts` validation).
- Layer 0 표준 Pydantic v2 계약(PIT 멀티모달 피처 배치, 사용자 정책 설정, `RunTrace`, `ThesisManifest`) 초기 릴리스.
