# ZENOV PRODUCTION RUNBOOK

## Scope

Customer Zero 운영 환경에서 데이터 수집, Import, Evidence, MRV, Verification, Asset, Report 체인을 안정적으로 유지한다.

## Daily Operations

1. DB 상태 확인
2. Import Job 상태 확인
3. Failed Row 확인
4. Traceability 100% 확인
5. Report Snapshot 확인
6. Backup 상태 확인

## Health Checks

```bash
curl -s http://127.0.0.1:8010/health
curl -s http://127.0.0.1:8010/api/v1/db/status
curl -s http://127.0.0.1:8010/api/v1/dashboard/summary
```

## Certification Check

```bash
python3 -B scripts/phase21_real_data_certification.py \
  --csv /path/to/ansan-143-real.csv
```

## Production Gates

- `memory_fallback` 금지
- PostgreSQL 연결 필수
- InfluxDB 연결 필수
- 실제 CSV 사용 필수
- Failure Certification 통과 필수

## Daily KPI

- Import Success Rate
- Verification Pass Rate
- Traceability Rate
- Data Loss Count
- Recovery Time

## Escalation

| Condition | Action |
| --- | --- |
| Data Loss > 0 | 즉시 Import 중단, 원본 CSV 보존 |
| Traceability < 100% | Manual Audit 진행 |
| Verification Pass < 95% | Failure reason_code 분석 |
| DB disconnected | 신규 Import 중단 |

