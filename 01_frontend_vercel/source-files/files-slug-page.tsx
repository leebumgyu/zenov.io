'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

type Lang = 'ko' | 'en' | 'zh' | 'th';

const FILE_ADMIN_SESSION_KEY = 'zenov_pilot_admin_session';
const FILE_ADMIN_ROLE_KEY = 'zenov_pilot_session_role';

type FileDoc = {
  label: string;
  filename: string;
  href: string;
  applyHref: string;
  applyLabel: string;
  summary: string;
  sections: Array<{
    title: string;
    items: string[];
  }>;
};

const languageOptions: Array<{ code: Lang; label: string }> = [
  { code: 'ko', label: '🇰🇷 한국어' },
  { code: 'en', label: '🇺🇸 English' },
  { code: 'zh', label: '🇨🇳 中文' },
  { code: 'th', label: '🇹🇭 ภาษาไทย' },
];

const uiText: Record<
  Lang,
  {
    language: string;
    reader: string;
    back: string;
    openOriginal: string;
    printPdf: string;
    notEvidence: string;
    missingTitle: string;
    missingDesc: string;
  }
> = {
  ko: {
    language: '문서 언어 선택',
    reader: 'PILOT 문서 리더',
    back: '파트너 로그인으로 돌아가기',
    openOriginal: '원본 파일 열기',
    printPdf: 'PDF 출력',
    notEvidence: '이 문서는 Pilot Acquisition Template이며 Evidence File이 아닙니다.',
    missingTitle: '문서를 찾을 수 없습니다',
    missingDesc: '전달 파일 목록으로 돌아가 다시 선택해 주세요.',
  },
  en: {
    language: 'Document Language',
    reader: 'PILOT Document Reader',
    back: 'Back to Partner Login',
    openOriginal: 'Open Source File',
    printPdf: 'Print PDF',
    notEvidence: 'This document is a Pilot Acquisition Template, not an Evidence File.',
    missingTitle: 'Document Not Found',
    missingDesc: 'Please return to the delivery file list and choose again.',
  },
  zh: {
    language: '文档语言',
    reader: 'PILOT 文档阅读器',
    back: '返回合作伙伴登录',
    openOriginal: '打开原始文件',
    printPdf: '输出 PDF',
    notEvidence: '本文件是 Pilot 获客模板，不是证据文件。',
    missingTitle: '未找到文档',
    missingDesc: '请返回交付文件列表后重新选择。',
  },
  th: {
    language: 'ภาษาเอกสาร',
    reader: 'ตัวอ่านเอกสาร PILOT',
    back: 'กลับไปหน้าเข้าสู่ระบบพาร์ทเนอร์',
    openOriginal: 'เปิดไฟล์ต้นฉบับ',
    printPdf: 'พิมพ์ PDF',
    notEvidence: 'เอกสารนี้เป็น Pilot Acquisition Template ไม่ใช่ Evidence File',
    missingTitle: 'ไม่พบเอกสาร',
    missingDesc: 'โปรดกลับไปยังรายการไฟล์และเลือกอีกครั้ง',
  },
};

