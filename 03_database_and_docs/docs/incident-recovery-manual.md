# ZENOV INCIDENT RECOVERY MANUAL

## Principle

실패 데이터는 삭제하지 않는다.

모든 실패는 `reason_code`와 함께 보존하고 재처리 가능해야 한다.

## Incident Types

| Incident | Reason Code |
| --- | --- |
| 차량번호 누락 | MISSING_VEHICLE_ID |
| 날짜 오류 | INVALID_DATE |
| 중복 운행 | DUPLICATE_OPERATION |
| 음수 거리 | NEGATIVE_DISTANCE |
| 이상 거리 | OUTLIER_DISTANCE |
| Evidence 실패 | EVIDENCE_CREATION_FAILED |
| MRV 실패 | MRV_CALCULATION_FAILED |
| Verification 거절 | VERIFICATION_REJECTED |

## Recovery Flow

```text
FAILED
-> Root Cause Analysis
-> Data Correction
-> RETRY_PENDING
-> RETRYING
-> RECOVERED
```

## Manual Audit Flow

```text
packet_id
-> evidence_id
-> mrv_id
-> verification_id
-> asset_id
-> report_id
```

## Recovery Rule

원본 CSV는 변경하지 않는다.

정정 데이터는 별도 correction file로 관리하고, 원본과 정정본의 Hash를 모두 보존한다.

## Recovery KPI

- Recovery Time
- Recovered Row Count
- Permanent Reject Count
- Repeat Incident Count

