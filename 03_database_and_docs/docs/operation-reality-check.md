# ZENOV OPERATION REALITY CHECK

## Current Stage

`PHASE_2_1_REAL_DATA_CERTIFICATION`

## Rule

새로운 데모 기능 개발을 중단한다.

현재 목표는 기능 수가 아니라 실제 데이터 기준 증명이다.

```text
CSV
-> Packet
-> Evidence
-> MRV
-> Verification
-> Asset
-> Registry
-> Report
```

## Development Stop List

6월 19일 전까지 아래 항목은 새로 개발하지 않는다.

- 신규 UI
- 신규 Dashboard 컴포넌트
- AI Agent
- Marketplace
- Carbon Credit 발행
- Token
- 외부 인증기관 API 자동 제출

## Production Hardening Gate

운영 인증에서는 `memory_fallback`을 허용하지 않는다.

반드시 실제 저장소를 연결한다.

```text
PostgreSQL
InfluxDB
```

필수 환경변수:

```text
DATABASE_URL
INFLUXDB_URL
INFLUXDB_TOKEN
INFLUXDB_ORG
INFLUXDB_BUCKET
ZENOV_HMAC_SECRET
```

## Reality Check Command

실제 안산교통 CSV:

```bash
python3 -B scripts/phase21_real_data_certification.py \
  --csv /path/to/ansan-143-real.csv
```

30일 리플레이:

```bash
python3 -B scripts/phase21_real_data_certification.py \
  --csv /path/to/ansan-143-30days-real.csv \
  --replay-days 30
```

샘플 리허설만 필요한 경우:

```bash
python3 -B scripts/phase21_real_data_certification.py \
  --use-sample \
  --replay-days 30 \
  --allow-memory-fallback
```

`--allow-memory-fallback`은 리허설 전용이다. 운영 인증 결과로 제출하지 않는다.

## Certification KPIs

| KPI | Target |
| --- | --- |
| Import Success | > 99% |
| Verification Pass | > 95% |
| Traceability | 100% |
| Data Loss | 0 |
| Manual Audit | Random packet trace under 5 minutes |

## Failure Certification

반드시 Reject 되어야 하는 오류:

- `MISSING_VEHICLE_ID`
- `INVALID_DATE`
- `DUPLICATE_OPERATION`
- `NEGATIVE_DISTANCE`
- `OUTLIER_DISTANCE`

## CEO Message

Zenov는 소프트웨어 기능을 판매하는 것이 아니라, 데이터 무결성과 탄소 감축 실적이라는 신뢰를 서비스한다.

143대 실제 데이터가 Report까지 완주하는 것이 이번 단계의 유일한 성공 기준이다.