const documents: Record<Lang, Record<string, FileDoc>> = {
  ko: {
    'pilot-proposal': {
      label: '시범 사업 제안',
      filename: 'ZENOV-PILOT-PROPOSAL.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-PILOT-PROPOSAL.pdf',
      applyHref: '/pilot-application',
      applyLabel: 'Pilot 신청 작성하기',
      summary: 'Pilot 후보에게 ZENOV의 목적, 진단 범위, 기대 산출물을 설명하는 제안 문서입니다.',
      sections: [
        { title: '현재 문제', items: ['ESG 대응 자료가 분산되어 있음', '탄소 데이터와 운영 데이터가 연결되어 있지 않음', 'Scope 3 대응 및 정부지원사업 준비가 어려움'] },
        { title: 'Pilot 내용', items: ['데이터 진단', 'ESG 진단', 'Carbon MRV 가능성 검토', 'Taxi Carbon Platform 검토', 'Factory Intelligence 검토', 'Charging Intelligence 검토'] },
        { title: '기대 효과', items: ['운영 데이터 가시화', 'ESG 준비도 확인', 'Carbon 프로젝트 후보 발굴', '정부지원사업 제출 자료 준비', '투자자 및 금융기관 검토용 자료 정리'] },
      ],
    },
    'due-diligence-questionnaire': {
      label: '통합 실사 설문지',
      filename: 'ZENOV-UNIFIED-DUE-DILIGENCE-QUESTIONNAIRE.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-UNIFIED-DUE-DILIGENCE-QUESTIONNAIRE.pdf',
      applyHref: '/due-diligence-questionnaire',
      applyLabel: '통합 실사 입력하기',
      summary: 'Pilot 선정, 리드 스코어링, MRV, 투자자 룸 공개 가능성, 탄소 프로젝트 후보를 한 번에 판단하는 통합 질문지입니다.',
      sections: [
        { title: '0. 문서 목적', items: ['리드 스코어링', 'Pilot 우선순위 선정', 'ESG 및 Carbon MRV 가능성', 'EV 전환 가능성', '충전 인프라 가능성', '공장 데이터 수집 가능성', '정부지원사업 적합성', '투자자 Deal Room 공개 가능성', '탄소 프로젝트 후보 발굴 가능성'] },
        { title: '1. 기본 기업 정보', items: ['회사명', '사업자등록번호', '법인등록번호', '대표자명', '설립연도', '본사 주소', '사업장 주소', '홈페이지', '업종', '주요 사업 내용', '담당자명', '직책', '부서', '휴대폰', '이메일', '의사결정 권한 여부'] },
        { title: '2. Pilot 참여 목적', items: ['ESG 관리 체계 구축', '탄소배출량 측정', 'Carbon MRV 준비', '탄소감축 프로젝트 발굴', '전기차 전환', '충전 인프라 구축', '태양광 및 ESS 검토', '스마트팩토리 진단', 'ERP 및 MES 데이터 연동', '에너지 비용 절감', 'Scope 3 대응', 'CBAM 대응', '정부지원사업 신청', '투자자 및 금융기관 제안 준비', 'Pilot 희망 시점'] },
        { title: '3. NDA 및 데이터 제공 가능성', items: ['NDA 체결 가능 여부', 'NDA 체결 예상일', 'NDA 담당자', '제공 가능한 데이터 유형', '데이터 제공 방식', 'API', 'CSV', 'Excel', 'PDF', 'DB Export', '수동 입력'] },
        { title: '4. 조직 및 사업장 규모', items: ['총 직원 수', '생산직', '관리직', '연구직', '운전기사 수', '외주 인력 수', '공장 수', '차고지 수', '물류센터 수', '지점 수', '충전소 수', '주요 사업 지역'] },
        { title: '5. 택시 / 모빌리티 전용 질문', items: ['총 차량 수', 'LPG 차량 수', '디젤 차량 수', '휘발유 차량 수', 'EV 차량 수', '하이브리드 차량 수', 'EV 전환 가능 차량 수', '연간 교체 예정 차량 수', '월 평균 주행거리', '월 평균 연료비', '월 평균 정비비', '주요 운행 지역', 'DTG 사용 여부', 'OBD 사용 여부', 'GPS 데이터 제공 가능 여부', '차고지 보유 여부', '충전기 설치 가능 여부', '태양광 설치 가능 여부', 'ESS 설치 가능 여부', '변압기 용량', '계약 전력'] },
        { title: '6. 공장 / 제조기업 전용 질문', items: ['생산 품목', '월 생산량', '주요 원재료', '주요 공정', '설비 수', '라인 수', '가동 시간', '평균 가동률', 'ERP 사용 여부', 'MES 사용 여부', '데이터 연동 가능성', '월 평균 전력 사용량', '월 평균 전기요금', '월 평균 가스 사용량', '월 평균 연료 사용량', '피크 전력 시간', '스마트미터 보유 여부'] },
        { title: '7. 충전사업자 / CPO 전용 질문', items: ['총 충전기 수', '급속 충전기 수', '완속 충전기 수', '운영 지역', '월 평균 충전량', '월 평균 충전 세션 수', '피크 시간대', '충전소 수', 'OCPP 지원 여부', 'API 제공 여부', '충전 시작 시간', '충전 종료 시간', '충전량 kWh', '차량 ID', '충전기 ID', '사용자 ID 익명화', '위치 정보', '장애 로그', '요금 데이터'] },
        { title: '8. ESG / 탄소 데이터 현황', items: ['ESG 보고서 발행 여부', 'ESG 담당자 보유 여부', 'ESG 평가 경험 여부', '고객사 ESG 요청 여부', '전력', '가스', '연료', '물', '폐기물', '원재료', '물류', '차량', '공급망', 'Scope 1', 'Scope 2', 'Scope 3', '탄소배출량 산정 여부', 'GHG Protocol', 'ISO 14064', 'K-ESG'] },
        { title: '9. Scope 3 / 공급망 정보', items: ['주요 납품 고객', '대기업 납품 여부', '해외 수출 여부', '수출 국가', '고객사 ESG 데이터 요청 여부', 'CBAM 영향 여부', 'EU 수출 여부', '글로벌 공급망 편입 여부'] },
        { title: '10. IoT / 센서 / 데이터 인프라', items: ['전력계', '스마트미터', '온도 센서', '습도 센서', '압력 센서', '진동 센서', '유량계', 'GPS', 'OBD', 'DTG', 'PLC', 'CCTV', 'Modbus', 'MQTT', 'OPC-UA', 'REST API', 'CSV Export', '수동 기록'] },
        { title: '11. AI 활용 가능성', items: ['현재 AI 사용 여부', '생산 예측', '품질 예측', '설비 고장 예측', '에너지 최적화', '탄소 최적화', '운행 패턴 분석', '충전 수요 예측', 'ESG 리포트 자동화', 'MRV 자동화'] },
        { title: '12. 정부지원사업 적격성', items: ['최근 3년 정부지원사업 수행 여부', '스마트공장', 'ESG', '탄소중립', '전기차', '충전소', 'RE100', 'AI', '데이터 바우처', '중소벤처기업부 과제', '산업부 과제', '환경부 과제', '지자체 지원사업', '사업계획서', '기술제안서', 'ESG 진단', '데이터 진단', '탄소감축 진단'] },
        { title: '13. 투자자 / 금융기관 실사 준비도', items: ['최근 매출 2023년', '최근 매출 2024년', '최근 매출 2025년', '재무 정보 제공 가능 여부', '설비 투자 검토', 'EV 전환 금융 검토', '충전 인프라 금융 검토', '태양광 및 ESS 검토', '탄소감축 프로젝트 검토', 'ESG 금융 검토', '정부지원금 매칭 검토'] },
        { title: '14. 탄소 프로젝트 후보 진단', items: ['EV 전환', '충전소 구축', '태양광', 'ESS', '공장 에너지 효율화', '스마트팩토리', '메탄 감축', '바이오차', '폐기물 에너지화', 'Scope 3 감축', 'RE100 대응', '프로젝트 예상 시작 시점'] },
        { title: '15. 첨부 가능 자료', items: ['사업자등록증', '회사소개서', 'ESG 보고서', '전기요금 고지서', '가스요금 고지서', '차량 목록', '운행거리 데이터', '충전 데이터', '생산량 데이터', 'ERP Export', 'MES Export', 'API 문서', '공장 배치도', '차고지 도면', '충전소 도면'] },
        { title: '16. Pilot 참여 동의', items: ['현장 방문 동의', '데이터 제공 동의', 'NDA 체결 동의', 'Pilot 참여 의사'] },
        { title: '17. 내부 평가 영역', items: ['Lead Score', 'ESG Readiness Score', 'MRV Readiness Score', 'Carbon Potential Score', 'Scope 3 Potential Score', 'Government Funding Score', 'Investment Readiness Score', 'EV Transition Score', 'Charging Potential Score', 'Data Quality Score', 'Overall Opportunity Score', 'Pilot Tier', 'Reviewer', 'Review Date', 'Next Action'] },
        { title: '18. 법적 고지', items: ['본 질문지는 Pilot 후보 평가 및 데이터 기반 사전 분석을 위한 정보 수집 문서입니다.', '모든 결과는 실제 데이터 검토, 별도 계약, 현장 실사, 제3자 검증 및 관련 법령 검토 이후 결정됩니다.', '본 문서의 작성 또는 제출은 금융상품 판매, 사업 선정, 탄소배출권 발급, 프로젝트 승인에 대한 확약이 아닙니다.'] },
      ],
    },
    'data-request-checklist': {
      label: '데이터 요청 체크리스트',
      filename: 'ZENOV-DATA-REQUEST-CHECKLIST.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-DATA-REQUEST-CHECKLIST.pdf',
      applyHref: '/data-request-checklist',
      applyLabel: '자료 요청 체크리스트 작성하기',
      summary: 'Pilot 후보에게 요청할 택시, 공장, 충전소 자료를 정리하는 체크리스트입니다.',
      sections: [
        { title: '택시 자료', items: ['차량 목록', '연료 종류', '운행거리', 'LPG 현황', '차고지 정보', '기사 수', '월 평균 주행거리'] },
        { title: '공장 자료', items: ['전기요금', '생산량', 'ERP 데이터', 'MES 데이터', '설비 정보', '공장 배치도', '에너지 비용'] },
        { title: '충전소 자료', items: ['충전량', '충전기 목록', 'OCPP 로그', 'API 문서', '충전 세션 데이터', '장애 로그'] },
      ],
    },
    'pilot-application': {
      label: '시범 적용',
      filename: 'ZENOV-PILOT-APPLICATION.xlsx',
      href: '/pilot-assets/sales-kit/ZENOV-PILOT-APPLICATION.xlsx',
      applyHref: '/pilot-application',
      applyLabel: '시범 적용 신청 작성하기',
      summary: 'Pilot 신청 기본 정보를 웹에서 입력하기 위한 신청서입니다.',
      sections: [
        { title: '신청 기본 정보', items: ['회사명', '담당자', '연락처', '이메일', '업종', '지역'] },
        { title: 'Pilot 관심 분야', items: ['ESG', 'Carbon MRV', 'Taxi Carbon', 'Factory Intelligence', 'Charging', '정부지원사업'] },
        { title: '검토 상태', items: ['NDA 체결 여부', '데이터 제공 가능 여부', '검토 메모'] },
      ],
    },
    'taxi-pilot-survey': {
      label: '택시 파일럿 설문조사',
      filename: 'ZENOV-TAXI-PILOT-SURVEY.xlsx',
      href: '/pilot-assets/sales-kit/ZENOV-TAXI-PILOT-SURVEY.xlsx',
      applyHref: '/taxi-survey',
      applyLabel: '택시 설문 작성하기',
      summary: '택시조합 및 법인택시의 차량, 기사, 차고지, 충전 후보 데이터를 수집하는 설문입니다.',
      sections: [
        { title: '차량 현황', items: ['조합명', '총 차량 수', 'LPG 차량 수', 'EV 차량 수', 'EV 전환 가능 차량 수', '기사 수'] },
        { title: '인프라 현황', items: ['차고지 여부', '충전소 후보지 여부', '월 평균 주행거리', '월 평균 연료비'] },
        { title: '활용 목적', items: ['EV 전환 가능성 분석', '충전소 후보지 검토', 'Taxi Carbon MRV 후보 발굴'] },
      ],
    },
    'factory-assessment': {
      label: '택시회사 시설 실사',
      filename: 'ZENOV-FACTORY-ASSESSMENT.xlsx',
      href: '/pilot-assets/sales-kit/ZENOV-FACTORY-ASSESSMENT.xlsx',
      applyHref: '/factory-assessment',
      applyLabel: '택시회사 시설 실사 작성하기',
      summary: '택시회사 내 정비소, 세차장, 사무실, 주차장/부지를 관리하고 충전소 및 태양광 설치 타당성 후보를 검토하는 실사 양식입니다.',
      sections: [
        { title: '시설 기본 정보', items: ['시설 명칭', '시설 유형', '관리 면적', '건물 구조'] },
        { title: '설비 및 에너지 관리', items: ['ERP/MES 도입 여부', '전기 인입 용량', '지붕/천장 재질', '월 전력 사용량', '월 전기요금'] },
        { title: '탄소 데이터 및 ESG', items: ['탄소 데이터 보유 여부', 'ESG 관심도'] },
      ],
    },
    'charging-partner-form': {
      label: '충전 파트너 양식',
      filename: 'ZENOV-CHARGING-PARTNER-FORM.xlsx',
      href: '/pilot-assets/sales-kit/ZENOV-CHARGING-PARTNER-FORM.xlsx',
      applyHref: '/charging-partner',
      applyLabel: '충전 파트너 양식 작성하기',
      summary: '충전사업자의 충전기 수, OCPP, API, 충전량, 세션 데이터 제공 가능성을 확인하는 양식입니다.',
      sections: [
        { title: '충전 인프라', items: ['충전사업자명', '충전기 수', '급속 충전기 수', '월 충전량'] },
        { title: '데이터 연동', items: ['OCPP 지원 여부', 'API 제공 여부', '충전 세션 데이터 제공 가능 여부'] },
        { title: '활용 목적', items: ['Charging Intelligence 구축', 'EV Carbon Reduction 계산', 'MRV Dataset 후보 생성'] },
      ],
    },
    'executive-one-pager': {
      label: '임원용 요약 자료 (원페이지)',
      filename: 'ZENOV-EXECUTIVE-ONE-PAGER.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-EXECUTIVE-ONE-PAGER.pdf',
      applyHref: '/pilot-application',
      applyLabel: 'Pilot 상담 정보 입력하기',
      summary: '30초 안에 ZENOV의 핵심 가치를 설명하기 위한 임원용 1장 요약 자료입니다.',
      sections: [
        { title: '우리는 무엇을 하는가', items: ['AI 기반 ESG 플랫폼', 'Carbon MRV 플랫폼', 'Taxi Carbon Platform', 'Factory Intelligence Platform'] },
        { title: '고객이 얻는 것', items: ['ESG Score', 'Carbon Score', 'Carbon Project 후보', '정부지원사업 검토', 'EV 전환 검토', '에너지 절감 검토'] },
        { title: '한 줄 메시지', items: ['기존 제조 KPI를 ESG KPI로 확장하는 데이터 플랫폼'] },
      ],
    },
    nda: {
      label: '비밀유지협약',
      filename: 'ZENOV-NDA.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-NDA.pdf',
      applyHref: '/pilot-application',
      applyLabel: 'NDA 상태 입력하기',
      summary: '자료 공유, 차량 데이터, 공장 데이터, 충전 데이터 공유 전 필요한 비밀유지협약 문서입니다.',
      sections: [
        { title: '대상', items: ['택시조합', '법인택시', '공장', '충전사업자', '전략 파트너'] },
        { title: '목적', items: ['자료 공유', '차량 데이터 공유', '공장 데이터 공유', '충전 데이터 공유', 'Pilot 검토 및 실사 준비'] },
        { title: '운영 원칙', items: ['NDA 체결 전 민감 자료 공유 제한', '제공 자료는 Pilot 검토 목적에 한정', 'Evidence File로 분류하지 않음'] },
      ],
    },
  },
  en: {
    'pilot-proposal': {
      label: 'Pilot Proposal',
      filename: 'ZENOV-PILOT-PROPOSAL.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-PILOT-PROPOSAL.pdf',
      applyHref: '/pilot-application',
      applyLabel: 'Fill Pilot Application',
      summary: 'A proposal document explaining ZENOV objectives, diagnostic scope, and expected pilot outputs.',
      sections: [
        { title: 'Current Problems', items: ['ESG response materials are fragmented', 'Carbon data and operating data are not connected', 'Scope 3 and public program preparation are difficult'] },
        { title: 'Pilot Scope', items: ['Data diagnosis', 'ESG diagnosis', 'Carbon MRV feasibility review', 'Taxi Carbon Platform review', 'Factory Intelligence review', 'Charging Intelligence review'] },
        { title: 'Expected Outcomes', items: ['Operational data visibility', 'ESG readiness confirmation', 'Carbon project candidate discovery', 'Public program submission preparation', 'Investor and financial institution review package'] },
      ],
    },
    'due-diligence-questionnaire': {
      label: 'Unified Due Diligence Questionnaire',
      filename: 'ZENOV-UNIFIED-DUE-DILIGENCE-QUESTIONNAIRE.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-UNIFIED-DUE-DILIGENCE-QUESTIONNAIRE.pdf',
      applyHref: '/due-diligence-questionnaire',
      applyLabel: 'Fill Due Diligence Form',
      summary: 'A unified questionnaire for pilot selection, lead scoring, MRV readiness, investor room visibility, and carbon project discovery.',
      sections: [
        { title: '0. Document Purpose', items: ['Lead scoring', 'Pilot priority selection', 'ESG and Carbon MRV feasibility', 'EV transition feasibility', 'Charging infrastructure feasibility', 'Factory data collection feasibility', 'Public program fit', 'Investor Deal Room visibility', 'Carbon project candidate discovery'] },
        { title: '1. Basic Company Information', items: ['Company name', 'Business registration number', 'Corporate registration number', 'CEO name', 'Year established', 'Head office address', 'Site address', 'Website', 'Industry', 'Main business description', 'Contact name', 'Title', 'Department', 'Mobile phone', 'Email', 'Decision authority'] },
        { title: '2. Pilot Participation Purpose', items: ['Build ESG management system', 'Measure carbon emissions', 'Prepare Carbon MRV', 'Discover reduction projects', 'EV transition', 'Charging infrastructure', 'Solar and ESS review', 'Smart factory diagnosis', 'ERP and MES data integration', 'Energy cost reduction', 'Scope 3 response', 'CBAM response', 'Public program application', 'Investor or financial institution proposal preparation', 'Desired pilot timing'] },
        { title: '3. NDA and Data Sharing', items: ['NDA availability', 'Expected NDA date', 'NDA contact', 'Available data types', 'Data delivery method', 'API', 'CSV', 'Excel', 'PDF', 'DB Export', 'Manual entry'] },
        { title: '4. Organization and Sites', items: ['Total employees', 'Production staff', 'Management staff', 'R&D staff', 'Drivers', 'Outsourced staff', 'Factories', 'Garages', 'Logistics centers', 'Branches', 'Charging stations', 'Main operating regions'] },
        { title: '5. Taxi / Mobility Questions', items: ['Total vehicles', 'LPG vehicles', 'Diesel vehicles', 'Gasoline vehicles', 'EV vehicles', 'Hybrid vehicles', 'EV convertible vehicles', 'Annual replacement vehicles', 'Monthly average mileage', 'Monthly fuel cost', 'Monthly maintenance cost', 'Main operating area', 'DTG use', 'OBD use', 'GPS data availability', 'Garage ownership', 'Charger installation feasibility', 'Solar installation feasibility', 'ESS installation feasibility', 'Transformer capacity', 'Contracted power'] },
        { title: '6. Factory / Manufacturer Questions', items: ['Products', 'Monthly production volume', 'Main raw materials', 'Main processes', 'Equipment count', 'Line count', 'Operating hours', 'Average utilization', 'ERP usage', 'MES usage', 'Data integration feasibility', 'Monthly power usage', 'Monthly electricity bill', 'Monthly gas usage', 'Monthly fuel usage', 'Peak power time', 'Smart meter availability'] },
        { title: '7. Charging Operator / CPO Questions', items: ['Total chargers', 'Fast chargers', 'Slow chargers', 'Operating region', 'Monthly charging volume', 'Monthly charging sessions', 'Peak time', 'Charging sites', 'OCPP support', 'API availability', 'Start time', 'End time', 'Charging kWh', 'Vehicle ID', 'Charger ID', 'Anonymized user ID', 'Location data', 'Fault logs', 'Tariff data'] },
        { title: '8. ESG / Carbon Data Status', items: ['ESG report status', 'ESG manager', 'ESG assessment experience', 'Customer ESG requests', 'Electricity', 'Gas', 'Fuel', 'Water', 'Waste', 'Raw materials', 'Logistics', 'Vehicles', 'Supply chain', 'Scope 1', 'Scope 2', 'Scope 3', 'Emission calculation status', 'GHG Protocol', 'ISO 14064', 'K-ESG'] },
        { title: '9. Scope 3 / Supply Chain', items: ['Major customers', 'Large enterprise supply', 'Export status', 'Export countries', 'Customer ESG data requests', 'CBAM impact', 'EU export', 'Global supply chain inclusion'] },
        { title: '10. IoT / Sensor / Data Infrastructure', items: ['Power meter', 'Smart meter', 'Temperature sensor', 'Humidity sensor', 'Pressure sensor', 'Vibration sensor', 'Flow meter', 'GPS', 'OBD', 'DTG', 'PLC', 'CCTV', 'Modbus', 'MQTT', 'OPC-UA', 'REST API', 'CSV Export', 'Manual records'] },
        { title: '11. AI Readiness', items: ['Current AI usage', 'Production prediction', 'Quality prediction', 'Equipment failure prediction', 'Energy optimization', 'Carbon optimization', 'Driving pattern analysis', 'Charging demand prediction', 'ESG report automation', 'MRV automation'] },
        { title: '12. Public Program Eligibility', items: ['Public program participation in last 3 years', 'Smart factory', 'ESG', 'Carbon neutrality', 'EV', 'Charging station', 'RE100', 'AI', 'Data voucher', 'SME program', 'Industry ministry program', 'Environment ministry program', 'Local government program', 'Business plan', 'Technical proposal', 'ESG diagnosis', 'Data diagnosis', 'Carbon reduction diagnosis'] },
        { title: '13. Investor / Finance Readiness', items: ['Recent revenue 2023', 'Recent revenue 2024', 'Recent revenue 2025', 'Financial information availability', 'Equipment investment review', 'EV transition finance review', 'Charging infrastructure finance review', 'Solar and ESS review', 'Carbon reduction project review', 'ESG finance review', 'Public funding matching review'] },
        { title: '14. Carbon Project Candidates', items: ['EV transition', 'Charging station buildout', 'Solar', 'ESS', 'Factory energy efficiency', 'Smart factory', 'Methane reduction', 'Biochar', 'Waste-to-energy', 'Scope 3 reduction', 'RE100 response', 'Expected project start timing'] },
        { title: '15. Available Attachments', items: ['Business registration certificate', 'Company introduction', 'ESG report', 'Electricity bill', 'Gas bill', 'Vehicle list', 'Mileage data', 'Charging data', 'Production data', 'ERP Export', 'MES Export', 'API document', 'Factory layout', 'Garage drawing', 'Charging site drawing'] },
        { title: '16. Pilot Consent', items: ['Site visit consent', 'Data sharing consent', 'NDA signing consent', 'Pilot participation intent'] },
        { title: '17. Internal Evaluation Area', items: ['Lead Score', 'ESG Readiness Score', 'MRV Readiness Score', 'Carbon Potential Score', 'Scope 3 Potential Score', 'Government Funding Score', 'Investment Readiness Score', 'EV Transition Score', 'Charging Potential Score', 'Data Quality Score', 'Overall Opportunity Score', 'Pilot Tier', 'Reviewer', 'Review Date', 'Next Action'] },
        { title: '18. Legal Notice', items: ['This questionnaire collects information for pilot candidate evaluation and data-based preliminary analysis.', 'All results are determined after actual data review, separate contracts, site due diligence, third-party validation, and legal review.', 'Submission of this document is not a commitment to sell financial products, select a project, issue carbon credits, or approve a project.'] },
      ],
    },
    'data-request-checklist': {
      label: 'Data Request Checklist',
      filename: 'ZENOV-DATA-REQUEST-CHECKLIST.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-DATA-REQUEST-CHECKLIST.pdf',
      applyHref: '/data-request-checklist',
      applyLabel: 'Fill Data Checklist',
      summary: 'A checklist of taxi, factory, and charging data to request from pilot candidates.',
      sections: [
        { title: 'Taxi Data', items: ['Vehicle list', 'Fuel type', 'Mileage', 'LPG status', 'Garage information', 'Driver count', 'Monthly average mileage'] },
        { title: 'Factory Data', items: ['Electricity bills', 'Production volume', 'ERP data', 'MES data', 'Equipment information', 'Factory layout', 'Energy costs'] },
        { title: 'Charging Site Data', items: ['Charging volume', 'Charger list', 'OCPP logs', 'API documents', 'Charging session data', 'Fault logs'] },
      ],
    },
    'pilot-application': {
      label: 'Pilot Application',
      filename: 'ZENOV-PILOT-APPLICATION.xlsx',
      href: '/pilot-assets/sales-kit/ZENOV-PILOT-APPLICATION.xlsx',
      applyHref: '/pilot-application',
      applyLabel: 'Fill Pilot Application',
      summary: 'A web application form for basic pilot candidate information.',
      sections: [
        { title: 'Basic Application Information', items: ['Company name', 'Contact person', 'Phone', 'Email', 'Industry', 'Region'] },
        { title: 'Pilot Interests', items: ['ESG', 'Carbon MRV', 'Taxi Carbon', 'Factory Intelligence', 'Charging', 'Public programs'] },
        { title: 'Review Status', items: ['NDA status', 'Data sharing availability', 'Review memo'] },
      ],
    },
    'taxi-pilot-survey': {
      label: 'Taxi Pilot Survey',
      filename: 'ZENOV-TAXI-PILOT-SURVEY.xlsx',
      href: '/pilot-assets/sales-kit/ZENOV-TAXI-PILOT-SURVEY.xlsx',
      applyHref: '/taxi-survey',
      applyLabel: 'Fill Taxi Survey',
      summary: 'A survey collecting vehicle, driver, garage, and charging candidate data from taxi unions and taxi companies.',
      sections: [
        { title: 'Vehicle Status', items: ['Union name', 'Total vehicles', 'LPG vehicles', 'EV vehicles', 'EV convertible vehicles', 'Driver count'] },
        { title: 'Infrastructure Status', items: ['Garage availability', 'Charging site candidate', 'Monthly average mileage', 'Monthly fuel cost'] },
        { title: 'Use Cases', items: ['EV transition feasibility analysis', 'Charging site candidate review', 'Taxi Carbon MRV candidate discovery'] },
      ],
    },
    'factory-assessment': {
      label: 'Taxi Company Facility Audit',
      filename: 'ZENOV-FACTORY-ASSESSMENT.xlsx',
      href: '/pilot-assets/sales-kit/ZENOV-FACTORY-ASSESSMENT.xlsx',
      applyHref: '/factory-assessment',
      applyLabel: 'Fill Taxi Company Facility Audit',
      summary: 'A site audit form for taxi company maintenance shops, washing areas, offices, parking lots, electricity, rooftop, ESG, and carbon data.',
      sections: [
        { title: 'Facility Basics', items: ['Facility name', 'Facility type', 'Managed area', 'Building structure'] },
        { title: 'Equipment and Energy', items: ['ERP/MES usage', 'Grid connection capacity', 'Roof/ceiling material', 'Monthly power usage', 'Monthly electricity bill'] },
        { title: 'Carbon Data and ESG', items: ['Carbon data availability', 'ESG interest'] },
      ],
    },
    'charging-partner-form': {
      label: 'Charging Partner Form',
      filename: 'ZENOV-CHARGING-PARTNER-FORM.xlsx',
      href: '/pilot-assets/sales-kit/ZENOV-CHARGING-PARTNER-FORM.xlsx',
      applyHref: '/charging-partner',
      applyLabel: 'Fill Charging Partner Form',
      summary: 'A form for charger count, OCPP, API, charging volume, and session data availability.',
      sections: [
        { title: 'Charging Infrastructure', items: ['Charging operator name', 'Charger count', 'Fast charger count', 'Monthly charging volume'] },
        { title: 'Data Integration', items: ['OCPP support', 'API availability', 'Charging session data availability'] },
        { title: 'Use Cases', items: ['Charging Intelligence buildout', 'EV Carbon Reduction calculation', 'MRV Dataset candidate creation'] },
      ],
    },
    'executive-one-pager': {
      label: 'Executive One Pager',
      filename: 'ZENOV-EXECUTIVE-ONE-PAGER.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-EXECUTIVE-ONE-PAGER.pdf',
      applyHref: '/pilot-application',
      applyLabel: 'Enter Pilot Consultation Info',
      summary: 'A one-page executive summary explaining ZENOV core value in 30 seconds.',
      sections: [
        { title: 'What We Do', items: ['AI-based ESG platform', 'Carbon MRV platform', 'Taxi Carbon Platform', 'Factory Intelligence Platform'] },
        { title: 'What Customers Get', items: ['ESG Score', 'Carbon Score', 'Carbon Project candidates', 'Public program review', 'EV transition review', 'Energy reduction review'] },
        { title: 'One-line Message', items: ['A data platform that extends existing manufacturing KPIs into ESG KPIs'] },
      ],
    },
    nda: {
      label: 'NDA',
      filename: 'ZENOV-NDA.pdf',
      href: '/pilot-assets/sales-kit/ZENOV-NDA.pdf',
      applyHref: '/pilot-application',
      applyLabel: 'Enter NDA Status',
      summary: 'A confidentiality document required before sharing materials, vehicle data, factory data, or charging data.',
      sections: [
        { title: 'Targets', items: ['Taxi union', 'Taxi company', 'Factory', 'Charging operator', 'Strategic partner'] },
        { title: 'Purpose', items: ['Material sharing', 'Vehicle data sharing', 'Factory data sharing', 'Charging data sharing', 'Pilot review and due diligence preparation'] },
        { title: 'Operating Principles', items: ['Restrict sensitive data sharing before NDA', 'Use provided materials only for pilot review', 'Do not classify as Evidence File'] },
      ],
    },
  },
  zh: {},
  th: {},
};

