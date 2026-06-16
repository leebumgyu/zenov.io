# CUSTOMER #2 DEPLOYMENT PLAYBOOK

## Objective

안산교통 성공 모델을 두 번째 택시회사에 7일 이내 복제한다.

## Deployment Flow

```text
Day 0: NDA / 데이터 범위 합의
Day 1: CSV 샘플 수령
Day 2: Data Mapping
Day 3: Test Import
Day 4: Failure Certification
Day 5: Full Import
Day 6: MRV / Asset / Report 검증
Day 7: Executive Review
```

## Required Customer Data

- 회사명
- 차량 목록
- 운행일별 주행거리
- 승객수
- 매출
- 기사 ID
- 차량 연료 유형
- EV 전환 계획

## Deployment Checklist

- Partner ID 생성
- Tenant 생성
- CSV Mapping 확정
- 첫 Packet 생성
- 첫 Evidence 생성
- 첫 MRV 생성
- 첫 Asset Candidate 생성
- 첫 Report 생성

## Success Criteria

| KPI | Target |
| --- | --- |
| Onboarding Time | < 7 Days |
| First Evidence | Day 3 이내 |
| First MRV | Day 5 이내 |
| First Report | Day 7 이내 |
| Manual Audit | 5분 이내 |

## Rule

새로운 고객을 연결하기 위해 코드를 수정해야 한다면 실패다.

Customer #2는 설정, 매핑, CSV 수집만으로 온보딩되어야 한다.

