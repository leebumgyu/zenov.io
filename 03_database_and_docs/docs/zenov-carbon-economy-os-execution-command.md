# ZENOV CARBON ECONOMY OS EXECUTION COMMAND

## Status

AUTHORITATIVE EXECUTION ORDER

이 문서는 Zenov의 전체 개발 순서와 개발 금지선을 정의한다.

핵심 원칙:

```text
Real Data
↓
Trust & Evidence
↓
MRV
↓
Carbon Asset
↓
Verification
↓
Deal Room
↓
Capital Marketplace
↓
Carbon Operations
```

Zenov는 탄소배출권을 직접 발행하는 플랫폼이 아니다.

Zenov는 탄소배출권이 될 수 있는 데이터를 수집하고, 증거화하고, MRV로 계산하고, Carbon Asset으로 등록하고, 검증과 투자 검토까지 연결하는 Carbon Economy Operating System이다.

---

## Development Rules

### Rule 1. Real Data First

실제 데이터가 없는 기능은 개발하지 않는다.

### Rule 2. No Trust, No MRV

Trust Layer를 통과하지 못한 데이터는 계산하지 않는다.

### Rule 3. No Evidence, No Asset

Evidence ID가 없는 MRV 결과는 Carbon Asset으로 등록하지 않는다.

### Rule 4. No Verification, No Investment

검증 상태가 없는 Asset은 Deal Room이나 투자 화면에 노출하지 않는다.

### Rule 5. No Marketplace Before Registry

Registry와 Verification Workflow가 완성되기 전 Marketplace 기능은 개발하지 않는다.

---

## Phase 1. Real Data Onboarding

목표:

전기택시, 충전기, 태양광, 공장 센서의 실제 데이터를 Zenov 표준 구조로 수집한다.

개발 항목:

- Taxi Data Connector
- Charger Data Connector
- Solar Inverter Connector
- Factory Sensor Connector
- Unified Telemetry Schema
- Data Cleansing Pipeline
- Store & Forward Gateway

필수 API:

```text
POST /api/v1/telemetry/ingest
GET /api/v1/telemetry/latest
GET /api/v1/telemetry/source/{source_id}
```

완료 기준:

- 실제 데이터 1,000건 수집
- 정제 성공률 95% 이상
- packet_id 생성
- Dashboard 표시

현재 구현 상태:

- Taxi CSV Import 존재
- Bulk CSV Import 존재
- Demo Generator 존재
- Real telemetry API는 별도 표준 경로로 미완성

판정:

IN PROGRESS

---

## Phase 2. Trust & Evidence Layer

목표:

모든 데이터를 증거화한다.

개발 항목:

- Trust Packet Service
- Hash Verification
- Signature Verification
- Calibration Check
- Evidence ID Generator
- Audit Trail
- Reject Log

데이터 체인:

```text
packet_id
↓
evidence_id
```

필수 API:

```text
POST /api/v1/trust/packet
POST /api/v1/evidence/create
GET /api/v1/evidence/{evidence_id}
GET /api/v1/audit/{packet_id}
GET /api/v1/rejects
```

현재 구현 상태:

- `POST /api/v1/trust/packet` 존재
- `GET /api/v1/audit/{packet_id}` 존재
- `GET /api/v1/rejects` 존재
- Trace Chain 내부에서 evidence_id 생성 구조 존재
- 독립 Evidence API는 보강 필요

판정:

PARTIAL COMPLETE

---

## Phase 3. MRV Engine

목표:

검증된 데이터만 탄소감축량으로 계산한다.

개발 항목:

- Mobility MRV Engine
- Solar MRV Engine
- Factory MRV Engine
- Carbon Factor Config YAML
- Methodology Versioning
- Double Counting Prevention

데이터 체인:

```text
packet_id
↓
evidence_id
↓
mrv_id
```

필수 API:

```text
POST /api/v1/mrv/calculate
GET /api/v1/mrv/{mrv_id}
GET /api/v1/mrv/by-packet/{packet_id}
```