documents.zh = {
  'pilot-proposal': {
    ...documents.en['pilot-proposal'],
    label: '试点项目提案',
    applyLabel: '填写试点申请',
    summary: '向试点候选方说明 ZENOV 目标、诊断范围和预期产出的提案文件。',
    sections: [
      { title: '当前问题', items: ['ESG 资料分散', '碳数据与运营数据未连接', 'Scope 3 和政府项目准备困难'] },
      { title: 'Pilot 内容', items: ['数据诊断', 'ESG 诊断', 'Carbon MRV 可行性审查', 'Taxi Carbon Platform 审查', 'Factory Intelligence 审查', 'Charging Intelligence 审查'] },
      { title: '预期效果', items: ['运营数据可视化', 'ESG 准备度确认', '碳项目候选发掘', '政府项目提交资料准备', '投资方和金融机构审查资料整理'] },
    ],
  },
  'due-diligence-questionnaire': {
    ...documents.en['due-diligence-questionnaire'],
    label: '综合尽调问卷',
    applyLabel: '填写尽调表单',
    summary: '用于试点选择、线索评分、MRV 准备度、投资者房间公开可能性和碳项目发掘的综合问卷。',
    sections: [
      { title: '0. 文档目的', items: ['线索评分', 'Pilot 优先级选择', 'ESG 与 Carbon MRV 可行性', 'EV 转换可能性', '充电基础设施可能性', '工厂数据收集可能性', '政府项目适配性', '投资者 Deal Room 公开可能性', '碳项目候选发掘'] },
      { title: '1. 基本企业信息', items: ['公司名', '营业执照号码', '法人登记号', '代表姓名', '成立年份', '总部地址', '事业场所地址', '网站', '行业', '主要业务内容', '联系人姓名', '职务', '部门', '手机', '邮箱', '决策权限'] },
      { title: '2. Pilot 参与目的', items: ['建立 ESG 管理体系', '测量碳排放量', '准备 Carbon MRV', '发掘减排项目', 'EV 转换', '充电基础设施建设', '太阳能与 ESS 审查', '智能工厂诊断', 'ERP 与 MES 数据联动', '能源成本节减', 'Scope 3 应对', 'CBAM 应对', '政府项目申请', '投资者或金融机构提案准备', 'Pilot 希望时间'] },
      { title: '3. NDA 与数据提供', items: ['NDA 签署可能性', '预计 NDA 日期', 'NDA 负责人', '可提供数据类型', '数据提供方式', 'API', 'CSV', 'Excel', 'PDF', 'DB 导出', '手动输入'] },
      { title: '4. 组织与场所规模', items: ['总员工数', '生产人员', '管理人员', '研发人员', '司机人数', '外包人员', '工厂数', '车库数', '物流中心数', '分支机构数', '充电站数', '主要运营地区'] },
      { title: '5. 出租车 / 移动出行专用问题', items: ['总车辆数', 'LPG 车辆数', '柴油车辆数', '汽油车辆数', 'EV 车辆数', '混动车辆数', 'EV 可转换车辆数', '年度更换计划车辆', '月平均行驶距离', '月燃料费', '月维修费', '主要运营地区', 'DTG 使用情况', 'OBD 使用情况', 'GPS 数据提供可能性', '车库持有情况', '充电器安装可能性', '太阳能安装可能性', 'ESS 安装可能性', '变压器容量', '合同电力'] },
      { title: '6. 工厂 / 制造企业专用问题', items: ['生产品类', '月生产量', '主要原材料', '主要工艺', '设备数量', '产线数量', '运行时间', '平均开工率', 'ERP 使用情况', 'MES 使用情况', '数据联动可能性', '月平均电力使用量', '月平均电费', '月平均燃气使用量', '月平均燃料使用量', '峰值用电时间', '智能电表持有情况'] },
      { title: '7. 充电运营商 / CPO 专用问题', items: ['总充电器数', '快速充电器数', '慢速充电器数', '运营地区', '月平均充电量', '月平均充电会话数', '高峰时间段', '充电站数', 'OCPP 支持情况', 'API 提供可能性', '充电开始时间', '充电结束时间', '充电量 kWh', '车辆 ID', '充电器 ID', '匿名用户 ID', '位置信息', '故障日志', '计费数据'] },
      { title: '8. ESG / 碳数据现状', items: ['ESG 报告书发行情况', 'ESG 负责人', 'ESG 评估经验', '客户 ESG 请求', '电力', '燃气', '燃料', '水', '废弃物', '原材料', '物流', '车辆', '供应链', 'Scope 1', 'Scope 2', 'Scope 3', '排放量计算情况', 'GHG Protocol', 'ISO 14064', 'K-ESG'] },
      { title: '9. Scope 3 / 供应链信息', items: ['主要供货客户', '是否供货大型企业', '出口情况', '出口国家', '客户 ESG 数据请求', 'CBAM 影响', 'EU 出口', '是否进入全球供应链'] },
      { title: '10. IoT / 传感器 / 数据基础设施', items: ['电表', '智能电表', '温度传感器', '湿度传感器', '压力传感器', '振动传感器', '流量计', 'GPS', 'OBD', 'DTG', 'PLC', 'CCTV', 'Modbus', 'MQTT', 'OPC-UA', 'REST API', 'CSV 导出', '手动记录'] },
      { title: '11. AI 应用可能性', items: ['当前 AI 使用情况', '生产预测', '质量预测', '设备故障预测', '能源优化', '碳优化', '行驶模式分析', '充电需求预测', 'ESG 报告自动化', 'MRV 自动化'] },
      { title: '12. 政府项目适配性', items: ['最近 3 年政府项目执行情况', '智能工厂', 'ESG', '碳中和', '电动车', '充电站', 'RE100', 'AI', '数据券', '中小企业项目', '产业部项目', '环境部项目', '地方政府项目', '商业计划书', '技术提案书', 'ESG 诊断', '数据诊断', '碳减排诊断'] },
      { title: '13. 投资者 / 金融机构尽调准备度', items: ['最近销售额 2023', '最近销售额 2024', '最近销售额 2025', '财务信息提供可能性', '设备投资审查', 'EV 转换金融审查', '充电基础设施金融审查', '太阳能与 ESS 审查', '碳减排项目审查', 'ESG 金融审查', '政府资金匹配审查'] },
      { title: '14. 碳项目候选诊断', items: ['EV 转换', '充电站建设', '太阳能', 'ESS', '工厂能源效率化', '智能工厂', '甲烷减排', '生物炭', '废弃物能源化', 'Scope 3 减排', 'RE100 应对', '预计项目启动时间'] },
      { title: '15. 可提交附件', items: ['营业执照', '公司介绍书', 'ESG 报告书', '电费账单', '燃气费账单', '车辆列表', '行驶距离数据', '充电数据', '生产量数据', 'ERP 导出', 'MES 导出', 'API 文档', '工厂布局图', '车库图纸', '充电站图纸'] },
      { title: '16. Pilot 参与同意', items: ['现场访问同意', '数据提供同意', 'NDA 签署同意', 'Pilot 参与意向'] },
      { title: '17. 内部评价区域', items: ['Lead Score', 'ESG Readiness Score', 'MRV Readiness Score', 'Carbon Potential Score', 'Scope 3 Potential Score', 'Government Funding Score', 'Investment Readiness Score', 'EV Transition Score', 'Charging Potential Score', 'Data Quality Score', 'Overall Opportunity Score', 'Pilot Tier', 'Reviewer', 'Review Date', 'Next Action'] },
      { title: '18. 法律告知', items: ['本问卷用于 Pilot 候选评估和基于数据的预先分析。', '所有结果需经过实际数据审查、另行合同、现场尽调、第三方验证及相关法律审查后决定。', '本文件的填写或提交不构成金融商品销售、项目选定、碳排放权发行或项目批准的承诺。'] },
    ],
  },
  'data-request-checklist': {
    ...documents.en['data-request-checklist'],
    label: '数据请求清单',
    applyLabel: '填写数据清单',
    summary: '整理向试点候选方请求的出租车、工厂和充电数据。',
    sections: [
      { title: '出租车资料', items: ['车辆列表', '燃料类型', '行驶距离', 'LPG 现状', '车库信息', '司机数量', '月平均行驶距离'] },
      { title: '工厂资料', items: ['电费账单', '生产量', 'ERP 数据', 'MES 数据', '设备信息', '工厂布局图', '能源成本'] },
      { title: '充电站资料', items: ['充电量', '充电器列表', 'OCPP 日志', 'API 文档', '充电会话数据', '故障日志'] },
    ],
  },
  'pilot-application': {
    ...documents.en['pilot-application'],
    label: '试点申请',
    applyLabel: '填写试点申请',
    summary: '用于在网页中录入试点候选方基础信息的申请表。',
    sections: [
      { title: '申请基本信息', items: ['公司名', '联系人', '电话', '邮箱', '行业', '地区'] },
      { title: 'Pilot 关注领域', items: ['ESG', 'Carbon MRV', 'Taxi Carbon', 'Factory Intelligence', 'Charging', '政府项目'] },
      { title: '审查状态', items: ['NDA 状态', '数据提供可能性', '审查备注'] },
    ],
  },
  'taxi-pilot-survey': {
    ...documents.en['taxi-pilot-survey'],
    label: '出租车试点问卷',
    applyLabel: '填写出租车问卷',
    summary: '收集出租车协会和出租车公司的车辆、司机、车库和充电候选数据。',
    sections: [
      { title: '车辆现状', items: ['协会名称', '总车辆数', 'LPG 车辆', 'EV 车辆', 'EV 可转换车辆', '司机数量'] },
      { title: '基础设施现状', items: ['车库可用性', '充电站候选地', '月平均行驶距离', '月平均燃料费'] },
      { title: '使用目的', items: ['EV 转换可行性分析', '充电站候选地审查', 'Taxi Carbon MRV 候选发掘'] },
    ],
  },
  'factory-assessment': {
    ...documents.en['factory-assessment'],
    label: '出租车公司设施实查',
    applyLabel: '填写出租车公司设施实查',
    summary: '用于出租车公司维修厂、洗车区、办公室、停车场/场地、电力、屋顶、ESG 和碳数据的现场实查表。',
    sections: [
      { title: '设施基础信息', items: ['设施名称', '设施类型', '管理面积', '建筑结构'] },
      { title: '设备与能源管理', items: ['ERP/MES 使用情况', '电力接入容量', '屋顶/天花材料', '月电力使用量', '月电费'] },
      { title: '碳数据与 ESG', items: ['碳数据持有情况', 'ESG 关注度'] },
    ],
  },
  'charging-partner-form': {
    ...documents.en['charging-partner-form'],
    label: '充电合作伙伴表单',
    applyLabel: '填写充电合作伙伴表单',
    summary: '确认充电器数量、OCPP、API、充电量和会话数据提供可能性的表单。',
    sections: [
      { title: '充电基础设施', items: ['充电运营商名称', '充电器数量', '快速充电器数量', '月充电量'] },
      { title: '数据联动', items: ['OCPP 支持', 'API 提供可能性', '充电会话数据提供可能性'] },
      { title: '使用目的', items: ['Charging Intelligence 构建', 'EV Carbon Reduction 计算', 'MRV Dataset 候选生成'] },
    ],
  },
  'executive-one-pager': {
    ...documents.en['executive-one-pager'],
    label: '高管一页摘要',
    applyLabel: '输入 Pilot 咨询信息',
    summary: '用于在 30 秒内说明 ZENOV 核心价值的一页高管摘要。',
    sections: [
      { title: '我们做什么', items: ['AI 驱动的 ESG 平台', 'Carbon MRV 平台', 'Taxi Carbon Platform', 'Factory Intelligence Platform'] },
      { title: '客户获得什么', items: ['ESG Score', 'Carbon Score', 'Carbon Project 候选', '政府项目审查', 'EV 转换审查', '能源节减审查'] },
      { title: '一句话信息', items: ['将现有制造 KPI 扩展为 ESG KPI 的数据平台'] },
    ],
  },
  nda: {
    ...documents.en.nda,
    label: '保密协议',
    applyLabel: '输入 NDA 状态',
    summary: '在共享资料、车辆数据、工厂数据或充电数据前需要的保密文件。',
    sections: [
      { title: '对象', items: ['出租车协会', '出租车公司', '工厂', '充电运营商', '战略合作伙伴'] },
      { title: '目的', items: ['资料共享', '车辆数据共享', '工厂数据共享', '充电数据共享', 'Pilot 审查和尽调准备'] },
      { title: '运营原则', items: ['NDA 签署前限制敏感资料共享', '提供资料仅限 Pilot 审查目的', '不分类为 Evidence File'] },
    ],
  },
};

