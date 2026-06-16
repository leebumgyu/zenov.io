# CUSTOMER ZERO CERTIFICATION REPORT

## Customer

Ansan Transport

## Certification Scope

143대 택시 실제 운영 데이터를 Zenov Trust Chain에 투입하여 아래 전체 체인 완주 여부를 검증한다.

```text
CSV
-> Packet
-> Evidence
-> MRV
-> Verification
-> Asset
-> Registry Ready
-> Report
```

## Required Inputs

- 실제 CSV 원본 파일
- 차량번호
- 운행일
- 일일 주행거리
- 승객수
- 일일 매출
- 기사 ID
- 전력 사용량 또는 전비 산정 근거

## Certification Result

현재 상태:

```text
HOLD
```

HOLD 사유:

- 실제 안산교통 CSV 미확보
- PostgreSQL 미연결
- InfluxDB 미연결

## Certification KPIs

| KPI | Target | Current |
| --- | --- | --- |
| Import Success | > 99% | Pending Real CSV |
| Verification Pass | > 95% | Pending Real CSV |
| Traceability | 100% | Pending Real CSV |
| Data Loss | 0 | Pending Real CSV |
| Asset Generation Success | > 95% | Pending Real CSV |

## Rehearsal Result

샘플 리허설 기준:

- 143건 처리 성공
- 30일 4,290건 리플레이 성공
- Failure Certification 통과

주의:

샘플 리허설은 운영 인증이 아니다. 실제 CSV와 실제 DB 연결 이후에만 PASS 판정 가능하다.

## Final Certification Command

```bash
python3 -B scripts/phase21_real_data_certification.py \
  --csv /path/to/ansan-143-real.csv
```

## 30-Day Replay Command

```bash
python3 -B scripts/phase21_real_data_certification.py \
  --csv /path/to/ansan-143-30days-real.csv \
  --replay-days 30
```