현재 구현 상태:

- Trust 통과 후 MRV Chain 처리 존재
- `POST /api/v1/navigation-carbon/predict` 존재
- `POST /api/v1/carbon-factor/calculate` 존재
- `GET /api/v1/traceability/mrv/{mrv_id}` 존재
- 표준 `/mrv/...` API는 별도 정리 필요

판정:

PARTIAL COMPLETE

---

## Phase 4. Carbon Value Engine

목표:

CO2e를 경제적 가치로 환산한다.

개발 항목:

- Carbon Price Config
- Carbon Value Calculator
- Currency Support
- Price Source Logging

데이터 체인:

```text
packet_id
↓
evidence_id
↓
mrv_id
↓
value_id
```

필수 API:

```text
POST /api/v1/carbon-value/calculate
GET /api/v1/carbon-value/{value_id}
```

현재 구현 상태:

- MRV Traceability Chain 안에서 Carbon Value 계산 존재
- Carbon Factor 계산 결과에서 estimated_value 산출 존재
- 표준 `/carbon-value/...` API는 별도 정리 필요

판정:

PARTIAL COMPLETE

---

## Phase 5. Carbon Registry

목표:

MRV 결과를 Carbon Asset으로 등록한다.

상태:

```text
DRAFT
PENDING
VERIFIED
RETIRED
REJECTED
```

데이터 체인:

```text
packet_id
↓
evidence_id
↓
mrv_id
↓
value_id
↓
asset_id
```

필수 API:

```text
POST /api/v1/projects
GET /api/v1/projects/{project_id}
POST /api/v1/assets/register
GET /api/v1/assets/{asset_id}
PATCH /api/v1/assets/{asset_id}/status
```

현재 구현 상태:

- Asset Candidate 구조 존재
- Full Trace에서 asset_id 조회 가능
- Carbon Finance/Ownership 일부 존재
- 표준 Registry API는 완성 필요

판정:

IN PROGRESS

---

## Phase 6. Verification Workflow

목표:

검증기관 또는 내부 검증자가 Asset을 검토할 수 있게 한다.

상태:

```text
REQUESTED
UNDER_REVIEW
VERIFIED
REJECTED
NEEDS_MORE_DATA
```

필수 API:

```text
POST /api/v1/verification/request
GET /api/v1/verification/{request_id}
PATCH /api/v1/verification/{request_id}/status
GET /api/v1/verification/{request_id}/evidence-package
```

현재 구현 상태:

- Verification Score 개념 존재
- Taxi CSV Import 체인에서 verification_id 생성
- 독립 Verification Workflow API는 미완성

판정:

NEXT CORE PHASE

---

## Phase 7. Deal Room

목표:

검증된 Carbon Asset을 투자 검토 가능한 패키지로 만든다.

필수 API:

```text
POST /api/v1/deal-room/create
GET /api/v1/deal-room/{deal_id}
GET /api/v1/deal-room/{deal_id}/documents
```

개발 조건:

- VERIFIED Asset만 Deal Room 등록 가능
- Evidence / MRV / Value / Audit 다운로드 가능
- Verification Workflow 완료 이후 착수

판정:

DEFERRED

---

## Phase 8. Capital Marketplace Readiness

목표:

실제 거래가 아니라 투자 연결 준비 상태를 만든다.

개발 금지:

- 실제 금융상품 판매
- 자동 투자 체결
- 토큰 발행
- 거래소 연동

필수 API:

```text
POST /api/v1/investors
GET /api/v1/investors/{investor_id}/matches
POST /api/v1/projects/{project_id}/interest
```

판정:

DEFERRED UNTIL REGISTRY + VERIFICATION

---

## Phase 9. Carbon Operations Center

목표:

추천이 실제 운영 행동으로 이어지는 Closed Loop 구조를 만든다.

필수 API:

