# ZENOV PHASE 2.1 REAL DATA CERTIFICATION

## Objective

새로운 기능 개발을 중단하고, 안산교통 실제 CSV 143대 데이터가 Zenov Trust Chain을 끝까지 통과하는지 증명한다.

검증 체인:

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

## Required Real Data

안산교통 CSV는 최소 아래 필드를 포함해야 한다.

```text
vehicle_id
operation_date
distance_km
passenger_count
daily_revenue
driver_id
energy_consumed_kwh
```

`energy_consumed_kwh`는 없으면 계산 가정값으로 보완할 수 있지만, 실제 인증 단계에서는 가능한 한 실측값을 사용한다.

## Real DB Requirements

실제 PostgreSQL / InfluxDB 검증 시 아래 환경변수가 필요하다.

```text
DATABASE_URL
INFLUXDB_URL
INFLUXDB_TOKEN
INFLUXDB_ORG
INFLUXDB_BUCKET
ZENOV_HMAC_SECRET
```

PostgreSQL 검증 항목:

- `packet_id` 저장
- `evidence_id` 저장
- `mrv_id` 저장
- `asset_id` 저장
- `trace/full` 조회

InfluxDB 검증 항목:

- 시계열 저장
- `packet_id` 태그 연결
- `evidence_id` 태그 연결
- `mrv_id` 태그 연결

## Certification Script

실제 CSV 인증:

```bash
python3 -B scripts/phase21_real_data_certification.py \
  --csv /path/to/ansan-143-real.csv
```

샘플 리허설:

```bash
python3 -B scripts/phase21_real_data_certification.py --use-sample --allow-memory-fallback
```

30일 리플레이 리허설:

```bash
python3 -B scripts/phase21_real_data_certification.py \
  --use-sample \
  --replay-days 30 \
  --allow-memory-fallback
```

결과 파일:

```text
outputs/phase2.1-real-data-certification/latest-certification-report.json
```

운영 인증에서는 `--allow-memory-fallback`을 사용하지 않는다. PostgreSQL 또는 InfluxDB가 연결되지 않으면 인증 상태는 `HOLD` 또는 `FAIL`이어야 한다.

## Failure Certification

아래 오류는 의도적으로 발생시켜 Reject 동작을 확인한다.

- `MISSING_VEHICLE_ID`
- `INVALID_DATE`
- `DUPLICATE_OPERATION`
- `NEGATIVE_DISTANCE`
- `OUTLIER_DISTANCE`

실패 Row는 삭제하지 않고 `failed_import_rows`에 보존해야 한다.

## Success Criteria

실제 데이터 기준:

```text
Import Success > 99%
Verification Pass > 95%
Traceability = 100%
Data Loss = 0
```

## Manual Audit Test

랜덤 Packet을 선택해 5분 이내 아래 체인을 확인한다.

```text
packet_id
-> evidence_id
-> mrv_id
-> verification_id
-> asset_id
-> report_id
```

## Operating Rule

Phase 2.1은 기능 개발 스프린트가 아니다.

Phase 2.1은 실제 데이터 기준으로 Zenov가 데이터를 Carbon Asset 후보와 MRV Report까지 전환할 수 있음을 증명하는 인증 단계다.