documents.th = {
  'pilot-proposal': {
    ...documents.en['pilot-proposal'],
    label: 'ข้อเสนอ Pilot',
    applyLabel: 'กรอกใบสมัคร Pilot',
    summary: 'เอกสารข้อเสนอที่อธิบายวัตถุประสงค์ของ ZENOV ขอบเขตการวินิจฉัย และผลลัพธ์ที่คาดหวัง',
    sections: [
      { title: 'ปัญหาปัจจุบัน', items: ['เอกสาร ESG กระจัดกระจาย', 'ข้อมูลคาร์บอนยังไม่เชื่อมกับข้อมูลปฏิบัติการ', 'การเตรียม Scope 3 และโครงการภาครัฐทำได้ยาก'] },
      { title: 'ขอบเขต Pilot', items: ['วินิจฉัยข้อมูล', 'วินิจฉัย ESG', 'ตรวจสอบความเป็นไปได้ Carbon MRV', 'ตรวจสอบ Taxi Carbon Platform', 'ตรวจสอบ Factory Intelligence', 'ตรวจสอบ Charging Intelligence'] },
      { title: 'ผลลัพธ์ที่คาดหวัง', items: ['มองเห็นข้อมูลปฏิบัติการ', 'ตรวจสอบความพร้อม ESG', 'ค้นหาโครงการคาร์บอนที่เป็นไปได้', 'เตรียมเอกสารโครงการภาครัฐ', 'จัดชุดข้อมูลสำหรับนักลงทุนและสถาบันการเงิน'] },
    ],
  },
  'due-diligence-questionnaire': {
    ...documents.en['due-diligence-questionnaire'],
    label: 'แบบสอบถาม Due Diligence รวม',
    applyLabel: 'กรอกแบบฟอร์ม Due Diligence',
    summary: 'แบบสอบถามรวมสำหรับคัดเลือก Pilot ให้คะแนนลีด ตรวจ MRV เปิด Investor Room และค้นหาโครงการคาร์บอน',
    sections: [
      { title: '0. วัตถุประสงค์เอกสาร', items: ['ให้คะแนนลีด', 'จัดลำดับความสำคัญของ Pilot', 'ตรวจความเป็นไปได้ ESG และ Carbon MRV', 'ตรวจความเป็นไปได้ EV transition', 'ตรวจความเป็นไปได้โครงสร้างพื้นฐานชาร์จ', 'ตรวจความเป็นไปได้การเก็บข้อมูลโรงงาน', 'ความเหมาะสมกับโครงการภาครัฐ', 'ความพร้อมเปิด Investor Deal Room', 'ค้นหาโครงการคาร์บอนที่เป็นไปได้'] },
      { title: '1. ข้อมูลบริษัทพื้นฐาน', items: ['ชื่อบริษัท', 'เลขทะเบียนธุรกิจ', 'เลขทะเบียนนิติบุคคล', 'ชื่อผู้แทน', 'ปีที่ก่อตั้ง', 'ที่อยู่สำนักงานใหญ่', 'ที่อยู่สถานประกอบการ', 'เว็บไซต์', 'ประเภทธุรกิจ', 'รายละเอียดธุรกิจหลัก', 'ชื่อผู้ติดต่อ', 'ตำแหน่ง', 'แผนก', 'โทรศัพท์มือถือ', 'อีเมล', 'อำนาจตัดสินใจ'] },
      { title: '2. วัตถุประสงค์การเข้าร่วม Pilot', items: ['สร้างระบบบริหาร ESG', 'วัดปริมาณการปล่อยคาร์บอน', 'เตรียม Carbon MRV', 'ค้นหาโครงการลดคาร์บอน', 'เปลี่ยนเป็น EV', 'สร้างโครงสร้างพื้นฐานชาร์จ', 'ตรวจ Solar และ ESS', 'วินิจฉัย Smart Factory', 'เชื่อมข้อมูล ERP และ MES', 'ลดต้นทุนพลังงาน', 'ตอบโจทย์ Scope 3', 'ตอบโจทย์ CBAM', 'สมัครโครงการภาครัฐ', 'เตรียมข้อเสนอสำหรับนักลงทุนหรือสถาบันการเงิน', 'ช่วงเวลาที่ต้องการเริ่ม Pilot'] },
      { title: '3. NDA และการให้ข้อมูล', items: ['ความพร้อมลงนาม NDA', 'วันที่คาดว่าจะลงนาม NDA', 'ผู้รับผิดชอบ NDA', 'ประเภทข้อมูลที่ให้ได้', 'วิธีส่งมอบข้อมูล', 'API', 'CSV', 'Excel', 'PDF', 'DB Export', 'กรอกด้วยตนเอง'] },
      { title: '4. ขนาดองค์กรและสถานที่', items: ['จำนวนพนักงานทั้งหมด', 'พนักงานผลิต', 'พนักงานบริหาร', 'พนักงานวิจัย', 'จำนวนคนขับ', 'พนักงาน outsource', 'จำนวนโรงงาน', 'จำนวนโรงจอด', 'จำนวนศูนย์โลจิสติกส์', 'จำนวนสาขา', 'จำนวนสถานีชาร์จ', 'พื้นที่ดำเนินงานหลัก'] },
      { title: '5. คำถามสำหรับ Taxi / Mobility', items: ['จำนวนรถทั้งหมด', 'รถ LPG', 'รถดีเซล', 'รถเบนซิน', 'รถ EV', 'รถ Hybrid', 'รถที่เปลี่ยนเป็น EV ได้', 'รถที่จะเปลี่ยนประจำปี', 'ระยะทางเฉลี่ยต่อเดือน', 'ค่าเชื้อเพลิงต่อเดือน', 'ค่าซ่อมบำรุงต่อเดือน', 'พื้นที่วิ่งหลัก', 'การใช้ DTG', 'การใช้ OBD', 'ความพร้อมให้ข้อมูล GPS', 'มีโรงจอดหรือไม่', 'ติดตั้งเครื่องชาร์จได้หรือไม่', 'ติดตั้ง Solar ได้หรือไม่', 'ติดตั้ง ESS ได้หรือไม่', 'ขนาดหม้อแปลง', 'กำลังไฟตามสัญญา'] },
      { title: '6. คำถามสำหรับโรงงาน / ผู้ผลิต', items: ['สินค้า', 'ปริมาณผลิตต่อเดือน', 'วัตถุดิบหลัก', 'กระบวนการหลัก', 'จำนวนอุปกรณ์', 'จำนวนไลน์', 'เวลาทำงาน', 'อัตราการเดินเครื่องเฉลี่ย', 'การใช้ ERP', 'การใช้ MES', 'ความเป็นไปได้การเชื่อมข้อมูล', 'การใช้ไฟฟ้ารายเดือน', 'ค่าไฟรายเดือน', 'การใช้ก๊าซรายเดือน', 'การใช้เชื้อเพลิงรายเดือน', 'ช่วงเวลา peak power', 'มี smart meter หรือไม่'] },
      { title: '7. คำถามสำหรับ Charging Operator / CPO', items: ['จำนวนเครื่องชาร์จทั้งหมด', 'จำนวน fast charger', 'จำนวน slow charger', 'พื้นที่ดำเนินงาน', 'ปริมาณชาร์จเฉลี่ยต่อเดือน', 'จำนวน charging session ต่อเดือน', 'ช่วง peak time', 'จำนวนสถานีชาร์จ', 'รองรับ OCPP หรือไม่', 'ให้ API ได้หรือไม่', 'เวลาเริ่มชาร์จ', 'เวลาสิ้นสุดชาร์จ', 'ปริมาณชาร์จ kWh', 'Vehicle ID', 'Charger ID', 'User ID แบบ anonymized', 'ข้อมูลตำแหน่ง', 'Fault logs', 'ข้อมูลราคา'] },
      { title: '8. สถานะข้อมูล ESG / Carbon', items: ['สถานะรายงาน ESG', 'มีผู้รับผิดชอบ ESG', 'ประสบการณ์ประเมิน ESG', 'คำขอ ESG จากลูกค้า', 'ไฟฟ้า', 'ก๊าซ', 'เชื้อเพลิง', 'น้ำ', 'ของเสีย', 'วัตถุดิบ', 'โลจิสติกส์', 'ยานพาหนะ', 'ซัพพลายเชน', 'Scope 1', 'Scope 2', 'Scope 3', 'สถานะคำนวณ emission', 'GHG Protocol', 'ISO 14064', 'K-ESG'] },
      { title: '9. Scope 3 / Supply Chain', items: ['ลูกค้าหลัก', 'ส่งมอบให้บริษัทขนาดใหญ่หรือไม่', 'มีการส่งออกหรือไม่', 'ประเทศที่ส่งออก', 'คำขอข้อมูล ESG จากลูกค้า', 'ผลกระทบ CBAM', 'ส่งออกไป EU หรือไม่', 'อยู่ใน global supply chain หรือไม่'] },
      { title: '10. IoT / Sensor / Data Infrastructure', items: ['มิเตอร์ไฟฟ้า', 'Smart meter', 'Temperature sensor', 'Humidity sensor', 'Pressure sensor', 'Vibration sensor', 'Flow meter', 'GPS', 'OBD', 'DTG', 'PLC', 'CCTV', 'Modbus', 'MQTT', 'OPC-UA', 'REST API', 'CSV Export', 'บันทึกด้วยมือ'] },
      { title: '11. ความพร้อมด้าน AI', items: ['สถานะการใช้ AI ปัจจุบัน', 'พยากรณ์การผลิต', 'พยากรณ์คุณภาพ', 'พยากรณ์อุปกรณ์เสีย', 'เพิ่มประสิทธิภาพพลังงาน', 'เพิ่มประสิทธิภาพคาร์บอน', 'วิเคราะห์รูปแบบการขับ', 'พยากรณ์ความต้องการชาร์จ', 'ทำรายงาน ESG อัตโนมัติ', 'ทำ MRV อัตโนมัติ'] },
      { title: '12. ความเหมาะสมของโครงการภาครัฐ', items: ['เคยทำโครงการภาครัฐใน 3 ปีล่าสุดหรือไม่', 'Smart factory', 'ESG', 'Carbon neutrality', 'EV', 'Charging station', 'RE100', 'AI', 'Data voucher', 'โครงการ SME', 'โครงการกระทรวงอุตสาหกรรม', 'โครงการกระทรวงสิ่งแวดล้อม', 'โครงการท้องถิ่น', 'Business plan', 'Technical proposal', 'ESG diagnosis', 'Data diagnosis', 'Carbon reduction diagnosis'] },
      { title: '13. ความพร้อมสำหรับนักลงทุน / สถาบันการเงิน', items: ['รายได้ล่าสุด 2023', 'รายได้ล่าสุด 2024', 'รายได้ล่าสุด 2025', 'ความพร้อมให้ข้อมูลการเงิน', 'ตรวจการลงทุนอุปกรณ์', 'ตรวจ EV transition finance', 'ตรวจ charging infrastructure finance', 'ตรวจ Solar และ ESS', 'ตรวจโครงการลดคาร์บอน', 'ตรวจ ESG finance', 'ตรวจการจับคู่เงินสนับสนุนภาครัฐ'] },
      { title: '14. โครงการคาร์บอนที่เป็นไปได้', items: ['EV transition', 'สร้างสถานีชาร์จ', 'Solar', 'ESS', 'เพิ่มประสิทธิภาพพลังงานโรงงาน', 'Smart factory', 'ลด methane', 'Biochar', 'Waste-to-energy', 'ลด Scope 3', 'ตอบโจทย์ RE100', 'เวลาที่คาดว่าจะเริ่มโครงการ'] },
      { title: '15. เอกสารแนบที่ให้ได้', items: ['ใบทะเบียนธุรกิจ', 'Company profile', 'ESG report', 'บิลค่าไฟ', 'บิลก๊าซ', 'รายการรถ', 'ข้อมูลระยะทาง', 'ข้อมูลชาร์จ', 'ข้อมูลการผลิต', 'ERP Export', 'MES Export', 'API document', 'ผังโรงงาน', 'แบบโรงจอด', 'แบบสถานีชาร์จ'] },
      { title: '16. ความยินยอมเข้าร่วม Pilot', items: ['ยินยอมให้เข้าพื้นที่', 'ยินยอมให้ข้อมูล', 'ยินยอมลงนาม NDA', 'ความตั้งใจเข้าร่วม Pilot'] },
      { title: '17. พื้นที่ประเมินภายใน', items: ['Lead Score', 'ESG Readiness Score', 'MRV Readiness Score', 'Carbon Potential Score', 'Scope 3 Potential Score', 'Government Funding Score', 'Investment Readiness Score', 'EV Transition Score', 'Charging Potential Score', 'Data Quality Score', 'Overall Opportunity Score', 'Pilot Tier', 'Reviewer', 'Review Date', 'Next Action'] },
      { title: '18. ข้อสังเกตทางกฎหมาย', items: ['แบบสอบถามนี้ใช้เพื่อประเมินผู้สมัคร Pilot และวิเคราะห์ข้อมูลเบื้องต้น', 'ผลลัพธ์ทั้งหมดต้องตัดสินหลังตรวจข้อมูลจริง สัญญาแยกต่างหาก due diligence ภาคสนาม การตรวจสอบโดยบุคคลที่สาม และการตรวจตามกฎหมาย', 'การกรอกหรือส่งเอกสารนี้ไม่ใช่คำมั่นเรื่องการขายผลิตภัณฑ์การเงิน การคัดเลือกโครงการ การออก carbon credit หรือการอนุมัติโครงการ'] },
    ],
  },
  'data-request-checklist': {
    ...documents.en['data-request-checklist'],
    label: 'เช็กลิสต์ขอข้อมูล',
    applyLabel: 'กรอกเช็กลิสต์ข้อมูล',
    summary: 'เช็กลิสต์สำหรับขอข้อมูล Taxi โรงงาน และสถานีชาร์จจากผู้สมัคร Pilot',
    sections: [
      { title: 'ข้อมูล Taxi', items: ['รายการรถ', 'ชนิดเชื้อเพลิง', 'ระยะทางวิ่ง', 'สถานะ LPG', 'ข้อมูลโรงจอด', 'จำนวนคนขับ', 'ระยะทางเฉลี่ยต่อเดือน'] },
      { title: 'ข้อมูลโรงงาน', items: ['บิลค่าไฟ', 'ปริมาณการผลิต', 'ข้อมูล ERP', 'ข้อมูล MES', 'ข้อมูลอุปกรณ์', 'ผังโรงงาน', 'ต้นทุนพลังงาน'] },
      { title: 'ข้อมูลสถานีชาร์จ', items: ['ปริมาณชาร์จ', 'รายการเครื่องชาร์จ', 'OCPP logs', 'เอกสาร API', 'ข้อมูล charging session', 'fault logs'] },
    ],
  },
  'pilot-application': {
    ...documents.en['pilot-application'],
    label: 'ใบสมัคร Pilot',
    applyLabel: 'กรอกใบสมัคร Pilot',
    summary: 'แบบฟอร์มเว็บสำหรับกรอกข้อมูลพื้นฐานของผู้สมัคร Pilot',
    sections: [
      { title: 'ข้อมูลใบสมัครพื้นฐาน', items: ['ชื่อบริษัท', 'ผู้ติดต่อ', 'โทรศัพท์', 'อีเมล', 'ประเภทธุรกิจ', 'พื้นที่'] },
      { title: 'ความสนใจ Pilot', items: ['ESG', 'Carbon MRV', 'Taxi Carbon', 'Factory Intelligence', 'Charging', 'โครงการภาครัฐ'] },
      { title: 'สถานะการตรวจสอบ', items: ['สถานะ NDA', 'ความพร้อมให้ข้อมูล', 'บันทึกการตรวจสอบ'] },
    ],
  },
  'taxi-pilot-survey': {
    ...documents.en['taxi-pilot-survey'],
    label: 'แบบสำรวจ Taxi Pilot',
    applyLabel: 'กรอกแบบสำรวจ Taxi',
    summary: 'แบบสำรวจเพื่อเก็บข้อมูลรถ คนขับ โรงจอด และพื้นที่ชาร์จที่เป็นไปได้จากสหกรณ์หรือบริษัทแท็กซี่',
    sections: [
      { title: 'สถานะรถ', items: ['ชื่อสหกรณ์', 'จำนวนรถทั้งหมด', 'รถ LPG', 'รถ EV', 'รถที่เปลี่ยนเป็น EV ได้', 'จำนวนคนขับ'] },
      { title: 'สถานะโครงสร้างพื้นฐาน', items: ['มีโรงจอดหรือไม่', 'พื้นที่ที่เป็นไปได้สำหรับสถานีชาร์จ', 'ระยะทางเฉลี่ยต่อเดือน', 'ค่าเชื้อเพลิงเฉลี่ยต่อเดือน'] },
      { title: 'การใช้งาน', items: ['วิเคราะห์ความเป็นไปได้ EV transition', 'ตรวจสอบพื้นที่สถานีชาร์จ', 'ค้นหา Taxi Carbon MRV ที่เป็นไปได้'] },
    ],
  },
  'factory-assessment': {
    ...documents.en['factory-assessment'],
    label: 'ตรวจสถานที่บริษัทแท็กซี่',
    applyLabel: 'กรอกการตรวจสถานที่บริษัทแท็กซี่',
    summary: 'แบบตรวจสถานที่สำหรับอู่ซ่อม ล้างรถ สำนักงาน ลานจอด/พื้นที่ ไฟฟ้า หลังคา ESG และข้อมูลคาร์บอนของบริษัทแท็กซี่',
    sections: [
      { title: 'ข้อมูลสถานที่พื้นฐาน', items: ['ชื่อสถานที่', 'ประเภทสถานที่', 'พื้นที่บริหารจัดการ', 'โครงสร้างอาคาร'] },
      { title: 'อุปกรณ์และพลังงาน', items: ['การใช้ ERP/MES', 'กำลังไฟฟ้าที่รับเข้า', 'วัสดุหลังคา/เพดาน', 'การใช้ไฟฟ้ารายเดือน', 'ค่าไฟรายเดือน'] },
      { title: 'ข้อมูลคาร์บอนและ ESG', items: ['ความพร้อมข้อมูลคาร์บอน', 'ความสนใจ ESG'] },
    ],
  },
  'charging-partner-form': {
    ...documents.en['charging-partner-form'],
    label: 'แบบฟอร์ม Charging Partner',
    applyLabel: 'กรอกแบบฟอร์ม Charging Partner',
    summary: 'แบบฟอร์มตรวจจำนวนเครื่องชาร์จ OCPP API ปริมาณชาร์จ และความพร้อมข้อมูล session',
    sections: [
      { title: 'โครงสร้างพื้นฐานชาร์จ', items: ['ชื่อผู้ให้บริการชาร์จ', 'จำนวนเครื่องชาร์จ', 'จำนวน fast charger', 'ปริมาณชาร์จรายเดือน'] },
      { title: 'การเชื่อมต่อข้อมูล', items: ['รองรับ OCPP', 'ให้ API ได้หรือไม่', 'ให้ข้อมูล charging session ได้หรือไม่'] },
      { title: 'การใช้งาน', items: ['สร้าง Charging Intelligence', 'คำนวณ EV Carbon Reduction', 'สร้าง MRV Dataset ที่เป็นไปได้'] },
    ],
  },
  'executive-one-pager': {
    ...documents.en['executive-one-pager'],
    label: 'Executive One Pager',
    applyLabel: 'กรอกข้อมูลปรึกษา Pilot',
    summary: 'เอกสารสรุปหนึ่งหน้าเพื่ออธิบายคุณค่าหลักของ ZENOV ภายใน 30 วินาที',
    sections: [
      { title: 'เราทำอะไร', items: ['แพลตฟอร์ม ESG ด้วย AI', 'แพลตฟอร์ม Carbon MRV', 'Taxi Carbon Platform', 'Factory Intelligence Platform'] },
      { title: 'ลูกค้าได้อะไร', items: ['ESG Score', 'Carbon Score', 'Carbon Project ที่เป็นไปได้', 'ตรวจสอบโครงการภาครัฐ', 'ตรวจ EV transition', 'ตรวจการลดพลังงาน'] },
      { title: 'ข้อความหนึ่งบรรทัด', items: ['แพลตฟอร์มข้อมูลที่ขยาย KPI การผลิตเดิมให้เป็น ESG KPI'] },
    ],
  },
  nda: {
    ...documents.en.nda,
    label: 'NDA',
    applyLabel: 'กรอกสถานะ NDA',
    summary: 'เอกสารรักษาความลับที่จำเป็นก่อนแบ่งปันเอกสาร ข้อมูลรถ ข้อมูลโรงงาน หรือข้อมูลชาร์จ',
    sections: [
      { title: 'กลุ่มเป้าหมาย', items: ['สหกรณ์แท็กซี่', 'บริษัทแท็กซี่', 'โรงงาน', 'ผู้ให้บริการชาร์จ', 'พาร์ทเนอร์เชิงกลยุทธ์'] },
      { title: 'วัตถุประสงค์', items: ['แบ่งปันเอกสาร', 'แบ่งปันข้อมูลรถ', 'แบ่งปันข้อมูลโรงงาน', 'แบ่งปันข้อมูลชาร์จ', 'เตรียม Pilot review และ due diligence'] },
      { title: 'หลักปฏิบัติ', items: ['จำกัดข้อมูลอ่อนไหวก่อนลงนาม NDA', 'ใช้ข้อมูลที่ได้รับเฉพาะเพื่อ Pilot review', 'ไม่จัดเป็น Evidence File'] },
    ],
  },
};