```text
GET /api/v1/actions/recommendations
POST /api/v1/actions/{action_id}/accept
POST /api/v1/actions/{action_id}/result
```

현재 구현 상태:

- Economic Decision Engine 추천 결과 존재
- Action accept/result API는 미완성

판정:

FUTURE PHASE

---

## Phase 10. Digital Twin & Project Factory

목표:

고객이 무엇을 하면 더 많은 탄소 자산을 만들 수 있는지 시뮬레이션한다.

필수 API:

```text
POST /api/v1/scenarios
POST /api/v1/scenarios/{scenario_id}/simulate
GET /api/v1/scenarios/{scenario_id}/result
POST /api/v1/project-factory/generate
```

판정:

DEFERRED BLUEPRINT

---

## Required Dashboard Menu

최종 메뉴 구조:

```text
01 System Status
02 Real Data Onboarding
03 Trust & Evidence
04 MRV Center
05 Carbon Value
06 Carbon Registry
07 Verification Center
08 Carbon Portfolio
09 Deal Room
10 Capital Marketplace Readiness
11 Carbon Operations Center
12 Digital Twin
13 Project Factory
14 Partner Ecosystem
15 Customer Expansion
```

현재 데모 메뉴는 기존 구현 단위 기준으로 분리되어 있으므로, 최종 제품 메뉴와 데모 메뉴를 구분한다.

데모 메뉴를 최종 메뉴로 즉시 바꾸면 실제 구현되지 않은 Phase까지 완성된 것처럼 보일 수 있으므로 금지한다.

---

## Immediate Development Order

지금 즉시 개발 또는 보강할 항목:

1. Real Data Connector
2. Unified Telemetry
3. Trust & Evidence 독립 API
4. MRV 표준 API
5. Carbon Value 표준 API

다음:

6. Carbon Registry
7. Verification Workflow
8. Portfolio Dashboard

이후:

9. Deal Room
10. Capital Marketplace Readiness
11. Carbon Operations
12. Digital Twin
13. Project Factory

---

## Absolute Prohibitions

아래는 법적·운영적 준비 전 개발 금지:

- Carbon Credit 자동 발행
- 토큰 발행
- 거래소 연동
- 자동 투자 체결
- 금융상품 판매
- 검증기관 승인 없는 VERIFIED 자동 처리

---

## Final Success Questions

Zenov는 아래 질문에 답할 수 있어야 한다.

1. 이 데이터는 어디서 왔는가?
2. 조작되지 않았는가?
3. 어떤 방법론으로 계산했는가?
4. 얼마의 감축량인가?
5. 얼마의 경제적 가치인가?
6. 어떤 프로젝트의 자산인가?
7. 누가 검증했는가?
8. 투자 검토가 가능한가?
9. 더 많은 탄소 자산을 만들려면 무엇을 해야 하는가?

---

## Current Implementation Matrix

| Phase | Current Status | Notes |
|---|---:|---|
| Real Data Onboarding | IN PROGRESS | Taxi CSV and bulk import exist. Standard telemetry API needed. |
| Trust & Evidence | PARTIAL COMPLETE | Trust packet, audit, reject, trace exist. Independent evidence API needed. |
| MRV Engine | PARTIAL COMPLETE | Navigation MRV and carbon factor calculation exist. Standard MRV API needed. |
| Carbon Value | PARTIAL COMPLETE | Value calculation exists inside chain. Standard Carbon Value API needed. |
| Carbon Registry | IN PROGRESS | Asset candidate and ownership exist. Registry lifecycle API needed. |
| Verification Workflow | NEXT CORE PHASE | Verification IDs/scores exist in import chain. Workflow API needed. |
| Deal Room | DEFERRED | Must wait for VERIFIED assets. |
| Capital Marketplace | DEFERRED | No marketplace before Registry and Verification. |
| Carbon Operations | FUTURE PHASE | Economic recommendations exist. Action tracking API needed later. |
| Digital Twin & Project Factory | DEFERRED | Needs real operating data before simulation is useful. |