export default function FileViewerPage() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const [lang, setLang] = useState<Lang>('ko');
  const [sessionReady, setSessionReady] = useState(false);
  const [hasPortalSession, setHasPortalSession] = useState(false);

  useEffect(() => {
    const savedLang =
      window.localStorage.getItem('zenov_admin_dashboard_lang') ||
      window.localStorage.getItem('zenov_partner_login_lang');
    if (savedLang === 'ko' || savedLang === 'en' || savedLang === 'zh' || savedLang === 'th') {
      setLang(savedLang);
    }
    const sessionActive = window.sessionStorage.getItem(FILE_ADMIN_SESSION_KEY) === 'active';
    const role = window.sessionStorage.getItem(FILE_ADMIN_ROLE_KEY) || '';
    const normalizedRole = role.toLowerCase();
    setHasPortalSession(sessionActive && (normalizedRole.includes('admin') || normalizedRole.includes('partner')));
    setSessionReady(true);
  }, []);

  useEffect(() => {
    window.localStorage.setItem('zenov_admin_dashboard_lang', lang);
    window.localStorage.setItem('zenov_partner_login_lang', lang);
  }, [lang]);

  const t = uiText[lang];
  const doc = documents[lang][slug];

  function printPdf() {
    window.setTimeout(() => window.print(), 80);
  }

  if (!sessionReady) {
    return (
      <main className="portal-shell file-reader-shell">
        <section className="portal-card">
          <p className="eyebrow">LOADING</p>
          <h1>세션 확인 중</h1>
          <p className="muted">파트너 또는 관리자 로그인 세션을 확인하고 있습니다.</p>
        </section>
      </main>
    );
  }

  if (!hasPortalSession) {
    return (
      <main className="portal-shell file-reader-shell">
        <section className="portal-card">
          <p className="eyebrow">LOGIN REQUIRED</p>
          <h1>파트너 로그인이 필요합니다</h1>
          <p className="muted">파트너 파일은 /partner-login에서 파트너 코드로 로그인한 뒤 열람할 수 있습니다. 관리자는 /admin-login에서도 열람할 수 있습니다.</p>
          <Link href="/partner-login" className="primary-link">
            파트너 로그인
          </Link>
          <Link href="/admin-login" className="secondary-button">
            관리자 로그인
          </Link>
        </section>
      </main>
    );
  }

  if (!doc) {
    return (
      <main className="portal-shell file-reader-shell">
        <section className="portal-card">
          <p className="eyebrow">{t.reader}</p>
          <h1>{t.missingTitle}</h1>
          <p className="muted">{t.missingDesc}</p>
          <Link href="/partner-login" className="primary-link">
            {t.back}
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="portal-shell file-reader-shell">
      <div className="language-tabs" aria-label={t.language}>
        <span className="language-tabs-title">{t.language}</span>
        {languageOptions.map((option) => (
          <button
            key={option.code}
            type="button"
            className={lang === option.code ? 'language-tab active' : 'language-tab'}
            onClick={() => setLang(option.code)}
            aria-pressed={lang === option.code}
          >
            {option.label}
          </button>
        ))}
      </div>

      <section className="portal-card document-reader-hero">
        <p className="eyebrow">{t.reader}</p>
        <h1>{doc.label}</h1>
        <p className="muted">{doc.summary}</p>
        <div className="file-actions">
          <Link href="/partner-login" className="secondary-button">
            {t.back}
          </Link>
          <Link href={doc.applyHref} className="secondary-button">
            {doc.applyLabel}
          </Link>
          <button type="button" className="secondary-button" onClick={printPdf}>
            {t.printPdf}
          </button>
          <a href={doc.href} className="secondary-button">
            {t.openOriginal}
          </a>
        </div>
        <div className="file-url-box">{doc.filename}</div>
      </section>

      <section className="governance-banner">
        <strong>Governance Guard</strong>
        <span>DOCUMENT_TYPE=PILOT_ACQUISITION_TEMPLATE</span>
        <span>EVIDENCE_FILE=false</span>
        <span>PRODUCTION_READY_TRIGGER=false</span>
        <span>COMMERCIAL_READY_TRIGGER=false</span>
      </section>

      <section className="portal-card">
        <p className="muted">{t.notEvidence}</p>
      </section>

      <section className="document-reader-grid">
        {doc.sections.map((section) => (
          <article key={section.title} className="portal-card document-section-card">
            <h2>{section.title}</h2>
            <ul className="document-list">
              {section.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        ))}
      </section>
    </main>
  );
}
