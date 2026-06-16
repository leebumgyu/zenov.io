'use client';

import { createClient } from '@supabase/supabase-js';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useMemo, useRef, useState } from 'react';

const LEGACY_ADMIN_CODE = 'ZENOV-PILOT-ADMIN-2026';
const CEO_ADMIN_CODE = 'ZENOV-ceo-ADMIN-2026';
const DASHBOARD_FILE_ADMIN_CODE = '48339446';
const ANSAN_PARTNER_LOGIN_CODE = 'ANSAN_CEO_001';
const ANSAN_QR_PARTNER_CODE = 'ANSAN_TRANS';
const ANSAN_REFERRAL_CODE = 'ANSAN-001';
const ANSAN_COMPANY_ID = 'ANSAN001';
const SESSION_KEY = 'zenov_pilot_admin_session';
const SESSION_ROLE_KEY = 'zenov_pilot_session_role';
const SESSION_PARTNER_CODE_KEY = 'zenov_pilot_session_partner_code';
const SESSION_PARTNER_NAME_KEY = 'zenov_pilot_session_partner_name';

type FieldType = 'text' | 'email' | 'number' | 'textarea' | 'select' | 'multiselect';

type Field = {
  name: string;
  label: string;
  type?: FieldType;
  options?: string[];
  placeholder?: string;
};

type FormConfig = {
  title: string;
  subtitle: string;
  route: string;
  storageKey: string;
  tableName: string;
  fields: Field[];
};

type SavedRecord = {
  id: string;
  status: string;
  created_at: string;
  updated_at: string;
  metadata: {
    document_type: 'PILOT_ACQUISITION_FORM';
    evidence_file: false;
    production_ready_trigger: false;
    commercial_ready_trigger: false;
  };
  values: Record<string, string | string[]>;
};

type CdKeyRecord = {
  id: string;
  cd_key: string;
  organization_name: string;
  recipient_name: string;
  recipient_email: string;
  account_type: string;
  license_scope: string[];
  expires_at: string;
  status: 'active' | 'revoked';
  created_at: string;
  metadata: {
    document_type: 'PILOT_ACCESS_CODE';
    evidence_file: false;
    production_ready_trigger: false;
    commercial_ready_trigger: false;
  };
};

type ReferralCodeRecord = {
  id: string;
  referral_code: string;
  code_scope?: 'PARTNER' | 'DRIVER';
  owner_partner_code?: string;
  parent_partner_code?: string;
  parent_driver_id?: string;
  issued_by_login_code?: string;
  reward_basis?: 'organization_scale' | 'referral_count';
  reward_policy_label?: string;
  hub_name: string;
  partner_name: string;
  partner_email: string;
  partner_type: string;
  region: string;
  status: 'pending_approval' | 'approved' | 'disabled';
  db_delivery_status?: string;
  db_error_message?: string;
  created_at: string;
  approved_at?: string;
  metadata: {
    document_type: 'PILOT_REFERRAL_CODE';
    evidence_file: false;
    production_ready_trigger: false;
    commercial_ready_trigger: false;
  };
};

type DeliveryRecord = {
  id: string;
  recipient_name: string;
  recipient_email: string;
  organization_name: string;
  selected_files: string[];
  created_at: string;
  metadata: {
    document_type: 'PILOT_FILE_DELIVERY_MANIFEST';
    evidence_file: false;
    production_ready_trigger: false;
    commercial_ready_trigger: false;
  };
};

type AdminLang = 'ko' | 'en' | 'zh' | 'th';

const adminLanguageOptions: Array<{ code: AdminLang; label: string }> = [
  { code: 'ko', label: '🇰🇷 한국어' },
  { code: 'en', label: '🇺🇸 English' },
  { code: 'zh', label: '🇨🇳 中文' },
  { code: 'th', label: '🇹🇭 ภาษาไทย' },
];

const adminI18n = {
  ko: {
    language: '언어 선택',
    brand: 'ZENOV Pilot Portal',
    nav_dashboard: '대시보드',
    nav_pilot: '시범 적용',
    nav_taxi: '택시',
    nav_factory: '시설 실사',
    nav_charging: '충전',
    nav_cd_key: 'CD Key',
    nav_files: '파일',
    eyebrow: 'Pilot Acquisition',
    title: 'ZENOV Pilot 확보 포털',
    desc: 'Taxi, 택시회사 시설, Charging 파트너의 Pilot 신청과 통합 실사 질문지를 입력·저장하고 내부 검토용 PDF 출력 및 Excel 다운로드를 수행합니다.',
    frozen_note: 'Evidence File 아님',
    saved_forms: '저장된 제출서',
    production_ready: 'Production Ready',
    commercial_ready: 'Commercial Ready',
    current_flow: 'Current Flow',
    saved_suffix: '저장',
    delivery_eyebrow: 'PILOT DELIVERY PACKAGE',
    delivery_title: '전달 파일',
    delivery_desc:
      'Pilot 확보에 필요한 제안서, 실사 설문지, 체크리스트, 신청서, 업종별 양식을 포털 안에서 바로 읽고 작성 화면으로 적용할 수 있습니다. 이 파일들은 Pilot Acquisition Template이며 Evidence File이 아닙니다.',
    pdf_print: 'PDF 출력',
    open_apply: '열람 / 작성 적용',
    output_title: 'PDF 출력 / Excel 다운로드',
    output_desc:
      '각 입력 화면에서 저장 후 PDF 인쇄와 CSV 다운로드를 실행할 수 있습니다. 출력물은 Pilot Acquisition Template / Submitted Form이며 Evidence File이 아닙니다.',
    menu_pilot_application: 'Pilot 신청 관리',
    menu_taxi_survey: 'Taxi Pilot Survey',
    menu_factory_assessment: '택시회사 시설 실사',
    menu_charging_partner: 'Charging Partner Form',
    menu_due_diligence: 'Due Diligence Questionnaire',
    menu_data_checklist: 'Data Request Checklist',
    menu_referral_code: '레퍼럴 코드 / 파트너 코드 발급',
    menu_file_delivery: '파일 전달 센터',
    menu_taxi_carbon_proof: 'Taxi Carbon Proof',
    menu_taxi_carbon_dashboard: 'Taxi Carbon OS 대시보드',
    menu_taxi_diagnosis_file: 'Taxi Carbon OS 진단 파일',
    menu_partner_approvals: '파트너 승인 관리',
    menu_partner_dashboard: '파트너 대시보드',
    menu_driver_dashboard: '기사 대시보드',
    dashboard_referral_title: '대시보드 파트너코드 생성',
    dashboard_referral_desc:
      '파트너 유입과 허브별 Pilot 신청을 추적할 수 있는 파트너코드를 즉시 생성합니다. 이 코드는 Evidence가 아니며 상태 전이를 유발하지 않습니다.',
    dashboard_referral_button: '파트너코드 생성',
    dashboard_referral_created: '파트너코드가 생성되었습니다',
    dashboard_referral_approval_note:
      '생성된 코드는 관리자 승인 대기 상태로 저장됩니다. 승인 전에는 하위 기사·차량 데이터 귀속과 정산 가능성 검토가 활성화되지 않습니다.',
    referral_flow_title: '파트너 코드 운영 절차',
    referral_flow_steps: [
      '대표자 또는 조합장 가입',
      '파트너코드 신청',
      '관리자 승인',
      '하위 기사·차량 데이터 연결',
      'EV 전환·충전소·탄소감축 후보 진단',
      '정산 가능성 검토',
    ],
    referral_status_pending_approval: '관리자 승인 대기',
    referral_status_approved: '관리자 승인 완료',
    referral_status_disabled: '비활성',
    referral_title: '레퍼럴 코드 / 파트너 코드 발급',
    referral_desc: '관리자 전용 화면에서 개인 레퍼럴 코드와 조직용 파트너 코드를 분리 발급·조회합니다. 이 코드는 Pilot 유입 추적용이며 CD Key가 아닙니다.',
    referral_button: '코드 발급',
    referral_created: '코드가 발급되었습니다',
    referral_hub_label: 'Hub / 지역 파트너명',
    referral_partner_label: '추천 파트너명',
    referral_email_label: '파트너 이메일',
    referral_type_label: '파트너 유형',
    referral_region_label: '지역',
    referral_region_placeholder: '예: 경기남부',
    referral_code_scope_label: '코드 유형',
    referral_scope_partner: '조직용 파트너 코드',
    referral_scope_driver: '일반 회원 레퍼럴 코드',
    referral_driver_id_label: '추천 기사 ID',
    referral_partner_policy_note: '조직용 파트너 코드는 관리자 승인 후 하위 기사·차량 귀속 검토가 활성화됩니다.',
    referral_driver_policy_note: '일반 회원 레퍼럴 코드는 지인 가입 추적용으로 즉시 활성화되며 포인트/혜택 후보 산정에 사용됩니다.',
    referral_scope_preview: '코드 유형',
    referral_download_latest: '최신 코드 파일 다운로드',
    referral_preview_title: '발급된 코드',
    referral_preview_desc: '브라우저 로컬 저장소에 보관되며, Supabase 환경이 설정되어 있으면 DB에도 저장됩니다. CD Key와 별도 원장으로 관리됩니다.',
    referral_empty: '발급된 코드가 없습니다.',
    referral_join_eyebrow: 'ZENOV 가입 및 혜택 안내',
    referral_join_title: '택시 데이터를 혜택 기회로 바꾸는 플랫폼',
    referral_join_why_title: '왜 가입해야 하나요?',
    referral_join_why_desc:
      'ZENOV는 기사님의 운행 데이터를 분석하여 연료비 절감 가능성, 전기차 전환 시 절감액, 충전·정비 혜택 후보, 정부 지원사업 정보를 확인할 수 있도록 돕습니다.',
    referral_join_benefits_title: '가입하면 받을 수 있는 혜택',
    referral_join_benefits: [
      ['연료비 절감 분석', '현재 차량 기준으로 얼마를 절약할 수 있는지 확인합니다.'],
      ['EV 전환 진단', '전기차 전환 시 예상 절감액과 우선순위를 확인합니다.'],
      ['충전 및 정비 혜택', '제휴 충전소와 제휴 정비소 할인 혜택 후보를 안내합니다.'],
      ['정부 지원사업 정보', 'EV 보조금, 충전 인프라 지원사업 등 관련 정보를 제공합니다.'],
      ['탄소감축 프로젝트 후보 참여 기회', '운행 데이터가 충분히 확보될 경우 MRV 가능성 검토와 후보 진단을 진행합니다.'],
    ],
    referral_join_disclaimer: '탄소배출권 발급이나 수익을 보장하지 않습니다.',
    referral_join_invite_title: '기사 추천 혜택',
    referral_join_invite_desc:
      '일반 회원 레퍼럴 코드가 발급됩니다. 지인을 초대하면 포인트 적립, 충전 할인, 정비 할인 등의 혜택 후보로 사용할 수 있습니다.',
    referral_join_steps_title: '가입 절차',
    referral_join_steps: ['회원가입', '추천코드 입력 선택', '차량 등록', '운행 데이터 연결', '절감액 리포트 확인'],
    referral_join_goal_title: 'ZENOV의 목표',
    referral_join_goal_desc:
      '복잡한 ESG 플랫폼이 아니라 기사님과 회사가 얼마를 절감하고 어떤 사업 기회를 만들 수 있는지 데이터로 보여주는 플랫폼입니다.',
    form_status_label: '상태값',
    status_draft: '작성 중',
    status_submitted: '제출 완료',
    status_under_review: '검토 중',
    status_nda_required: 'NDA 필요',
    status_pilot_candidate: '파일럿 후보',
    status_rejected: '보류 / 반려',
    form_save: '저장',
    form_internal_pdf: '내부 검토용 PDF 출력',
    form_customer_pdf: '고객 제출용 PDF 출력',
    form_excel: 'Excel 다운로드',
    form_select: '선택',
    form_submitted_preview: '제출 양식 미리보기',
    form_not_evidence: '출력 PDF는 Evidence가 아니며 운영 로그 검증 전까지 상태 전이를 유발하지 않습니다.',
    form_latest_saved: '최근 저장',
    form_no_saved: '저장된 제출서가 없습니다.',
    form_save_success: '저장되었습니다. 이 제출 데이터는 Evidence File이 아닙니다.',
    form_taxi_save_success: '저장되었습니다. Taxi Carbon OS 진단 입력 데이터로도 연결되었습니다. 이 제출 데이터는 Evidence File이 아닙니다.',
    form_print_suffix: '출력 모드입니다. 브라우저 인쇄에서 PDF 저장을 선택하세요.',
    records_suffix: '건',
    preview_table: '테이블',
    preview_status: '상태',
    preview_document_type: '문서 유형',
    preview_evidence_file: 'Evidence File',
    data_checklist_title: '파일 다운로드 체크리스트',
    data_checklist_desc:
      '아래 파일을 내려받아 작성한 뒤 Pilot 후보에게 전달하거나 내부 검토 자료로 사용하세요. 이 파일들은 Evidence가 아니며, 실제 운영 증적 제출 전까지 상태 전이를 유발하지 않습니다.',
    taxi_diagnosis_file_link: 'Taxi Carbon OS 진단 파일',
    taxi_dashboard_link: 'Taxi Carbon OS 대시보드',
    delivery_org_label: '수신 회사 / 조합명',
    delivery_recipient_label: '수신자명',
    delivery_email_label: '수신자 이메일',
    delivery_files_label: '전달 파일',
    delivery_download: '다운로드',
    delivery_create_manifest: '전달 매니페스트 생성',
    delivery_created_message: '전달 매니페스트가 생성되었습니다. 실제 외부 발송은 별도 이메일/메신저에서 수행하세요.',
    delivery_preview_title: '전달 미리보기',
    delivery_preview_desc: '외부 이메일 전송 기능은 연결하지 않았습니다. 다운로드한 파일과 매니페스트를 별도로 전달하세요.',
    delivery_latest_manifest: '최근 매니페스트',
    delivery_empty_manifest: '생성된 전달 매니페스트가 없습니다.',
    delivery_preview_recipient: '수신자',
    delivery_preview_email: '이메일',
    delivery_preview_organization: '회사 / 조합',
    delivery_preview_selected_files: '선택된 파일',
    partner_type_taxi_union: '택시조합',
    partner_type_taxi_company: '법인택시',
    partner_type_factory: '택시회사 시설',
    partner_type_charging_operator: '충전사업자',
    partner_type_consultant: '컨설턴트',
    partner_type_regional_partner: '지역 파트너',
    login_eyebrow: 'ZENOV Partner Access',
    login_title: '파트너 로그인',
    login_desc: '파트너 코드를 입력하면 Pilot Dashboard로 이동합니다.',
    login_code_label: '파트너 코드',
    login_button: '로그인',
    login_error: '파트너 코드가 일치하지 않습니다.',
    login_required_title: '파트너 로그인이 필요합니다',
    login_required_desc: 'Pilot 신청과 질문지 데이터는 파트너 세션에서만 입력할 수 있습니다.',
    code_placeholder: '파트너 코드를 입력하세요',
  },
  en: {
    language: 'Language',
    brand: 'ZENOV Pilot Portal',
    nav_dashboard: 'Dashboard',
    nav_pilot: 'Pilot',
    nav_taxi: 'Taxi',
    nav_factory: 'Facility Audit',
    nav_charging: 'Charging',
    nav_cd_key: 'CD Key',
    nav_files: 'Files',
    eyebrow: 'Pilot Acquisition',
    title: 'ZENOV Pilot Acquisition Portal',
    desc: 'Enter, save, print PDF, and export Excel files for Taxi, Taxi Company Facility, and Charging partner pilot applications and due diligence questionnaires.',
    frozen_note: 'Not an Evidence File',
    saved_forms: 'Saved Submissions',
    production_ready: 'Production Ready',
    commercial_ready: 'Commercial Ready',
    current_flow: 'Current Flow',
    saved_suffix: 'saved',
    delivery_eyebrow: 'PILOT DELIVERY PACKAGE',
    delivery_title: 'Delivery Files',
    delivery_desc:
      'Read and apply pilot proposals, due diligence questionnaires, checklists, applications, and sector forms directly inside the portal. These are Pilot Acquisition Templates, not Evidence Files.',
    pdf_print: 'Print PDF',
    open_apply: 'Read / Apply',
    output_title: 'PDF Print / Excel Download',
    output_desc:
      'After saving each form, you can print to PDF and download CSV. Outputs are Pilot Acquisition Templates / Submitted Forms, not Evidence Files.',
    menu_pilot_application: 'Pilot Applications',
    menu_taxi_survey: 'Taxi Pilot Survey',
    menu_factory_assessment: 'Taxi Company Facility Audit',
    menu_charging_partner: 'Charging Partner Form',
    menu_due_diligence: 'Due Diligence Questionnaire',
    menu_data_checklist: 'Data Request Checklist',
    menu_referral_code: 'Issue Referral / Partner Code',
    menu_file_delivery: 'File Delivery Center',
    menu_taxi_carbon_proof: 'Taxi Carbon Proof',
    menu_taxi_carbon_dashboard: 'Taxi Carbon OS Dashboard',
    menu_taxi_diagnosis_file: 'Taxi Carbon OS Diagnosis File',
    menu_partner_approvals: 'Partner Approval Management',
    menu_partner_dashboard: 'Partner Dashboard',
    menu_driver_dashboard: 'Driver Dashboard',
    dashboard_referral_title: 'Dashboard Partner Code Generator',
    dashboard_referral_desc:
      'Generate a partner code for partner attribution and hub-level pilot application tracking. This code is not Evidence and does not trigger status transitions.',
    dashboard_referral_button: 'Generate Partner Code',
    dashboard_referral_created: 'Partner code generated',
    dashboard_referral_approval_note:
      'Generated codes are stored as pending admin approval. Sub-driver and vehicle data attribution and settlement feasibility review remain inactive until approval.',
    referral_flow_title: 'Partner Code Operating Flow',
    referral_flow_steps: [
      'Representative or union leader signs up',
      'Partner code request',
      'Admin approval',
      'Sub-driver and vehicle data connection',
      'EV transition, charging site, and carbon reduction candidate diagnosis',
      'Settlement feasibility review',
    ],
    referral_status_pending_approval: 'Pending admin approval',
    referral_status_approved: 'Admin approved',
    referral_status_disabled: 'Disabled',
    referral_title: 'Issue Referral / Partner Code',
    referral_desc: 'In this admin-only screen, personal referral codes and organization partner codes are issued and viewed separately. These codes are for pilot attribution and are not CD Keys.',
    referral_button: 'Issue Code',
    referral_created: 'Code issued',
    referral_hub_label: 'Hub / Regional Partner Name',
    referral_partner_label: 'Referring Partner Name',
    referral_email_label: 'Partner Email',
    referral_type_label: 'Partner Type',
    referral_region_label: 'Region',
    referral_region_placeholder: 'Example: Southern Gyeonggi',
    referral_code_scope_label: 'Code Type',
    referral_scope_partner: 'Organization Partner Code',
    referral_scope_driver: 'General Member Referral Code',
    referral_driver_id_label: 'Referring Driver ID',
    referral_partner_policy_note:
      'Organization partner codes require admin approval before sub-driver and vehicle attribution review is activated.',
    referral_driver_policy_note:
      'General member referral codes are activated immediately for friend signup tracking and point/benefit candidate calculation.',
    referral_scope_preview: 'Code Type',
    referral_download_latest: 'Download Latest Code File',
    referral_preview_title: 'Issued Codes',
    referral_preview_desc: 'Stored in browser local storage and, when Supabase is configured, also saved to the DB. Managed separately from CD Keys.',
    referral_empty: 'No codes have been issued.',
    referral_join_eyebrow: 'ZENOV Signup & Benefits Guide',
    referral_join_title: 'A platform that turns taxi data into benefit opportunities',
    referral_join_why_title: 'Why sign up?',
    referral_join_why_desc:
      'ZENOV analyzes driver operation data so drivers can review fuel cost saving potential, EV transition savings, charging and maintenance benefit candidates, and government program information.',
    referral_join_benefits_title: 'Benefits available after signup',
    referral_join_benefits: [
      ['Fuel Cost Saving Analysis', 'Review how much can be saved based on the current vehicle.'],
      ['EV Transition Diagnosis', 'Review estimated savings and priority when switching to an EV.'],
      ['Charging & Maintenance Benefits', 'Review partner charging station and repair shop discount candidates.'],
      ['Government Program Information', 'Receive information on EV subsidies and charging infrastructure support programs.'],
      ['Carbon Reduction Project Candidate Participation', 'When enough operation data is secured, MRV feasibility review and candidate diagnosis can be conducted.'],
    ],
    referral_join_disclaimer: 'Carbon credit issuance or revenue is not guaranteed.',
    referral_join_invite_title: 'Driver Referral Benefits',
    referral_join_invite_desc:
      'Each driver receives a general member referral code. Inviting peers can be used for point accumulation and charging or maintenance benefit candidates.',
    referral_join_steps_title: 'Signup Flow',
    referral_join_steps: ['Sign up', 'Enter referral code optionally', 'Register vehicle', 'Connect operation data', 'Review savings report'],
    referral_join_goal_title: 'ZENOV Goal',
    referral_join_goal_desc:
      'ZENOV is not a complex ESG platform. It shows drivers and companies how much they may save and what business opportunities can be reviewed through data.',
    form_status_label: 'Status',
    status_draft: 'Draft',
    status_submitted: 'Submitted',
    status_under_review: 'Under Review',
    status_nda_required: 'NDA Required',
    status_pilot_candidate: 'Pilot Candidate',
    status_rejected: 'Rejected / Hold',
    form_save: 'Save',
    form_internal_pdf: 'Print Internal Review PDF',
    form_customer_pdf: 'Print Customer Submission PDF',
    form_excel: 'Download Excel',
    form_select: 'Select',
    form_submitted_preview: 'Submitted Form Preview',
    form_not_evidence: 'Printed PDFs are not Evidence and do not trigger status transitions before operational log verification.',
    form_latest_saved: 'Latest Saved',
    form_no_saved: 'No submissions saved.',
    form_save_success: 'Saved. This submission is not an Evidence File.',
    form_taxi_save_success: 'Saved and linked to Taxi Carbon OS diagnosis input data. This submission is not an Evidence File.',
    form_print_suffix: 'mode. Choose Save as PDF in the browser print dialog.',
    records_suffix: 'records',
    preview_table: 'Table',
    preview_status: 'Status',
    preview_document_type: 'Document Type',
    preview_evidence_file: 'Evidence File',
    data_checklist_title: 'File Download Checklist',
    data_checklist_desc:
      'Download and use the files below for pilot candidates or internal review. These files are not Evidence and do not trigger status transitions before real operational proof is submitted.',
    taxi_diagnosis_file_link: 'Taxi Carbon OS Diagnosis File',
    taxi_dashboard_link: 'Taxi Carbon OS Dashboard',
    delivery_org_label: 'Recipient Company / Union',
    delivery_recipient_label: 'Recipient Name',
    delivery_email_label: 'Recipient Email',
    delivery_files_label: 'Delivery Files',
    delivery_download: 'Download',
    delivery_create_manifest: 'Create Delivery Manifest',
    delivery_created_message: 'Delivery manifest created. Send the downloaded files and manifest through a separate email or messenger.',
    delivery_preview_title: 'Delivery Preview',
    delivery_preview_desc: 'External email sending is not connected. Deliver the downloaded files and manifest separately.',
    delivery_latest_manifest: 'Latest Manifest',
    delivery_empty_manifest: 'No delivery manifest has been created.',
    delivery_preview_recipient: 'Recipient',
    delivery_preview_email: 'Email',
    delivery_preview_organization: 'Organization',
    delivery_preview_selected_files: 'Selected Files',
    partner_type_taxi_union: 'Taxi Union',
    partner_type_taxi_company: 'Taxi Company',
    partner_type_factory: 'Taxi Company Facility',
    partner_type_charging_operator: 'Charging Operator',
    partner_type_consultant: 'Consultant',
    partner_type_regional_partner: 'Regional Partner',
    login_eyebrow: 'ZENOV Partner Access',
    login_title: 'Partner Login',
    login_desc: 'Enter the partner code to open the Pilot Dashboard.',
    login_code_label: 'Partner Code',
    login_button: 'Login',
    login_error: 'The partner code does not match.',
    login_required_title: 'Partner login required',
    login_required_desc: 'Pilot applications and questionnaire data can only be entered in a partner session.',
    code_placeholder: 'Enter partner code',
  },
  zh: {
    language: '语言选择',
    brand: 'ZENOV Pilot Portal',
    nav_dashboard: '仪表板',
    nav_pilot: '试点',
    nav_taxi: '出租车',
    nav_factory: '设施实查',
    nav_charging: '充电',
    nav_cd_key: 'CD Key',
    nav_files: '文件',
    eyebrow: '试点获客',
    title: 'ZENOV 试点获客门户',
    desc: '输入、保存并输出出租车、出租车公司设施、充电合作伙伴的试点申请和综合尽调问卷，可用于内部 PDF 审阅和 Excel 下载。',
    frozen_note: '不是证据文件',
    saved_forms: '已保存提交',
    production_ready: 'Production Ready',
    commercial_ready: 'Commercial Ready',
    current_flow: 'Current Flow',
    saved_suffix: '已保存',
    delivery_eyebrow: '试点交付资料包',
    delivery_title: '交付文件',
    delivery_desc: '可在门户内直接阅读并套用试点提案、尽调问卷、清单、申请书和行业表单。这些是试点获客模板，不是证据文件。',
    pdf_print: 'PDF 输出',
    open_apply: '阅读 / 套用',
    output_title: 'PDF 输出 / Excel 下载',
    output_desc: '各输入画面保存后可执行 PDF 打印和 CSV 下载。输出物是试点获客模板 / 已提交表单，不是证据文件。',
    menu_pilot_application: '试点申请管理',
    menu_taxi_survey: '出租车试点问卷',
    menu_factory_assessment: '出租车公司设施实查',
    menu_charging_partner: '充电合作伙伴表单',
    menu_due_diligence: '综合尽调问卷',
    menu_data_checklist: '数据请求清单',
    menu_referral_code: '发放推荐码 / 伙伴代码',
    menu_file_delivery: '文件交付中心',
    menu_taxi_carbon_proof: 'Taxi Carbon Proof',
    menu_taxi_carbon_dashboard: 'Taxi Carbon OS 仪表板',
    menu_taxi_diagnosis_file: 'Taxi Carbon OS 诊断文件',
    menu_partner_approvals: '合作伙伴审批管理',
    menu_partner_dashboard: '合作伙伴仪表板',
    menu_driver_dashboard: '司机仪表板',
    dashboard_referral_title: '仪表板伙伴代码生成',
    dashboard_referral_desc: '生成用于伙伴归因和 Hub 级 Pilot 申请追踪的伙伴代码。该代码不是证据文件，也不会触发状态变更。',
    dashboard_referral_button: '生成伙伴代码',
    dashboard_referral_created: '伙伴代码已生成',
    dashboard_referral_approval_note:
      '生成的代码将以管理员审批待处理状态保存。审批前不会启用下级司机、车辆数据归属及结算可行性审查。',
    referral_flow_title: '合作伙伴代码运营流程',
    referral_flow_steps: [
      '代表或协会负责人注册',
      '申请合作伙伴推荐码',
      '管理员审批',
      '连接下级司机与车辆数据',
      'EV 转换、充电站、碳减排候选诊断',
      '结算可行性审查',
    ],
    referral_status_pending_approval: '等待管理员审批',
    referral_status_approved: '管理员已审批',
    referral_status_disabled: '已停用',
    referral_title: '发放推荐码 / 伙伴代码',
    referral_desc: '在管理员专用画面中，个人推荐码与组织伙伴代码分开签发和查看。该代码仅用于 Pilot 来源追踪，不是 CD Key。',
    referral_button: '发放代码',
    referral_created: '代码已发放',
    referral_hub_label: 'Hub / 区域合作伙伴名称',
    referral_partner_label: '推荐合作伙伴名称',
    referral_email_label: '合作伙伴邮箱',
    referral_type_label: '合作伙伴类型',
    referral_region_label: '区域',
    referral_region_placeholder: '例如：京畿南部',
    referral_code_scope_label: '代码类型',
    referral_scope_partner: '组织合作伙伴代码',
    referral_scope_driver: '普通会员推荐码',
    referral_driver_id_label: '推荐司机 ID',
    referral_partner_policy_note: '组织合作伙伴代码需管理员审批后，才会启用下级司机与车辆归属审查。',
    referral_driver_policy_note: '普通会员推荐码用于好友注册追踪，并立即启用以计算积分/权益候选。',
    referral_scope_preview: '代码类型',
    referral_download_latest: '下载最新代码文件',
    referral_preview_title: '已发放代码',
    referral_preview_desc: '保存在浏览器本地存储中；配置 Supabase 后也会保存到 DB，并与 CD Key 分开管理。',
    referral_empty: '尚未发放代码。',
    referral_join_eyebrow: 'ZENOV 注册与权益说明',
    referral_join_title: '将出租车数据转化为权益机会的平台',
    referral_join_why_title: '为什么要注册？',
    referral_join_why_desc:
      'ZENOV 会分析司机的运营数据，帮助查看燃料成本节省可能性、切换电动车时的预计节省、充电与维修权益候选以及政府支持项目信息。',
    referral_join_benefits_title: '注册后可查看的权益',
    referral_join_benefits: [
      ['燃料成本节省分析', '基于当前车辆查看可节省金额候选。'],
      ['EV 转换诊断', '查看切换电动车时的预计节省与优先级。'],
      ['充电与维修权益', '查看合作充电站和维修点折扣权益候选。'],
      ['政府支持项目信息', '提供 EV 补贴和充电基础设施支持项目等相关信息。'],
      ['碳减排项目候选参与机会', '当运营数据足够充分时，可进行 MRV 可行性审查和候选诊断。'],
    ],
    referral_join_disclaimer: '不保证碳信用签发或收益。',
    referral_join_invite_title: '司机推荐权益',
    referral_join_invite_desc:
      '每位司机都会获得个人推荐码。邀请同业注册后，可用于积分累计、充电折扣或维修折扣等权益候选。',
    referral_join_steps_title: '注册流程',
    referral_join_steps: ['注册会员', '选择性输入推荐码', '登记车辆', '连接运营数据', '查看节省报告'],
    referral_join_goal_title: 'ZENOV 的目标',
    referral_join_goal_desc:
      'ZENOV 不是复杂的 ESG 平台，而是用数据展示司机和公司可能节省多少、可审查哪些业务机会的平台。',
    form_status_label: '状态',
    status_draft: '草稿',
    status_submitted: '已提交',
    status_under_review: '审核中',
    status_nda_required: '需要 NDA',
    status_pilot_candidate: '试点候选',
    status_rejected: '保留 / 驳回',
    form_save: '保存',
    form_internal_pdf: '输出内部审查 PDF',
    form_customer_pdf: '输出客户提交 PDF',
    form_excel: '下载 Excel',
    form_select: '选择',
    form_submitted_preview: '提交表单预览',
    form_not_evidence: '输出 PDF 不是证据文件，在运营日志验证前不会触发状态变更。',
    form_latest_saved: '最近保存',
    form_no_saved: '尚无保存的提交。',
    form_save_success: '已保存。该提交数据不是证据文件。',
    form_taxi_save_success: '已保存，并已连接到 Taxi Carbon OS 诊断输入数据。该提交数据不是证据文件。',
    form_print_suffix: '输出模式。请在浏览器打印窗口中选择保存为 PDF。',
    records_suffix: '条记录',
    preview_table: '数据表',
    preview_status: '状态',
    preview_document_type: '文档类型',
    preview_evidence_file: '证据文件',
    data_checklist_title: '文件下载清单',
    data_checklist_desc: '下载并使用下列文件，用于 Pilot 候选方或内部审查。这些文件不是证据文件，在实际运营证据提交前不会触发状态变更。',
    taxi_diagnosis_file_link: 'Taxi Carbon OS 诊断文件',
    taxi_dashboard_link: 'Taxi Carbon OS 仪表板',
    delivery_org_label: '接收公司 / 协会名称',
    delivery_recipient_label: '接收人姓名',
    delivery_email_label: '接收人邮箱',
    delivery_files_label: '交付文件',
    delivery_download: '下载',
    delivery_create_manifest: '生成交付清单',
    delivery_created_message: '交付清单已生成。实际外部发送请通过单独的邮件或消息工具执行。',
    delivery_preview_title: '交付预览',
    delivery_preview_desc: '未连接外部邮件发送功能。请另行发送下载的文件和清单。',
    delivery_latest_manifest: '最新清单',
    delivery_empty_manifest: '尚未生成交付清单。',
    delivery_preview_recipient: '接收人',
    delivery_preview_email: '邮箱',
    delivery_preview_organization: '公司 / 协会',
    delivery_preview_selected_files: '已选文件',
    partner_type_taxi_union: '出租车协会',
    partner_type_taxi_company: '出租车公司',
    partner_type_factory: '出租车公司设施',
    partner_type_charging_operator: '充电运营商',
    partner_type_consultant: '顾问',
    partner_type_regional_partner: '区域合作伙伴',
    login_eyebrow: 'ZENOV 合作伙伴访问',
    login_title: '合作伙伴登录',
    login_desc: '输入合作伙伴代码后即可进入 Pilot Dashboard。',
    login_code_label: '合作伙伴代码',
    login_button: '登录',
    login_error: '合作伙伴代码不一致。',
    login_required_title: '需要合作伙伴登录',
    login_required_desc: 'Pilot 申请和问卷数据只能在合作伙伴会话中输入。',
    code_placeholder: '请输入合作伙伴代码',
  },
  th: {
    language: 'เลือกภาษา',
    brand: 'ZENOV Pilot Portal',
    nav_dashboard: 'แดชบอร์ด',
    nav_pilot: 'Pilot',
    nav_taxi: 'แท็กซี่',
    nav_factory: 'ตรวจสถานที่',
    nav_charging: 'ชาร์จ EV',
    nav_cd_key: 'CD Key',
    nav_files: 'ไฟล์',
    eyebrow: 'Pilot Acquisition',
    title: 'พอร์ทัลจัดหา Pilot ของ ZENOV',
    desc: 'กรอก บันทึก พิมพ์ PDF และดาวน์โหลด Excel สำหรับใบสมัคร Pilot และแบบสอบถาม Due Diligence ของ Taxi, สถานที่บริษัทแท็กซี่ และ Charging Partner',
    frozen_note: 'ไม่ใช่ Evidence File',
    saved_forms: 'แบบฟอร์มที่บันทึกแล้ว',
    production_ready: 'Production Ready',
    commercial_ready: 'Commercial Ready',
    current_flow: 'Current Flow',
    saved_suffix: 'บันทึกแล้ว',
    delivery_eyebrow: 'PILOT DELIVERY PACKAGE',
    delivery_title: 'ไฟล์สำหรับส่งมอบ',
    delivery_desc:
      'อ่านและนำข้อเสนอ Pilot แบบสอบถาม Due Diligence เช็กลิสต์ ใบสมัคร และแบบฟอร์มตามกลุ่มธุรกิจไปใช้ได้ในพอร์ทัล ไฟล์เหล่านี้เป็น Template ไม่ใช่ Evidence File',
    pdf_print: 'พิมพ์ PDF',
    open_apply: 'อ่าน / นำไปใช้',
    output_title: 'พิมพ์ PDF / ดาวน์โหลด Excel',
    output_desc: 'หลังบันทึกแต่ละฟอร์ม สามารถพิมพ์ PDF และดาวน์โหลด CSV ได้ เอกสารเหล่านี้ไม่ใช่ Evidence File',
    menu_pilot_application: 'จัดการใบสมัคร Pilot',
    menu_taxi_survey: 'แบบสำรวจ Taxi Pilot',
    menu_factory_assessment: 'ตรวจสถานที่บริษัทแท็กซี่',
    menu_charging_partner: 'แบบฟอร์ม Charging Partner',
    menu_due_diligence: 'แบบสอบถาม Due Diligence',
    menu_data_checklist: 'เช็กลิสต์ข้อมูล',
    menu_referral_code: 'ออก Referral Code / Partner Code',
    menu_file_delivery: 'ศูนย์ส่งมอบไฟล์',
    menu_taxi_carbon_proof: 'Taxi Carbon Proof',
    menu_taxi_carbon_dashboard: 'แดชบอร์ด Taxi Carbon OS',
    menu_taxi_diagnosis_file: 'ไฟล์วินิจฉัย Taxi Carbon OS',
    menu_partner_approvals: 'จัดการอนุมัติ Partner',
    menu_partner_dashboard: 'แดชบอร์ด Partner',
    menu_driver_dashboard: 'แดชบอร์ดคนขับ',
    dashboard_referral_title: 'สร้าง Partner Code จากแดชบอร์ด',
    dashboard_referral_desc:
      'สร้าง Partner Code สำหรับติดตามที่มาของพาร์ทเนอร์และใบสมัคร Pilot ตาม Hub โค้ดนี้ไม่ใช่ Evidence และไม่ทำให้สถานะเปลี่ยน',
    dashboard_referral_button: 'สร้าง Partner Code',
    dashboard_referral_created: 'สร้าง Partner Code แล้ว',
    dashboard_referral_approval_note:
      'Code ที่สร้างจะถูกบันทึกเป็นสถานะรอการอนุมัติจากผู้ดูแล ก่อนอนุมัติจะยังไม่เปิดใช้การผูกข้อมูลคนขับ/รถและการตรวจสอบความเป็นไปได้ด้านการจัดสรร',
    referral_flow_title: 'ขั้นตอนการใช้งาน Partner Code',
    referral_flow_steps: [
      'ตัวแทนหรือผู้นำสหกรณ์สมัคร',
      'ขอ Partner Code',
      'ผู้ดูแลอนุมัติ',
      'เชื่อมโยงข้อมูลคนขับและรถในสังกัด',
      'วิเคราะห์ EV สถานีชาร์จ และโครงการลดคาร์บอนที่เป็นไปได้',
      'ตรวจสอบความเป็นไปได้ด้านการจัดสรร',
    ],
    referral_status_pending_approval: 'รอการอนุมัติจากผู้ดูแล',
    referral_status_approved: 'ผู้ดูแลอนุมัติแล้ว',
    referral_status_disabled: 'ปิดใช้งาน',
    referral_title: 'ออก Referral Code / Partner Code',
    referral_desc: 'หน้าผู้ดูแลระบบนี้ใช้แยกออกและตรวจดู Referral Code ส่วนบุคคลกับ Partner Code ขององค์กร โค้ดนี้ใช้ติดตามที่มาของ Pilot เท่านั้น ไม่ใช่ CD Key',
    referral_button: 'ออกโค้ด',
    referral_created: 'ออกโค้ดแล้ว',
    referral_hub_label: 'ชื่อ Hub / พาร์ทเนอร์ภูมิภาค',
    referral_partner_label: 'ชื่อพาร์ทเนอร์ผู้แนะนำ',
    referral_email_label: 'อีเมลพาร์ทเนอร์',
    referral_type_label: 'ประเภทพาร์ทเนอร์',
    referral_region_label: 'ภูมิภาค',
    referral_region_placeholder: 'ตัวอย่าง: Southern Gyeonggi',
    referral_code_scope_label: 'ประเภทโค้ด',
    referral_scope_partner: 'โค้ดพาร์ทเนอร์องค์กร',
    referral_scope_driver: 'Referral Code สมาชิกทั่วไป',
    referral_driver_id_label: 'Driver ID ของผู้แนะนำ',
    referral_partner_policy_note:
      'โค้ดพาร์ทเนอร์องค์กรต้องรอผู้ดูแลอนุมัติก่อนจึงจะเปิดใช้การผูกข้อมูลคนขับและรถ',
    referral_driver_policy_note:
      'Referral Code สมาชิกทั่วไปเปิดใช้ทันทีสำหรับติดตามการแนะนำและคำนวณสิทธิประโยชน์/คะแนนเบื้องต้น',
    referral_scope_preview: 'ประเภทโค้ด',
    referral_download_latest: 'ดาวน์โหลดไฟล์โค้ดล่าสุด',
    referral_preview_title: 'โค้ดที่ออกแล้ว',
    referral_preview_desc: 'จัดเก็บใน local storage ของเบราว์เซอร์ และหากตั้งค่า Supabase แล้วจะบันทึกลง DB ด้วย โดยแยกจาก CD Key',
    referral_empty: 'ยังไม่มีโค้ดที่ออกแล้ว',
    referral_join_eyebrow: 'คู่มือสมัครและสิทธิประโยชน์ ZENOV',
    referral_join_title: 'แพลตฟอร์มที่เปลี่ยนข้อมูลแท็กซี่เป็นโอกาสด้านสิทธิประโยชน์',
    referral_join_why_title: 'ทำไมควรสมัคร?',
    referral_join_why_desc:
      'ZENOV วิเคราะห์ข้อมูลการขับขี่ของคนขับ เพื่อช่วยตรวจสอบโอกาสประหยัดค่าเชื้อเพลิง เงินประหยัดโดยประมาณเมื่อเปลี่ยนเป็น EV สิทธิประโยชน์ด้านการชาร์จและซ่อมบำรุง และข้อมูลโครงการสนับสนุนจากภาครัฐ',
    referral_join_benefits_title: 'สิทธิประโยชน์หลังสมัคร',
    referral_join_benefits: [
      ['วิเคราะห์การประหยัดค่าเชื้อเพลิง', 'ตรวจสอบว่ารถปัจจุบันมีโอกาสประหยัดได้เท่าใด'],
      ['วินิจฉัยการเปลี่ยนเป็น EV', 'ตรวจสอบเงินประหยัดโดยประมาณและลำดับความสำคัญเมื่อเปลี่ยนเป็นรถ EV'],
      ['สิทธิประโยชน์การชาร์จและซ่อมบำรุง', 'ตรวจสอบสิทธิ์ส่วนลดจากสถานีชาร์จและอู่ซ่อมพันธมิตร'],
      ['ข้อมูลโครงการสนับสนุนภาครัฐ', 'รับข้อมูลเกี่ยวกับเงินสนับสนุน EV และโครงการโครงสร้างพื้นฐานการชาร์จ'],
      ['โอกาสเข้าร่วมโครงการลดคาร์บอนเบื้องต้น', 'เมื่อมีข้อมูลการขับขี่เพียงพอ จะสามารถตรวจสอบความเป็นไปได้ของ MRV และวินิจฉัยโครงการ candidate ได้'],
    ],
    referral_join_disclaimer: 'ไม่รับประกันการออกคาร์บอนเครดิตหรือรายได้',
    referral_join_invite_title: 'สิทธิประโยชน์จากการแนะนำคนขับ',
    referral_join_invite_desc:
      'สมาชิกทั่วไปจะได้รับโค้ดพาร์ทเนอร์ส่วนตัว เมื่อนำไปเชิญเพื่อนร่วมอาชีพ สามารถใช้เป็น candidate สำหรับคะแนนสะสม ส่วนลดการชาร์จ หรือส่วนลดซ่อมบำรุงได้',
    referral_join_steps_title: 'ขั้นตอนสมัคร',
    referral_join_steps: ['สมัครสมาชิก', 'กรอก Referral Code หากมี', 'ลงทะเบียนรถ', 'เชื่อมข้อมูลการขับขี่', 'ดูรายงานการประหยัด'],
    referral_join_goal_title: 'เป้าหมายของ ZENOV',
    referral_join_goal_desc:
      'ZENOV ไม่ใช่แพลตฟอร์ม ESG ที่ซับซ้อน แต่เป็นแพลตฟอร์มข้อมูลที่แสดงให้คนขับและบริษัทเห็นว่าอาจประหยัดได้เท่าใด และมีโอกาสทางธุรกิจใดที่ควรตรวจสอบ',
    form_status_label: 'สถานะ',
    status_draft: 'แบบร่าง',
    status_submitted: 'ส่งแล้ว',
    status_under_review: 'อยู่ระหว่างตรวจสอบ',
    status_nda_required: 'ต้องมี NDA',
    status_pilot_candidate: 'ผู้สมัคร Pilot',
    status_rejected: 'พักไว้ / ปฏิเสธ',
    form_save: 'บันทึก',
    form_internal_pdf: 'พิมพ์ PDF สำหรับตรวจภายใน',
    form_customer_pdf: 'พิมพ์ PDF สำหรับส่งลูกค้า',
    form_excel: 'ดาวน์โหลด Excel',
    form_select: 'เลือก',
    form_submitted_preview: 'ตัวอย่างแบบฟอร์มที่ส่ง',
    form_not_evidence: 'PDF ที่พิมพ์ไม่ใช่ Evidence และไม่ทำให้สถานะเปลี่ยนก่อนตรวจสอบ operational log',
    form_latest_saved: 'บันทึกล่าสุด',
    form_no_saved: 'ยังไม่มีรายการที่บันทึก',
    form_save_success: 'บันทึกแล้ว ข้อมูลนี้ไม่ใช่ Evidence File',
    form_taxi_save_success: 'บันทึกแล้วและเชื่อมไปยังข้อมูลวินิจฉัย Taxi Carbon OS ข้อมูลนี้ไม่ใช่ Evidence File',
    form_print_suffix: 'เลือก Save as PDF ในหน้าต่างพิมพ์ของเบราว์เซอร์',
    records_suffix: 'รายการ',
    preview_table: 'ตาราง',
    preview_status: 'สถานะ',
    preview_document_type: 'ประเภทเอกสาร',
    preview_evidence_file: 'Evidence File',
    data_checklist_title: 'เช็กลิสต์ดาวน์โหลดไฟล์',
    data_checklist_desc:
      'ดาวน์โหลดและใช้ไฟล์ด้านล่างสำหรับผู้สมัคร Pilot หรือการตรวจภายใน ไฟล์เหล่านี้ไม่ใช่ Evidence และไม่ทำให้สถานะเปลี่ยนก่อนส่งหลักฐานปฏิบัติการจริง',
    taxi_diagnosis_file_link: 'ไฟล์วินิจฉัย Taxi Carbon OS',
    taxi_dashboard_link: 'แดชบอร์ด Taxi Carbon OS',
    delivery_org_label: 'บริษัท / สหกรณ์ผู้รับ',
    delivery_recipient_label: 'ชื่อผู้รับ',
    delivery_email_label: 'อีเมลผู้รับ',
    delivery_files_label: 'ไฟล์ที่จะส่ง',
    delivery_download: 'ดาวน์โหลด',
    delivery_create_manifest: 'สร้าง Delivery Manifest',
    delivery_created_message: 'สร้าง Delivery Manifest แล้ว กรุณาส่งไฟล์ที่ดาวน์โหลดและ manifest ผ่านอีเมลหรือเมสเซนเจอร์แยกต่างหาก',
    delivery_preview_title: 'ตัวอย่างการส่งมอบ',
    delivery_preview_desc: 'ยังไม่ได้เชื่อมระบบส่งอีเมลภายนอก กรุณาส่งไฟล์ที่ดาวน์โหลดและ manifest แยกต่างหาก',
    delivery_latest_manifest: 'Manifest ล่าสุด',
    delivery_empty_manifest: 'ยังไม่มี Delivery Manifest',
    delivery_preview_recipient: 'ผู้รับ',
    delivery_preview_email: 'อีเมล',
    delivery_preview_organization: 'องค์กร',
    delivery_preview_selected_files: 'ไฟล์ที่เลือก',
    partner_type_taxi_union: 'สหกรณ์แท็กซี่',
    partner_type_taxi_company: 'บริษัทแท็กซี่',
    partner_type_factory: 'สถานที่บริษัทแท็กซี่',
    partner_type_charging_operator: 'ผู้ให้บริการชาร์จ',
    partner_type_consultant: 'ที่ปรึกษา',
    partner_type_regional_partner: 'พาร์ทเนอร์ภูมิภาค',
    login_eyebrow: 'ZENOV Partner Access',
    login_title: 'เข้าสู่ระบบพาร์ทเนอร์',
    login_desc: 'กรอกรหัสพาร์ทเนอร์เพื่อเข้าสู่ Pilot Dashboard',
    login_code_label: 'รหัสพาร์ทเนอร์',
    login_button: 'เข้าสู่ระบบ',
    login_error: 'รหัสพาร์ทเนอร์ไม่ถูกต้อง',
    login_required_title: 'ต้องเข้าสู่ระบบพาร์ทเนอร์',
    login_required_desc: 'สามารถกรอกใบสมัคร Pilot และข้อมูลแบบสอบถามได้เฉพาะในเซสชันพาร์ทเนอร์เท่านั้น',
    code_placeholder: 'กรอกรหัสพาร์ทเนอร์',
  },
};

const allowedStatuses = [
  'draft',
  'submitted',
  'under_review',
  'nda_required',
  'pilot_candidate',
  'rejected',
] as const;

type FormStatus = (typeof allowedStatuses)[number];

const statusLabelKeys: Record<FormStatus, keyof (typeof adminI18n)['ko']> = {
  draft: 'status_draft',
  submitted: 'status_submitted',
  under_review: 'status_under_review',
  nda_required: 'status_nda_required',
  pilot_candidate: 'status_pilot_candidate',
  rejected: 'status_rejected',
};

function getStatusLabel(status: string, t: (typeof adminI18n)[AdminLang]) {
  if (allowedStatuses.includes(status as FormStatus)) {
    return t[statusLabelKeys[status as FormStatus]];
  }
  return status;
}

const menu = [
  ['menu_pilot_application', '/pilot-application'],
  ['menu_taxi_survey', '/taxi-survey'],
  ['menu_factory_assessment', '/factory-assessment'],
  ['menu_charging_partner', '/charging-partner'],
  ['menu_referral_code', '/referral-code'],
  ['menu_file_delivery', '/file-delivery'],
  ['nav_dashboard', '/dashboard'],
];

const salesKitFiles = [
  {
    slug: 'pilot-proposal',
    labelKey: 'pilot_proposal',
    label: '시범 사업 제안',
    filename: 'ZENOV-PILOT-PROPOSAL.pdf',
    href: '/pilot-assets/sales-kit/ZENOV-PILOT-PROPOSAL.pdf',
  },
  {
    slug: 'due-diligence-questionnaire',
    labelKey: 'due_diligence_questionnaire',
    label: '통합 실사 설문지',
    filename: 'ZENOV-UNIFIED-DUE-DILIGENCE-QUESTIONNAIRE.pdf',
    href: '/pilot-assets/sales-kit/ZENOV-UNIFIED-DUE-DILIGENCE-QUESTIONNAIRE.pdf',
  },
  {
    slug: 'data-request-checklist',
    labelKey: 'data_request_checklist',
    label: '데이터 요청 체크리스트',
    filename: 'ZENOV-DATA-REQUEST-CHECKLIST.pdf',
    href: '/pilot-assets/sales-kit/ZENOV-DATA-REQUEST-CHECKLIST.pdf',
  },
  {
    slug: 'pilot-application',
    labelKey: 'pilot_application',
    label: '시범 적용',
    filename: 'ZENOV-PILOT-APPLICATION.xlsx',
    href: '/pilot-assets/sales-kit/ZENOV-PILOT-APPLICATION.xlsx',
  },
  {
    slug: 'taxi-pilot-survey',
    labelKey: 'taxi_pilot_survey',
    label: '택시 조종사 설문조사',
    filename: 'ZENOV-TAXI-PILOT-SURVEY.xlsx',
    href: '/pilot-assets/sales-kit/ZENOV-TAXI-PILOT-SURVEY.xlsx',
  },
  {
    slug: 'factory-assessment',
    labelKey: 'factory_assessment',
    label: '택시회사 시설 실사',
    filename: 'ZENOV-FACTORY-ASSESSMENT.xlsx',
    href: '/pilot-assets/sales-kit/ZENOV-FACTORY-ASSESSMENT.xlsx',
  },
  {
    slug: 'charging-partner-form',
    labelKey: 'charging_partner_form',
    label: '과금 파트너 양식',
    filename: 'ZENOV-CHARGING-PARTNER-FORM.xlsx',
    href: '/pilot-assets/sales-kit/ZENOV-CHARGING-PARTNER-FORM.xlsx',
  },
  {
    slug: 'executive-one-pager',
    labelKey: 'executive_one_pager',
    label: '임원용 요약 자료 (원페이지)',
    filename: 'ZENOV-EXECUTIVE-ONE-PAGER.pdf',
    href: '/pilot-assets/sales-kit/ZENOV-EXECUTIVE-ONE-PAGER.pdf',
  },
  {
    slug: 'nda',
    labelKey: 'nda',
    label: '비밀유지협약',
    filename: 'ZENOV-NDA.pdf',
    href: '/pilot-assets/sales-kit/ZENOV-NDA.pdf',
  },
];

const salesKitFileLabels: Record<AdminLang, Record<(typeof salesKitFiles)[number]['labelKey'], string>> = {
  ko: {
    pilot_proposal: '시범 사업 제안',
    due_diligence_questionnaire: '통합 실사 설문지',
    data_request_checklist: '데이터 요청 체크리스트',
    pilot_application: '시범 적용',
    taxi_pilot_survey: '택시 파일럿 설문조사',
    factory_assessment: '택시회사 시설 실사',
    charging_partner_form: '충전 파트너 양식',
    executive_one_pager: '임원용 요약 자료 (원페이지)',
    nda: '비밀유지협약',
  },
  en: {
    pilot_proposal: 'Pilot Proposal',
    due_diligence_questionnaire: 'Unified Due Diligence Questionnaire',
    data_request_checklist: 'Data Request Checklist',
    pilot_application: 'Pilot Application',
    taxi_pilot_survey: 'Taxi Pilot Survey',
    factory_assessment: 'Taxi Company Facility Audit',
    charging_partner_form: 'Charging Partner Form',
    executive_one_pager: 'Executive One Pager',
    nda: 'NDA',
  },
  zh: {
    pilot_proposal: '试点项目提案',
    due_diligence_questionnaire: '综合尽调问卷',
    data_request_checklist: '数据请求清单',
    pilot_application: '试点申请',
    taxi_pilot_survey: '出租车试点问卷',
    factory_assessment: '出租车公司设施实查',
    charging_partner_form: '充电合作伙伴表单',
    executive_one_pager: '高管一页摘要',
    nda: '保密协议',
  },
  th: {
    pilot_proposal: 'ข้อเสนอ Pilot',
    due_diligence_questionnaire: 'แบบสอบถาม Due Diligence รวม',
    data_request_checklist: 'เช็กลิสต์ขอข้อมูล',
    pilot_application: 'ใบสมัคร Pilot',
    taxi_pilot_survey: 'แบบสำรวจ Taxi Pilot',
    factory_assessment: 'ตรวจสถานที่บริษัทแท็กซี่',
    charging_partner_form: 'แบบฟอร์ม Charging Partner',
    executive_one_pager: 'Executive One Pager',
    nda: 'NDA',
  },
};

const checklistFileOptions = salesKitFiles.slice(0, 7).map((file) => `${file.label} - ${file.filename}`);

const forms: Record<string, FormConfig> = {
  pilotApplication: {
    title: 'Pilot 신청 입력',
    subtitle: 'Pilot 후보 기본 정보와 NDA·데이터 제공 가능성을 수집합니다.',
    route: '/pilot-application',
    storageKey: 'zenov_pilot_applications',
    tableName: 'zenov_pilot_applications',
    fields: [
      { name: 'company_name', label: '회사명' },
      { name: 'contact_name', label: '담당자' },
      { name: 'phone', label: '연락처' },
      { name: 'email', label: '이메일', type: 'email' },
      { name: 'industry', label: '업종' },
      { name: 'region', label: '지역' },
      {
        name: 'pilot_interest',
        label: 'Pilot 관심 분야',
        type: 'multiselect',
        options: ['ESG', 'Carbon MRV', 'Taxi Carbon', 'Factory Intelligence', 'Charging', '정부지원사업'],
      },
      {
        name: 'nda_status',
        label: 'NDA 체결 여부',
        type: 'select',
        options: ['가능', '법무 검토 필요', '불가'],
      },
      {
        name: 'data_sharing_status',
        label: '데이터 제공 가능 여부',
        type: 'select',
        options: ['가능', '익명화 후 가능', '검토 필요', '불가'],
      },
    ],
  },
  taxiSurvey: {
    title: 'Taxi Pilot Survey',
    subtitle: '택시조합·법인택시의 차량, 기사, 차고지, 충전 후보 데이터를 수집합니다.',
    route: '/taxi-survey',
    storageKey: 'zenov_taxi_pilot_surveys',
    tableName: 'zenov_taxi_pilot_surveys',
    fields: [
      { name: 'union_name', label: '조합명' },
      { name: 'taxi_company_name', label: '택시 회사 이름' },
      { name: 'total_vehicles', label: '총 차량 수', type: 'number' },
      { name: 'union_vehicle_count', label: '조합 차량 수', type: 'number' },
      { name: 'taxi_company_vehicle_count', label: '택시 회사 차량 수', type: 'number' },
      { name: 'lpg_vehicles', label: 'LPG 차량 수', type: 'number' },
      { name: 'ev_vehicles', label: 'EV 차량 수', type: 'number' },
      { name: 'ev_convertible_vehicles', label: 'EV 전환 가능 차량 수', type: 'number' },
      { name: 'driver_count', label: '기사 수', type: 'number' },
      { name: 'garage_available', label: '차고지 여부', type: 'select', options: ['있음', '없음', '확인 필요'] },
      {
        name: 'charging_candidate_site',
        label: '충전소 후보지 여부',
        type: 'select',
        options: ['있음', '없음', '확인 필요'],
      },
      { name: 'monthly_distance', label: '월 평균 주행거리', type: 'number' },
      { name: 'monthly_fuel_cost', label: '월 평균 연료비', type: 'number' },
    ],
  },
  factoryAssessment: {
    title: '택시회사 시설 부지 실사',
    subtitle: '택시회사 내 정비소, 세차장, 사무실, 주차장/부지를 관리하고 충전소·태양광 설치 타당성 후보를 분석하기 위한 데이터를 수집합니다.',
    route: '/factory-assessment',
    storageKey: 'zenov_factory_assessments',
    tableName: 'zenov_factory_assessments',
    fields: [
      { name: 'facility_name', label: '시설 명칭' },
      {
        name: 'facility_type',
        label: '시설 유형',
        type: 'select',
        options: ['정비소', '세차장', '사무실', '주차장/부지'],
      },
      { name: 'managed_area_sqm', label: '관리 면적', type: 'number' },
      {
        name: 'building_structure',
        label: '건물 구조',
        type: 'select',
        options: ['통건물', '조립식', '컨테이너', '노지'],
      },
      { name: 'erp_mes_usage', label: 'ERP/MES 도입 여부', type: 'select', options: ['사용', '미사용', '도입 검토'] },
      { name: 'grid_connection_capacity_kw', label: '전기 인입 용량', type: 'number' },
      {
        name: 'roof_ceiling_material',
        label: '지붕/천장 재질',
        type: 'select',
        options: ['시멘트', '철골', '샌드위치 패널', '아스팔트 싱글', '확인 필요'],
      },
      { name: 'monthly_power_usage', label: '월 전력 사용량', type: 'number' },
      { name: 'monthly_power_cost', label: '월 전기요금', type: 'number' },
      {
        name: 'carbon_data_available',
        label: '탄소 데이터 보유 여부',
        type: 'select',
        options: ['보유(운행/충전 기록)', '일부 보유', '없음', '확인 필요'],
      },
      { name: 'esg_interest', label: 'ESG 관심도', type: 'select', options: ['높음', '보통', '낮음', '확인 필요'] },
    ],
  },
  chargingPartner: {
    title: 'Charging Partner Form',
    subtitle: '충전사업자의 OCPP, API, 충전량, 세션 데이터 제공 가능성을 수집합니다.',
    route: '/charging-partner',
    storageKey: 'zenov_charging_partner_forms',
    tableName: 'zenov_charging_partner_forms',
    fields: [
      { name: 'operator_name', label: '충전사업자명' },
      { name: 'charger_count', label: '충전기 수', type: 'number' },
      { name: 'fast_charger_count', label: '급속 충전기 수', type: 'number' },
      {
        name: 'ocpp_support',
        label: 'OCPP 지원 여부',
        type: 'select',
        options: ['OCPP 1.6', 'OCPP 2.0.1', '미지원', '확인 필요'],
      },
      { name: 'api_available', label: 'API 제공 여부', type: 'select', options: ['가능', '일부 가능', '검토 필요', '불가'] },
      { name: 'monthly_charging_volume', label: '월 충전량', type: 'number' },
      {
        name: 'session_data_available',
        label: '충전 세션 데이터 제공 가능 여부',
        type: 'select',
        options: ['가능', '익명화 후 가능', '검토 필요', '불가'],
      },
    ],
  },
  dueDiligence: {
    title: 'Due Diligence Questionnaire',
    subtitle: 'Pilot 선정, 리드 스코어링, MRV, Deal Room 공개 가능성을 통합 검토합니다.',
    route: '/due-diligence-questionnaire',
    storageKey: 'zenov_due_diligence_responses',
    tableName: 'zenov_due_diligence_responses',
    fields: [
      { name: 'company_name', label: '회사명' },
      { name: 'business_summary', label: '주요 사업 내용', type: 'textarea' },
      { name: 'pilot_purpose', label: 'Pilot 참여 목적', type: 'textarea' },
      {
        name: 'data_types',
        label: '제공 가능한 데이터 유형',
        type: 'multiselect',
        options: ['운영 데이터', '전력 데이터', '차량 데이터', '충전 데이터', '생산 데이터', 'ERP', 'MES', 'ESG'],
      },
      { name: 'mrv_readiness', label: 'MRV 준비도', type: 'select', options: ['높음', '보통', '낮음', '확인 필요'] },
      { name: 'government_program_interest', label: '정부지원사업 관심도', type: 'select', options: ['높음', '보통', '낮음'] },
      { name: 'next_action', label: 'Next Action', type: 'select', options: ['NDA 발송', '현장 방문', '데이터 요청', '제안서 작성', 'CEO 검토', '보류'] },
    ],
  },
  dataChecklist: {
    title: 'Data Request Checklist',
    subtitle: '택시, 공장, 충전소 Pilot 검토에 필요한 자료와 전달 파일 다운로드 여부를 수집합니다.',
    route: '/data-request-checklist',
    storageKey: 'zenov_data_request_checklists',
    tableName: 'zenov_due_diligence_responses',
    fields: [
      { name: 'target_name', label: '대상 회사 / 조합명' },
      {
        name: 'download_package_checklist',
        label: '파일 다운로드 체크리스트',
        type: 'multiselect',
        options: checklistFileOptions,
      },
      {
        name: 'taxi_materials',
        label: '택시 자료',
        type: 'multiselect',
        options: ['차량 목록', '연료 종류', '운행거리', 'LPG 현황', '차고지 정보'],
      },
      {
        name: 'factory_materials',
        label: '공장 자료',
        type: 'multiselect',
        options: ['전기요금', '생산량', 'ERP 데이터', 'MES 데이터', '설비 정보'],
      },
      {
        name: 'charging_materials',
        label: '충전 자료',
        type: 'multiselect',
        options: ['충전량', '충전기 목록', 'OCPP 로그', 'API 문서', '세션 데이터'],
      },
      { name: 'submission_memo', label: '자료 제출 메모', type: 'textarea' },
    ],
  },
};

type FormTranslation = {
  title: string;
  subtitle: string;
  fields: Record<string, { label: string; options?: string[] }>;
};

const formTranslations: Record<AdminLang, Record<string, FormTranslation>> = {
  ko: Object.fromEntries(
    Object.entries(forms).map(([key, config]) => [
      key,
      {
        title: config.title,
        subtitle: config.subtitle,
        fields: Object.fromEntries(
          config.fields.map((field) => [field.name, { label: field.label, options: field.options }]),
        ),
      },
    ]),
  ) as Record<string, FormTranslation>,
  en: {
    pilotApplication: {
      title: 'Pilot Application Entry',
      subtitle: 'Collect basic pilot candidate information, NDA status, and data sharing availability.',
      fields: {
        company_name: { label: 'Company Name' },
        contact_name: { label: 'Contact Person' },
        phone: { label: 'Phone' },
        email: { label: 'Email' },
        industry: { label: 'Industry' },
        region: { label: 'Region' },
        pilot_interest: { label: 'Pilot Interest Areas', options: ['ESG', 'Carbon MRV', 'Taxi Carbon', 'Factory Intelligence', 'Charging', 'Public Programs'] },
        nda_status: { label: 'NDA Status', options: ['Available', 'Legal Review Required', 'Unavailable'] },
        data_sharing_status: { label: 'Data Sharing Availability', options: ['Available', 'Available after anonymization', 'Review Required', 'Unavailable'] },
      },
    },
    taxiSurvey: {
      title: 'Taxi Pilot Survey',
      subtitle: 'Collect vehicle, driver, garage, and charging candidate data from taxi unions and taxi companies.',
      fields: {
        union_name: { label: 'Taxi Union Name' },
        taxi_company_name: { label: 'Taxi Company Name' },
        total_vehicles: { label: 'Total Vehicles' },
        union_vehicle_count: { label: 'Taxi Union Vehicles' },
        taxi_company_vehicle_count: { label: 'Taxi Company Vehicles' },
        lpg_vehicles: { label: 'LPG Vehicles' },
        ev_vehicles: { label: 'EV Vehicles' },
        ev_convertible_vehicles: { label: 'EV Convertible Vehicles' },
        driver_count: { label: 'Drivers' },
        garage_available: { label: 'Garage Availability', options: ['Available', 'Unavailable', 'Need Confirmation'] },
        charging_candidate_site: { label: 'Charging Site Candidate', options: ['Available', 'Unavailable', 'Need Confirmation'] },
        monthly_distance: { label: 'Monthly Average Mileage' },
        monthly_fuel_cost: { label: 'Monthly Average Fuel Cost' },
      },
    },
    factoryAssessment: {
      title: 'Taxi Company Facility Site Audit',
      subtitle: 'Collect facility, garage, maintenance, washing, office, parking, electricity, rooftop, ESG, and carbon data for charging and solar feasibility review.',
      fields: {
        facility_name: { label: 'Facility Name' },
        facility_type: { label: 'Facility Type', options: ['Maintenance Shop', 'Car Wash', 'Office', 'Parking Lot / Site'] },
        managed_area_sqm: { label: 'Managed Area' },
        building_structure: { label: 'Building Structure', options: ['Integrated Building', 'Prefab', 'Container', 'Open Lot'] },
        erp_mes_usage: { label: 'ERP/MES Usage', options: ['In Use', 'Not in Use', 'Under Review'] },
        grid_connection_capacity_kw: { label: 'Grid Connection Capacity' },
        roof_ceiling_material: {
          label: 'Roof / Ceiling Material',
          options: ['Cement', 'Steel Frame', 'Sandwich Panel', 'Asphalt Shingle', 'Need Confirmation'],
        },
        monthly_power_usage: { label: 'Monthly Power Usage' },
        monthly_power_cost: { label: 'Monthly Electricity Cost' },
        carbon_data_available: { label: 'Carbon Data Availability', options: ['Available (operation/charging records)', 'Partially Available', 'Unavailable', 'Need Confirmation'] },
        esg_interest: { label: 'ESG Interest', options: ['High', 'Medium', 'Low', 'Need Confirmation'] },
      },
    },
    chargingPartner: {
      title: 'Charging Partner Form',
      subtitle: 'Collect OCPP, API, charging volume, and session data availability from charging operators.',
      fields: {
        operator_name: { label: 'Charging Operator Name' },
        charger_count: { label: 'Chargers' },
        fast_charger_count: { label: 'Fast Chargers' },
        ocpp_support: { label: 'OCPP Support', options: ['OCPP 1.6', 'OCPP 2.0.1', 'Not Supported', 'Need Confirmation'] },
        api_available: { label: 'API Availability', options: ['Available', 'Partially Available', 'Review Required', 'Unavailable'] },
        monthly_charging_volume: { label: 'Monthly Charging Volume' },
        session_data_available: { label: 'Charging Session Data Availability', options: ['Available', 'Available after anonymization', 'Review Required', 'Unavailable'] },
      },
    },
    dueDiligence: {
      title: 'Due Diligence Questionnaire',
      subtitle: 'Review pilot selection, lead scoring, MRV readiness, and Deal Room visibility in one flow.',
      fields: {
        company_name: { label: 'Company Name' },
        business_summary: { label: 'Main Business Summary' },
        pilot_purpose: { label: 'Pilot Participation Purpose' },
        data_types: { label: 'Available Data Types', options: ['Operating Data', 'Power Data', 'Vehicle Data', 'Charging Data', 'Production Data', 'ERP', 'MES', 'ESG'] },
        mrv_readiness: { label: 'MRV Readiness', options: ['High', 'Medium', 'Low', 'Need Confirmation'] },
        government_program_interest: { label: 'Public Program Interest', options: ['High', 'Medium', 'Low'] },
        next_action: { label: 'Next Action', options: ['Send NDA', 'Field Visit', 'Data Request', 'Proposal Draft', 'CEO Review', 'Hold'] },
      },
    },
    dataChecklist: {
      title: 'Data Request Checklist',
      subtitle: 'Collect requested materials and delivery file download status for taxi, factory, and charging pilots.',
      fields: {
        target_name: { label: 'Target Company / Union Name' },
        download_package_checklist: { label: 'File Download Checklist', options: salesKitFiles.slice(0, 7).map((file) => `${salesKitFileLabels.en[file.labelKey]} - ${file.filename}`) },
        taxi_materials: { label: 'Taxi Materials', options: ['Vehicle List', 'Fuel Type', 'Mileage', 'LPG Status', 'Garage Information'] },
        factory_materials: { label: 'Factory Materials', options: ['Electricity Bill', 'Production Volume', 'ERP Data', 'MES Data', 'Equipment Information'] },
        charging_materials: { label: 'Charging Materials', options: ['Charging Volume', 'Charger List', 'OCPP Logs', 'API Documents', 'Session Data'] },
        submission_memo: { label: 'Submission Memo' },
      },
    },
  },
  zh: {
    pilotApplication: {
      title: '试点申请录入',
      subtitle: '收集试点候选方基本信息、NDA 状态和数据提供可能性。',
      fields: {
        company_name: { label: '公司名称' },
        contact_name: { label: '联系人' },
        phone: { label: '联系电话' },
        email: { label: '邮箱' },
        industry: { label: '行业' },
        region: { label: '地区' },
        pilot_interest: { label: 'Pilot 关注领域', options: ['ESG', 'Carbon MRV', 'Taxi Carbon', 'Factory Intelligence', 'Charging', '政府项目'] },
        nda_status: { label: 'NDA 签署状态', options: ['可签署', '需要法务审查', '不可签署'] },
        data_sharing_status: { label: '数据提供可能性', options: ['可提供', '匿名化后可提供', '需要审查', '不可提供'] },
      },
    },
    taxiSurvey: {
      title: '出租车 Pilot 问卷',
      subtitle: '收集出租车协会和出租车公司的车辆、司机、车库和充电候选数据。',
      fields: {
        union_name: { label: '出租车协会名称' },
        taxi_company_name: { label: '出租车公司名称' },
        total_vehicles: { label: '总车辆数' },
        union_vehicle_count: { label: '协会车辆数' },
        taxi_company_vehicle_count: { label: '出租车公司车辆数' },
        lpg_vehicles: { label: 'LPG 车辆数' },
        ev_vehicles: { label: 'EV 车辆数' },
        ev_convertible_vehicles: { label: '可转换 EV 车辆数' },
        driver_count: { label: '司机人数' },
        garage_available: { label: '车库是否可用', options: ['有', '无', '需要确认'] },
        charging_candidate_site: { label: '充电站候选地', options: ['有', '无', '需要确认'] },
        monthly_distance: { label: '月平均行驶距离' },
        monthly_fuel_cost: { label: '月平均燃料费' },
      },
    },
    factoryAssessment: {
      title: '出租车公司设施场地实查',
      subtitle: '收集出租车公司内维修厂、洗车区、办公室、停车场/场地、电力、屋顶、ESG 和碳数据，用于充电站和太阳能可行性候选分析。',
      fields: {
        facility_name: { label: '设施名称' },
        facility_type: { label: '设施类型', options: ['维修厂', '洗车区', '办公室', '停车场/场地'] },
        managed_area_sqm: { label: '管理面积' },
        building_structure: { label: '建筑结构', options: ['整体建筑', '装配式', '集装箱', '露天场地'] },
        erp_mes_usage: { label: 'ERP/MES 使用情况', options: ['使用中', '未使用', '导入审查中'] },
        grid_connection_capacity_kw: { label: '电力接入容量' },
        roof_ceiling_material: { label: '屋顶/天花材料', options: ['水泥', '钢结构', '夹芯板', '沥青瓦', '需要确认'] },
        monthly_power_usage: { label: '月电力使用量' },
        monthly_power_cost: { label: '月电费' },
        carbon_data_available: { label: '碳数据持有情况', options: ['持有(运营/充电记录)', '部分持有', '无', '需要确认'] },
        esg_interest: { label: 'ESG 关注度', options: ['高', '中', '低', '需要确认'] },
      },
    },
    chargingPartner: {
      title: '充电合作伙伴表单',
      subtitle: '收集充电运营商的 OCPP、API、充电量和会话数据提供可能性。',
      fields: {
        operator_name: { label: '充电运营商名称' },
        charger_count: { label: '充电器数量' },
        fast_charger_count: { label: '快速充电器数量' },
        ocpp_support: { label: 'OCPP 支持情况', options: ['OCPP 1.6', 'OCPP 2.0.1', '不支持', '需要确认'] },
        api_available: { label: 'API 提供情况', options: ['可提供', '部分可提供', '需要审查', '不可提供'] },
        monthly_charging_volume: { label: '月充电量' },
        session_data_available: { label: '充电会话数据提供可能性', options: ['可提供', '匿名化后可提供', '需要审查', '不可提供'] },
      },
    },
    dueDiligence: {
      title: '尽调问卷',
      subtitle: '统一审查试点选择、线索评分、MRV 准备度和 Deal Room 公开可能性。',
      fields: {
        company_name: { label: '公司名称' },
        business_summary: { label: '主要业务内容' },
        pilot_purpose: { label: 'Pilot 参与目的' },
        data_types: { label: '可提供数据类型', options: ['运营数据', '电力数据', '车辆数据', '充电数据', '生产数据', 'ERP', 'MES', 'ESG'] },
        mrv_readiness: { label: 'MRV 准备度', options: ['高', '中', '低', '需要确认'] },
        government_program_interest: { label: '政府项目关注度', options: ['高', '中', '低'] },
        next_action: { label: 'Next Action', options: ['发送 NDA', '现场访问', '数据请求', '提案书 작성', 'CEO 审查', '保留'] },
      },
    },
    dataChecklist: {
      title: '数据请求清单',
      subtitle: '收集出租车、工厂和充电 Pilot 审查所需资料及交付文件下载状态。',
      fields: {
        target_name: { label: '目标公司 / 协会名称' },
        download_package_checklist: { label: '文件下载清单', options: salesKitFiles.slice(0, 7).map((file) => `${salesKitFileLabels.zh[file.labelKey]} - ${file.filename}`) },
        taxi_materials: { label: '出租车资料', options: ['车辆列表', '燃料类型', '行驶距离', 'LPG 现状', '车库信息'] },
        factory_materials: { label: '工厂资料', options: ['电费账单', '生产量', 'ERP 数据', 'MES 数据', '设备信息'] },
        charging_materials: { label: '充电资料', options: ['充电量', '充电器列表', 'OCPP 日志', 'API 文档', '会话数据'] },
        submission_memo: { label: '资料提交备注' },
      },
    },
  },
  th: {
    pilotApplication: {
      title: 'กรอกใบสมัคร Pilot',
      subtitle: 'เก็บข้อมูลพื้นฐานของผู้สมัคร Pilot สถานะ NDA และความพร้อมให้ข้อมูล',
      fields: {
        company_name: { label: 'ชื่อบริษัท' },
        contact_name: { label: 'ผู้ติดต่อ' },
        phone: { label: 'โทรศัพท์' },
        email: { label: 'อีเมล' },
        industry: { label: 'ประเภทธุรกิจ' },
        region: { label: 'ภูมิภาค' },
        pilot_interest: { label: 'พื้นที่สนใจ Pilot', options: ['ESG', 'Carbon MRV', 'Taxi Carbon', 'Factory Intelligence', 'Charging', 'โครงการภาครัฐ'] },
        nda_status: { label: 'สถานะ NDA', options: ['พร้อม', 'ต้องตรวจฝ่ายกฎหมาย', 'ไม่พร้อม'] },
        data_sharing_status: { label: 'ความพร้อมให้ข้อมูล', options: ['พร้อม', 'พร้อมหลัง anonymization', 'ต้องตรวจสอบ', 'ไม่พร้อม'] },
      },
    },
    taxiSurvey: {
      title: 'แบบสำรวจ Taxi Pilot',
      subtitle: 'เก็บข้อมูลรถ คนขับ โรงจอด และพื้นที่ที่เป็นไปได้สำหรับสถานีชาร์จจากสหกรณ์/บริษัทแท็กซี่',
      fields: {
        union_name: { label: 'ชื่อสหกรณ์แท็กซี่' },
        taxi_company_name: { label: 'ชื่อบริษัทแท็กซี่' },
        total_vehicles: { label: 'จำนวนรถทั้งหมด' },
        union_vehicle_count: { label: 'จำนวนรถของสหกรณ์แท็กซี่' },
        taxi_company_vehicle_count: { label: 'จำนวนรถของบริษัทแท็กซี่' },
        lpg_vehicles: { label: 'จำนวนรถ LPG' },
        ev_vehicles: { label: 'จำนวนรถ EV' },
        ev_convertible_vehicles: { label: 'จำนวนรถที่เปลี่ยนเป็น EV ได้' },
        driver_count: { label: 'จำนวนคนขับ' },
        garage_available: { label: 'มีโรงจอดหรือไม่', options: ['มี', 'ไม่มี', 'ต้องยืนยัน'] },
        charging_candidate_site: { label: 'มีพื้นที่ที่เป็นไปได้สำหรับสถานีชาร์จหรือไม่', options: ['มี', 'ไม่มี', 'ต้องยืนยัน'] },
        monthly_distance: { label: 'ระยะทางเฉลี่ยต่อเดือน' },
        monthly_fuel_cost: { label: 'ค่าเชื้อเพลิงเฉลี่ยต่อเดือน' },
      },
    },
    factoryAssessment: {
      title: 'ตรวจสถานที่บริษัทแท็กซี่',
      subtitle: 'เก็บข้อมูลอู่ซ่อม ล้างรถ สำนักงาน ลานจอด/พื้นที่ ไฟฟ้า หลังคา ESG และข้อมูลคาร์บอน เพื่อประเมินความเป็นไปได้ของสถานีชาร์จและ Solar',
      fields: {
        facility_name: { label: 'ชื่อสถานที่' },
        facility_type: { label: 'ประเภทสถานที่', options: ['อู่ซ่อม', 'ล้างรถ', 'สำนักงาน', 'ลานจอด / พื้นที่'] },
        managed_area_sqm: { label: 'พื้นที่บริหารจัดการ' },
        building_structure: { label: 'โครงสร้างอาคาร', options: ['อาคารรวม', 'Prefab', 'ตู้คอนเทนเนอร์', 'พื้นที่โล่ง'] },
        erp_mes_usage: { label: 'การใช้ ERP/MES', options: ['ใช้งานอยู่', 'ไม่ได้ใช้', 'กำลังพิจารณา'] },
        grid_connection_capacity_kw: { label: 'กำลังไฟฟ้าที่รับเข้า' },
        roof_ceiling_material: { label: 'วัสดุหลังคา/เพดาน', options: ['ซีเมนต์', 'โครงเหล็ก', 'แผ่น Sandwich Panel', 'Asphalt Shingle', 'ต้องยืนยัน'] },
        monthly_power_usage: { label: 'การใช้ไฟฟ้ารายเดือน' },
        monthly_power_cost: { label: 'ค่าไฟรายเดือน' },
        carbon_data_available: { label: 'ความพร้อมข้อมูลคาร์บอน', options: ['มี(ข้อมูลการเดินรถ/ชาร์จ)', 'มีบางส่วน', 'ไม่มี', 'ต้องยืนยัน'] },
        esg_interest: { label: 'ความสนใจ ESG', options: ['สูง', 'ปานกลาง', 'ต่ำ', 'ต้องยืนยัน'] },
      },
    },
    chargingPartner: {
      title: 'แบบฟอร์ม Charging Partner',
      subtitle: 'เก็บข้อมูล OCPP, API, ปริมาณชาร์จ และความพร้อมข้อมูล session จากผู้ให้บริการชาร์จ',
      fields: {
        operator_name: { label: 'ชื่อผู้ให้บริการชาร์จ' },
        charger_count: { label: 'จำนวนเครื่องชาร์จ' },
        fast_charger_count: { label: 'จำนวน Fast Charger' },
        ocpp_support: { label: 'รองรับ OCPP หรือไม่', options: ['OCPP 1.6', 'OCPP 2.0.1', 'ไม่รองรับ', 'ต้องยืนยัน'] },
        api_available: { label: 'ให้ API ได้หรือไม่', options: ['ได้', 'ได้บางส่วน', 'ต้องตรวจสอบ', 'ไม่ได้'] },
        monthly_charging_volume: { label: 'ปริมาณชาร์จรายเดือน' },
        session_data_available: { label: 'ให้ข้อมูล Charging Session ได้หรือไม่', options: ['ได้', 'ได้หลัง anonymization', 'ต้องตรวจสอบ', 'ไม่ได้'] },
      },
    },
    dueDiligence: {
      title: 'แบบสอบถาม Due Diligence',
      subtitle: 'ตรวจการคัดเลือก Pilot, Lead Scoring, MRV และความพร้อมเปิด Deal Room ในขั้นตอนเดียว',
      fields: {
        company_name: { label: 'ชื่อบริษัท' },
        business_summary: { label: 'รายละเอียดธุรกิจหลัก' },
        pilot_purpose: { label: 'วัตถุประสงค์การเข้าร่วม Pilot' },
        data_types: { label: 'ประเภทข้อมูลที่ให้ได้', options: ['ข้อมูลปฏิบัติการ', 'ข้อมูลไฟฟ้า', 'ข้อมูลรถ', 'ข้อมูลชาร์จ', 'ข้อมูลผลิต', 'ERP', 'MES', 'ESG'] },
        mrv_readiness: { label: 'ความพร้อม MRV', options: ['สูง', 'ปานกลาง', 'ต่ำ', 'ต้องยืนยัน'] },
        government_program_interest: { label: 'ความสนใจโครงการภาครัฐ', options: ['สูง', 'ปานกลาง', 'ต่ำ'] },
        next_action: { label: 'Next Action', options: ['ส่ง NDA', 'เยี่ยมพื้นที่', 'ขอข้อมูล', 'จัดทำข้อเสนอ', 'CEO Review', 'Hold'] },
      },
    },
    dataChecklist: {
      title: 'เช็กลิสต์ขอข้อมูล',
      subtitle: 'เก็บรายการเอกสารที่ต้องใช้และสถานะดาวน์โหลดไฟล์สำหรับ Taxi, Factory และ Charging Pilot',
      fields: {
        target_name: { label: 'บริษัท / สหกรณ์เป้าหมาย' },
        download_package_checklist: { label: 'เช็กลิสต์ดาวน์โหลดไฟล์', options: salesKitFiles.slice(0, 7).map((file) => `${salesKitFileLabels.th[file.labelKey]} - ${file.filename}`) },
        taxi_materials: { label: 'ข้อมูล Taxi', options: ['รายการรถ', 'ชนิดเชื้อเพลิง', 'ระยะทาง', 'สถานะ LPG', 'ข้อมูลโรงจอด'] },
        factory_materials: { label: 'ข้อมูลโรงงาน', options: ['บิลค่าไฟ', 'ปริมาณผลิต', 'ข้อมูล ERP', 'ข้อมูล MES', 'ข้อมูลอุปกรณ์'] },
        charging_materials: { label: 'ข้อมูลชาร์จ', options: ['ปริมาณชาร์จ', 'รายการเครื่องชาร์จ', 'OCPP Logs', 'API Documents', 'Session Data'] },
        submission_memo: { label: 'บันทึกการส่งข้อมูล' },
      },
    },
  },
};

function localizeFormConfig(formKey: keyof typeof forms, config: FormConfig, lang: AdminLang): FormConfig {
  const translation = formTranslations[lang][formKey] || formTranslations.ko[formKey];
  return {
    ...config,
    title: translation.title,
    subtitle: translation.subtitle,
    fields: config.fields.map((field) => {
      const translatedField = translation.fields[field.name];
      return translatedField
        ? {
            ...field,
            label: translatedField.label,
            options: translatedField.options || field.options,
          }
        : field;
    }),
  };
}

type MemberSignupRecord = {
  id: string;
  values?: Record<string, unknown>;
  analysis?: Record<string, unknown>;
};

type AdminDashboardStats = {
  signupMembers: number;
  taxiDrivers: number;
  partners: number;
  referralSignups: number;
  taxiCompanies: number;
  taxiUnions: number;
  vehicleCount: number;
  evPlanCount: number;
  monthlyDistanceKm: number;
  annualSavingKrw: number;
  estimatedCarbonReduction: string;
};

function isAuthed() {
  if (typeof window === 'undefined') return false;
  return window.sessionStorage.getItem(SESSION_KEY) === 'active';
}

function resolveLoginCode(inputCode: string, loginMode: 'admin' | 'partner') {
  const normalizedCode = inputCode.trim();
  if (
    loginMode === 'admin' &&
    normalizedCode === DASHBOARD_FILE_ADMIN_CODE
  ) {
    return {
      ok: true,
      role: 'ceo_admin',
      partnerCode: 'ZENOV',
      partnerName: 'ZENOV Dashboard / File Admin',
    };
  }
  if (
    loginMode === 'partner' &&
    (normalizedCode === ANSAN_PARTNER_LOGIN_CODE || normalizedCode === ANSAN_QR_PARTNER_CODE)
  ) {
    return {
      ok: true,
      role: 'ansan_partner_admin',
      partnerCode: ANSAN_PARTNER_LOGIN_CODE,
      partnerName: '안산교통',
    };
  }
  return {
    ok: false,
    role: '',
    partnerCode: '',
    partnerName: '',
  };
}

function emptyValues(fields: Field[]) {
  return fields.reduce<Record<string, string | string[]>>((acc, field) => {
    acc[field.name] = field.type === 'multiselect' ? [] : '';
    return acc;
  }, {});
}

function readRecords(storageKey: string): SavedRecord[] {
  if (typeof window === 'undefined') return [];
  const raw = window.localStorage.getItem(storageKey);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeRecords(storageKey: string, records: SavedRecord[]) {
  window.localStorage.setItem(storageKey, JSON.stringify(records));
}

function getStoredPortalLang(): AdminLang | null {
  if (typeof window === 'undefined') return null;
  const savedLang =
    window.localStorage.getItem('zenov_admin_dashboard_lang') ||
    window.localStorage.getItem('zenov_partner_login_lang');
  return savedLang === 'ko' || savedLang === 'en' || savedLang === 'zh' || savedLang === 'th' ? savedLang : null;
}

function makeCsv(records: SavedRecord[], fields: Field[]) {
  const headers = ['id', 'status', 'created_at', 'updated_at', ...fields.map((field) => field.name)];
  const rows = records.map((record) =>
    headers.map((header) => {
      const value =
        header in record
          ? String(record[header as keyof SavedRecord] ?? '')
          : Array.isArray(record.values[header])
            ? (record.values[header] as string[]).join('; ')
            : String(record.values[header] ?? '');
      return `"${value.replace(/"/g, '""')}"`;
    }),
  );
  return [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
}

function downloadText(filename: string, content: string, type = 'text/plain;charset=utf-8') {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function readCdKeys(): CdKeyRecord[] {
  if (typeof window === 'undefined') return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem('zenov_cd_keys') || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeCdKeys(records: CdKeyRecord[]) {
  window.localStorage.setItem('zenov_cd_keys', JSON.stringify(records));
}

function readReferralCodes(): ReferralCodeRecord[] {
  if (typeof window === 'undefined') return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem('zenov_referral_codes') || '[]');
    if (!Array.isArray(parsed)) return [];
    return parsed.map((record) => ({
      ...record,
      code_scope: record.code_scope || 'PARTNER',
      reward_basis: record.reward_basis || 'organization_scale',
      status: record.status === 'active' ? 'approved' : record.status || 'pending_approval',
    }));
  } catch {
    return [];
  }
}

function writeReferralCodes(records: ReferralCodeRecord[]) {
  window.localStorage.setItem('zenov_referral_codes', JSON.stringify(records));
}

function readMemberSignups(): MemberSignupRecord[] {
  if (typeof window === 'undefined') return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem('zenov_member_signups') || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function toDashboardNumber(value: unknown) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : 0;
}

function buildAdminDashboardStats(records: MemberSignupRecord[]): AdminDashboardStats {
  return records.reduce<AdminDashboardStats>(
    (stats, record) => {
      const values = record.values || {};
      const analysis = record.analysis || {};
      const memberType = String(values.member_type || '');
      stats.signupMembers += 1;
      if (memberType === 'driver') stats.taxiDrivers += 1;
      if (memberType === 'taxi_company') stats.taxiCompanies += 1;
      if (memberType === 'taxi_union') stats.taxiUnions += 1;
      if (memberType === 'taxi_company' || memberType === 'taxi_union') stats.partners += 1;
      if (String(values.referral_code || '').trim()) stats.referralSignups += 1;
      stats.vehicleCount += toDashboardNumber(values.vehicle_count);
      stats.evPlanCount += toDashboardNumber(values.ev_planned_count);
      stats.monthlyDistanceKm += toDashboardNumber(values.monthly_distance_km || values.monthly_total_distance_km);
      stats.annualSavingKrw += toDashboardNumber(analysis.annual_saving);
      return stats;
    },
    {
      signupMembers: 0,
      taxiDrivers: 0,
      partners: 0,
      referralSignups: 0,
      taxiCompanies: 0,
      taxiUnions: 0,
      vehicleCount: 0,
      evPlanCount: 0,
      monthlyDistanceKm: 0,
      annualSavingKrw: 0,
      estimatedCarbonReduction: '실제 운행 데이터 확보 후 산정',
    },
  );
}

function getSessionContext() {
  if (typeof window === 'undefined') {
    return {
      role: '',
      partnerCode: '',
      partnerName: '',
    };
  }
  return {
    role: window.sessionStorage.getItem(SESSION_ROLE_KEY) || '',
    partnerCode: window.sessionStorage.getItem(SESSION_PARTNER_CODE_KEY) || '',
    partnerName: window.sessionStorage.getItem(SESSION_PARTNER_NAME_KEY) || '',
  };
}

function isAdminRole(role: string) {
  return role === 'ceo_admin';
}

function canIssuePartnerCode(session: { role: string; partnerCode: string; partnerName: string }) {
  return isAdminRole(session.role);
}

function ensureAnsanReferralSeed() {
  if (typeof window === 'undefined') return;
  const records = readReferralCodes();
  const exists = records.some((record) => record.referral_code === ANSAN_REFERRAL_CODE);
  if (exists) return;

  const now = new Date().toISOString();
  const ansanRecord: ReferralCodeRecord = {
    id: 'zenov_referral_code_ansan_transport_seed',
    referral_code: ANSAN_REFERRAL_CODE,
    code_scope: 'PARTNER',
    owner_partner_code: ANSAN_PARTNER_LOGIN_CODE,
    parent_partner_code: 'ZENOV',
    issued_by_login_code: ANSAN_PARTNER_LOGIN_CODE,
    reward_basis: 'organization_scale',
    reward_policy_label: '조직 규모 기반 운영 혜택 후보',
    hub_name: '안산교통',
    partner_name: '안산교통 대표 파트너',
    partner_email: '',
    partner_type: 'taxi_company',
    region: 'Ansan',
    status: 'approved',
    created_at: now,
    approved_at: now,
    metadata: {
      document_type: 'PILOT_REFERRAL_CODE',
      evidence_file: false,
      production_ready_trigger: false,
      commercial_ready_trigger: false,
    },
  };
  writeReferralCodes([ansanRecord, ...records]);
}

function referralStatusLabel(status: ReferralCodeRecord['status'], t: (typeof adminI18n)[AdminLang]) {
  if (status === 'approved') return t.referral_status_approved;
  if (status === 'disabled') return t.referral_status_disabled;
  return t.referral_status_pending_approval;
}

function readDeliveries(): DeliveryRecord[] {
  if (typeof window === 'undefined') return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem('zenov_file_delivery_manifests') || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeDeliveries(records: DeliveryRecord[]) {
  window.localStorage.setItem('zenov_file_delivery_manifests', JSON.stringify(records));
}

function syncTaxiCarbonDiagnosis(record: SavedRecord) {
  const values = record.values;
  const totalVehicles = Number(values.total_vehicles || 0);
  const lpgVehicles = Number(values.lpg_vehicles || 0);
  const evVehicles = Number(values.ev_vehicles || 0);
  const evConvertibleVehicles = Number(values.ev_convertible_vehicles || 0);
  const monthlyDistance = Number(values.monthly_distance || 0);
  const monthlyFuelCost = Number(values.monthly_fuel_cost || 0);
  const annualDistance = monthlyDistance * 12 * Math.max(totalVehicles, 1);
  const estimatedAnnualReduction = Math.round(evConvertibleVehicles * 6.4 * 10) / 10;
  const estimatedKoc = Math.round(estimatedAnnualReduction);
  const estimatedCarbonRevenue = estimatedKoc * 70000;

  const diagnosis = {
    id: `taxi_carbon_os_diagnosis_${Date.now()}`,
    source_record_id: record.id,
    source_storage_key: 'zenov_taxi_pilot_surveys',
    synced_at: new Date().toISOString(),
    document_type: 'TAXI_CARBON_OS_DIAGNOSIS_INPUT',
    evidence_file: false,
    production_ready_trigger: false,
    commercial_ready_trigger: false,
    partner_name: values.union_name || '',
    total_vehicles: totalVehicles,
    lpg_vehicles: lpgVehicles,
    ev_vehicles: evVehicles,
    ev_convertible_vehicles: evConvertibleVehicles,
    driver_count: Number(values.driver_count || 0),
    garage_available: values.garage_available || '',
    charging_candidate_site: values.charging_candidate_site || '',
    monthly_distance: monthlyDistance,
    monthly_fuel_cost: monthlyFuelCost,
    derived: {
      annual_distance: annualDistance,
      lpg_ratio: totalVehicles ? Math.round((lpgVehicles / totalVehicles) * 1000) / 10 : 0,
      ev_ratio: totalVehicles ? Math.round((evVehicles / totalVehicles) * 1000) / 10 : 0,
      estimated_annual_reduction_tco2e: estimatedAnnualReduction,
      estimated_koc_candidate: estimatedKoc,
      estimated_carbon_revenue_krw: estimatedCarbonRevenue,
    },
  };

  const existing = JSON.parse(window.localStorage.getItem('zenov_taxi_carbon_os_diagnosis_inputs') || '[]');
  const next = [diagnosis, ...(Array.isArray(existing) ? existing : [])];
  window.localStorage.setItem('zenov_taxi_carbon_os_diagnosis_inputs', JSON.stringify(next));
}

function makeCdKey() {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const segment = () =>
    Array.from({ length: 4 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]).join('');
  return `ZENOV-PILOT-${segment()}-${segment()}-${new Date().getFullYear()}`;
}

function makeReferralCode(region = 'KR', codeScope: 'PARTNER' | 'DRIVER' = 'PARTNER') {
  const normalizedRegion = region
    .replace(/[^A-Za-z0-9가-힣]/g, '')
    .slice(0, 4)
    .toUpperCase();
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const suffix = Array.from({ length: 5 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]).join('');
  const prefix = codeScope === 'DRIVER' ? 'ZENOV-DRV' : 'ZENOV-REF';
  return `${prefix}-${normalizedRegion || 'KR'}-${suffix}`;
}

async function getSupabaseAccessTokenForPortal() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    return {
      token: '',
      userId: '',
      status: 'SUPABASE_ENV_MISSING',
    };
  }

  const supabase = createClient(url, anonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
    },
  });
  const sessionResult = await supabase.auth.getSession();
  const existingSession = sessionResult.data.session;
  if (existingSession?.access_token && existingSession.user?.id) {
    return {
      token: existingSession.access_token,
      userId: existingSession.user.id,
      status: 'SUPABASE_EXISTING_SESSION',
    };
  }

  const anonymousResult = await supabase.auth.signInAnonymously();
  const anonymousSession = anonymousResult.data.session;
  if (anonymousResult.error || !anonymousSession?.access_token || !anonymousSession.user?.id) {
    return {
      token: '',
      userId: '',
      status: `SUPABASE_ANONYMOUS_AUTH_FAILED:${anonymousResult.error?.message || 'no_session'}`,
    };
  }

  return {
    token: anonymousSession.access_token,
    userId: anonymousSession.user.id,
    status: 'SUPABASE_ANONYMOUS_SESSION_CREATED',
  };
}

async function persistReferralCodeToDb(record: ReferralCodeRecord) {
  const auth = await getSupabaseAccessTokenForPortal();
  const response = await fetch('/api/platform/referral-code', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
    },
    body: JSON.stringify({
      referral_code: record.referral_code,
      code_type: record.code_scope === 'DRIVER' ? 'DRIVER' : 'PARTNER',
      owner_user_id: auth.userId,
      company_id: record.parent_partner_code === ANSAN_REFERRAL_CODE || record.owner_partner_code === ANSAN_PARTNER_LOGIN_CODE ? ANSAN_COMPANY_ID : '',
      status: record.code_scope === 'DRIVER' ? 'ACTIVE' : 'PENDING',
      source: 'pilot_portal_referral_code_page',
      metadata: record.metadata,
    }),
  });
  const result = await response.json();
  return {
    ...result,
    auth_status: auth.status,
  };
}

function Guard({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);
  const pathname = usePathname();
  const adminOnlyPath =
    pathname === '/dashboard' || pathname === '/referral-code' || pathname === '/file-delivery';

  useEffect(() => {
    setAuthed(isAuthed());
    setReady(true);
  }, []);

  if (!ready) return <main className="portal-shell">Loading...</main>;
  if (!authed) {
    const t = adminI18n.ko;
    return (
      <main className="portal-shell">
        <section className="portal-card">
          <p className="eyebrow">{adminOnlyPath ? 'ZENOV ADMIN ACCESS' : t.login_eyebrow}</p>
          <h1>{adminOnlyPath ? '관리자 로그인이 필요합니다' : t.login_required_title}</h1>
          <p className="muted">
            {adminOnlyPath
              ? '대시보드와 코드/파일 관리 화면은 /admin-login 로그인 후 사용할 수 있습니다.'
              : t.login_required_desc}
          </p>
          <Link className="primary-link" href={adminOnlyPath ? '/admin-login' : '/partner-login'}>
            {adminOnlyPath ? '관리자 로그인' : t.login_title}
          </Link>
        </section>
      </main>
    );
  }
  return <>{children}</>;
}

function PortalLanguageTabs({ lang, setLang, label }: { lang: AdminLang; setLang: (lang: AdminLang) => void; label: string }) {
  return (
    <div className="language-tabs" aria-label={label}>
      <span className="language-tabs-title">{label}</span>
      {adminLanguageOptions.map((option) => (
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
  );
}

function Header({ t = adminI18n.ko }: { t?: (typeof adminI18n)[AdminLang] }) {
  const session = getSessionContext();
  const isAdmin = isAdminRole(session.role);

  return (
    <header className="portal-header">
      <Link href="/" className="brand">
        {t.brand}
      </Link>
      <nav>
        <Link href="/pilot-application">{t.nav_pilot}</Link>
        <Link href="/taxi-survey">{t.nav_taxi}</Link>
        <Link href="/factory-assessment">{t.nav_factory}</Link>
        <Link href="/charging-partner">{t.nav_charging}</Link>
        {isAdmin ? <Link href="/referral-code">{t.menu_referral_code}</Link> : null}
        {isAdmin ? <Link href="/dashboard">{t.nav_dashboard}</Link> : null}
      </nav>
    </header>
  );
}

function GovernanceBanner() {
  return (
    <section className="governance-banner">
      <strong>Governance Guard</strong>
      <span>DOCUMENT_TYPE=PILOT_ACQUISITION_FORM</span>
      <span>EVIDENCE_FILE=false</span>
      <span>PRODUCTION_READY_TRIGGER=false</span>
      <span>COMMERCIAL_READY_TRIGGER=false</span>
    </section>
  );
}

function DeliveryFilesPanel({ t = adminI18n.ko, lang = 'ko' }: { t?: (typeof adminI18n)[AdminLang]; lang?: AdminLang }) {
  function printPanel() {
    window.setTimeout(() => window.print(), 80);
  }

  const fileBadges = ['NDA 대기', '검토 중', '데이터 요청', '제안 준비', 'Pilot 후보', 'MRV 검토'];

  return (
    <section className="portal-card delivery-files-panel">
      <div className="section-title-row">
        <div>
          <p className="eyebrow">PILOT DELIVERY PACKAGE</p>
          <h2>{t.delivery_title}</h2>
          <p className="muted">{t.delivery_desc}</p>
        </div>
        <button type="button" className="secondary-button" onClick={printPanel}>
          {t.pdf_print}
        </button>
      </div>
      <div className="download-grid">
        {salesKitFiles.map((file, index) => (
          <Link key={file.filename} href={`/files/${file.slug}`} className="download-card">
            <span>{salesKitFileLabels[lang][file.labelKey]}</span>
            <em className="status-badge">{fileBadges[index % fileBadges.length]}</em>
            <strong>{t.open_apply}</strong>
            <small>{file.filename}</small>
          </Link>
        ))}
      </div>
    </section>
  );
}

function FieldInput({
  field,
  value,
  onChange,
  selectPlaceholder = '선택',
}: {
  field: Field;
  value: string | string[];
  onChange: (value: string | string[]) => void;
  selectPlaceholder?: string;
}) {
  if (field.type === 'textarea') {
    return (
      <textarea
        value={String(value)}
        placeholder={field.placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    );
  }

  if (field.type === 'select') {
    return (
      <select value={String(value)} onChange={(event) => onChange(event.target.value)}>
        <option value="">{selectPlaceholder}</option>
        {field.options?.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  }

  if (field.type === 'multiselect') {
    const selected = Array.isArray(value) ? value : [];
    return (
      <div className="check-grid">
        {field.options?.map((option) => (
          <label key={option} className="check-item">
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={(event) => {
                if (event.target.checked) onChange([...selected, option]);
                else onChange(selected.filter((item) => item !== option));
              }}
            />
            {option}
          </label>
        ))}
      </div>
    );
  }

  return (
    <input
      type={field.type || 'text'}
      value={String(value)}
      placeholder={field.placeholder}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}

export function AdminLoginPage({ mode }: { mode?: 'admin' | 'partner' }) {
  const [lang, setLang] = useState<AdminLang>('ko');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const codeInputRef = useRef<HTMLInputElement>(null);
  const pathname = usePathname();
  const isPartnerLogin = mode ? mode === 'partner' : pathname === '/partner-login';
  const loginMode = isPartnerLogin ? 'partner' : 'admin';
  const t = adminI18n[lang];

  useEffect(() => {
    const savedLang = getStoredPortalLang();
    if (savedLang) {
      setLang(savedLang);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem('zenov_partner_login_lang', lang);
    window.localStorage.setItem('zenov_admin_dashboard_lang', lang);
  }, [lang]);

  function handleLogin() {
    const submittedCode = codeInputRef.current?.value || code;
    const loginResult = resolveLoginCode(submittedCode, loginMode);
    if (!loginResult.ok) {
      setError(t.login_error);
      return;
    }
    window.sessionStorage.setItem(SESSION_KEY, 'active');
    window.sessionStorage.setItem(SESSION_ROLE_KEY, loginResult.role);
    window.sessionStorage.setItem(SESSION_PARTNER_CODE_KEY, loginResult.partnerCode);
    window.sessionStorage.setItem(SESSION_PARTNER_NAME_KEY, loginResult.partnerName);
    ensureAnsanReferralSeed();
    window.location.href = isAdminRole(loginResult.role) ? '/dashboard' : '/partner-dashboard';
  }

  function submit(event: React.FormEvent) {
    event.preventDefault();
    handleLogin();
  }

  return (
    <main className={`portal-shell login-shell ${isPartnerLogin ? 'partner-login-shell' : 'admin-login-shell'}`}>
      <section className="login-card">
        <PortalLanguageTabs lang={lang} setLang={setLang} label={t.language} />
        <p className="eyebrow">{isPartnerLogin ? t.login_eyebrow : 'ZENOV Admin Access'}</p>
        <h1>{isPartnerLogin ? t.login_title : '관리자 로그인'}</h1>
        <p className="muted">
          {isPartnerLogin
            ? t.login_desc
            : '관리자 대시보드와 파일 관리 화면은 관리자 비밀번호로만 접근합니다. 파트너 코드는 파트너 로그인에서 사용하세요.'}
        </p>
        <form onSubmit={submit} className="login-form">
          <label>
            {isPartnerLogin ? t.login_code_label : '관리자 비밀번호'}
            <input
              ref={codeInputRef}
              value={code}
              onChange={(event) => setCode(event.target.value)}
              onInput={(event) => setCode(event.currentTarget.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  handleLogin();
                }
              }}
              type="password"
              placeholder={isPartnerLogin ? t.code_placeholder : '관리자 비밀번호 입력'}
            />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button type="button" onClick={handleLogin}>
            {t.login_button}
          </button>
        </form>
      </section>
      {isPartnerLogin ? <DeliveryFilesPanel t={t} lang={lang} /> : null}
    </main>
  );
}

export function DashboardPage() {
  const [lang, setLang] = useState<AdminLang>('ko');
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [cdKeyCount, setCdKeyCount] = useState(0);
  const [referralCodeCount, setReferralCodeCount] = useState(0);
  const [deliveryCount, setDeliveryCount] = useState(0);
  const [codeRecords, setCodeRecords] = useState<ReferralCodeRecord[]>([]);
  const [signupRecords, setSignupRecords] = useState<MemberSignupRecord[]>([]);
  const [adminStats, setAdminStats] = useState<AdminDashboardStats>({
    signupMembers: 0,
    taxiDrivers: 0,
    partners: 0,
    referralSignups: 0,
    taxiCompanies: 0,
    taxiUnions: 0,
    vehicleCount: 0,
    evPlanCount: 0,
    monthlyDistanceKm: 0,
    annualSavingKrw: 0,
    estimatedCarbonReduction: '실제 운행 데이터 확보 후 산정',
  });
  const [sessionContext, setSessionContext] = useState({ role: '', partnerCode: '', partnerName: '' });
  const [sessionReady, setSessionReady] = useState(false);
  const t = adminI18n[lang];

  useEffect(() => {
    const savedLang = getStoredPortalLang();
    if (savedLang) {
      setLang(savedLang);
    }
    setCounts(
      Object.fromEntries(
        Object.values(forms).map((config) => [config.storageKey, readRecords(config.storageKey).length]),
      ),
    );
    ensureAnsanReferralSeed();
    setCdKeyCount(readCdKeys().length);
    const referralRecords = readReferralCodes();
    setReferralCodeCount(referralRecords.length);
    setCodeRecords(referralRecords);
    setDeliveryCount(readDeliveries().length);
    const memberSignupRecords = readMemberSignups();
    setSignupRecords(memberSignupRecords);
    setAdminStats(buildAdminDashboardStats(memberSignupRecords));
    setSessionContext(getSessionContext());
    setSessionReady(true);
  }, []);

  useEffect(() => {
    window.localStorage.setItem('zenov_admin_dashboard_lang', lang);
    window.localStorage.setItem('zenov_partner_login_lang', lang);
  }, [lang]);

  const total =
    Object.values(counts).reduce((sum, count) => sum + count, 0) + cdKeyCount + referralCodeCount + deliveryCount;
  const isAdmin = isAdminRole(sessionContext.role);

  return (
    <Guard>
      <main className="portal-shell">
        <PortalLanguageTabs lang={lang} setLang={setLang} label={t.language} />
        <Header t={t} />
        {!sessionReady ? (
          <section className="portal-card">
            <p className="eyebrow">LOADING</p>
            <h1>세션 확인 중</h1>
            <p className="muted">관리자 권한을 확인한 뒤 대시보드를 표시합니다.</p>
          </section>
        ) : !isAdmin ? (
          <section className="portal-card">
            <p className="eyebrow">ADMIN ONLY</p>
            <h1>관리자 전용 대시보드</h1>
            <p className="muted">레퍼럴 코드와 파트너 코드 조회 및 발급은 관리자만 사용할 수 있습니다.</p>
            <Link href="/partner-dashboard" className="primary-link">
              파트너 대시보드로 이동
            </Link>
          </section>
        ) : null}
        {sessionReady && isAdmin ? (
          <>
        <section className="hero-panel">
          <div>
            <p className="eyebrow">{t.eyebrow}</p>
            <h1>{t.title}</h1>
            <p>{t.desc}</p>
          </div>
          <div className="hero-status">
            <span>STATUS</span>
            <strong>FROZEN</strong>
            <small>{t.frozen_note}</small>
          </div>
        </section>
        <section className="portal-card">
          <p className="eyebrow">LOGIN SCOPE</p>
          <h2>{sessionContext.partnerName || 'ZENOV'}</h2>
          <p className="muted">관리자 세션 확인 완료. 발급된 레퍼럴 코드와 파트너 코드 원장은 이 대시보드와 관리자 코드 관리 화면에서만 확인할 수 있습니다.</p>
        </section>
        <section className="portal-card">
          <p className="eyebrow">ADMIN KPI SUMMARY</p>
          <h2>대시보드 통계</h2>
          <p className="muted">일반 회원 화면에는 코드 번호를 노출하지 않습니다. 관리자 대시보드에서는 발급 현황과 코드 원장을 통제합니다.</p>
          <div className="metric-grid">
            <article>
              <span>전체 가입자 수</span>
              <strong>{adminStats.signupMembers}</strong>
            </article>
            <article>
              <span>택시 기사 수</span>
              <strong>{adminStats.taxiDrivers}</strong>
            </article>
            <article>
              <span>파트너 수</span>
              <strong>{adminStats.partners}</strong>
            </article>
            <article>
              <span>추천 가입 수</span>
              <strong>{adminStats.referralSignups}</strong>
            </article>
            <article>
              <span>EV 전환 예상 수</span>
              <strong>{adminStats.evPlanCount}</strong>
            </article>
            <article>
              <span>예상 절감액</span>
              <strong>{adminStats.annualSavingKrw.toLocaleString('ko-KR')}원</strong>
            </article>
            <article>
              <span>예상 탄소감축량</span>
              <strong>{adminStats.estimatedCarbonReduction}</strong>
            </article>
            <article>
              <span>월 주행거리</span>
              <strong>{adminStats.monthlyDistanceKm.toLocaleString('ko-KR')}km</strong>
            </article>
            <article>
              <span>세부 파트너 유형</span>
              <strong>회사 {adminStats.taxiCompanies} / 조합 {adminStats.taxiUnions}</strong>
            </article>
          </div>
        </section>
        <section className="portal-card">
          <p className="eyebrow">PILOT CONVERSION FUNNEL</p>
          <h2>ZENOV Pilot Funnel</h2>
          <p className="muted">가입, 파트너, EV 전환 후보, 파일 검토 흐름을 한눈에 보는 관리자용 전환 퍼널입니다.</p>
          <div className="zenov-funnel">
            <article style={{ '--bar': '100%' } as React.CSSProperties}>
              <span>전체 가입</span>
              <strong>{adminStats.signupMembers}</strong>
              <small>Self-Service Diagnosis</small>
            </article>
            <article style={{ '--bar': `${Math.max(18, Math.min(100, adminStats.signupMembers ? (adminStats.partners / adminStats.signupMembers) * 100 : 26))}%` } as React.CSSProperties}>
              <span>파트너 전환</span>
              <strong>{adminStats.partners}</strong>
              <small>Taxi / Union / Company</small>
            </article>
            <article style={{ '--bar': `${Math.max(18, Math.min(100, adminStats.signupMembers ? (adminStats.evPlanCount / adminStats.signupMembers) * 100 : 34))}%` } as React.CSSProperties}>
              <span>EV 후보</span>
              <strong>{adminStats.evPlanCount}</strong>
              <small>ROI Candidate</small>
            </article>
            <article style={{ '--bar': `${Math.max(18, Math.min(100, deliveryCount * 18 || 24))}%` } as React.CSSProperties}>
              <span>파일 검토</span>
              <strong>{deliveryCount}</strong>
              <small>Deal Room / Data Room</small>
            </article>
          </div>
        </section>
        <section className="portal-card">
          <p className="eyebrow">ADMIN CODE LEDGER</p>
          <h2>발급된 레퍼럴 코드 / 파트너 코드 원장</h2>
          <p className="muted">파일 폴더와 코드 발급 화면에 저장된 코드 내용을 관리자 대시보드에서 함께 확인합니다. 이 영역은 관리자 비밀번호 세션에서만 렌더링됩니다.</p>
          <div className="form-layout">
            <div className="preview-panel">
              <h3>파트너 코드</h3>
              {codeRecords.filter((record) => record.code_scope === 'PARTNER').length === 0 ? (
                <p className="muted">발급된 파트너 코드가 없습니다.</p>
              ) : (
                <div className="saved-list">
                  {codeRecords
                    .filter((record) => record.code_scope === 'PARTNER')
                    .map((record) => (
                      <p key={record.id}>
                        <strong>{record.hub_name || record.partner_name || '-'}</strong>
                        <br />
                        파트너 코드: <code>{record.referral_code}</code>
                        <br />
                        상태: <span className="status-badge">{referralStatusLabel(record.status, t)}</span>
                        <br />
                        발급일: {record.created_at}
                      </p>
                    ))}
                </div>
              )}
            </div>
            <div className="preview-panel">
              <h3>개인 레퍼럴 코드</h3>
              {codeRecords.filter((record) => record.code_scope === 'DRIVER').length === 0 ? (
                <p className="muted">발급된 개인 레퍼럴 코드가 없습니다.</p>
              ) : (
                <div className="saved-list">
                  {codeRecords
                    .filter((record) => record.code_scope === 'DRIVER')
                    .map((record) => (
                      <p key={record.id}>
                        <strong>{record.partner_name || '-'}</strong>
                        <br />
                        레퍼럴 코드: <code>{record.referral_code}</code>
                        <br />
                        상태: <span className="status-badge">{referralStatusLabel(record.status, t)}</span>
                        <br />
                        발급일: {record.created_at}
                      </p>
                    ))}
                </div>
              )}
            </div>
          </div>
        </section>
        <DeliveryFilesPanel t={t} lang={lang} />
        <section className="portal-card">
          <p className="eyebrow">ADMIN QUICK ACTIONS</p>
          <h2>관리자 전용 작업</h2>
          <p className="muted">아래 메뉴는 관리자 비밀번호 세션에서만 열립니다. 파일 폴더 내용은 이 대시보드 안에 통합되었습니다.</p>
          <div className="menu-grid">
            <Link href="/referral-code" className="menu-card">
              <span>레퍼럴 코드 / 파트너 코드 발급</span>
              <small>{referralCodeCount} 저장</small>
            </Link>
          </div>
        </section>
          </>
        ) : null}
      </main>
    </Guard>
  );
}

export function CdKeyPage() {
  const [records, setRecords] = useState<CdKeyRecord[]>([]);
  const [organizationName, setOrganizationName] = useState('');
  const [recipientName, setRecipientName] = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [accountType, setAccountType] = useState('taxi_union');
  const [expiresAt, setExpiresAt] = useState('');
  const [scope, setScope] = useState<string[]>(['pilot_portal']);
  const [message, setMessage] = useState('');

  const scopeOptions = ['pilot_portal', 'taxi_survey', 'factory_assessment', 'charging_partner', 'due_diligence', 'file_delivery'];

  useEffect(() => {
    setRecords(readCdKeys());
  }, []);

  function toggleScope(item: string, checked: boolean) {
    setScope((current) => (checked ? [...current, item] : current.filter((value) => value !== item)));
  }

  function issueKey() {
    const now = new Date().toISOString();
    const record: CdKeyRecord = {
      id: `zenov_cd_key_${Date.now()}`,
      cd_key: makeCdKey(),
      organization_name: organizationName,
      recipient_name: recipientName,
      recipient_email: recipientEmail,
      account_type: accountType,
      license_scope: scope,
      expires_at: expiresAt,
      status: 'active',
      created_at: now,
      metadata: {
        document_type: 'PILOT_ACCESS_CODE',
        evidence_file: false,
        production_ready_trigger: false,
        commercial_ready_trigger: false,
      },
    };
    const next = [record, ...records];
    writeCdKeys(next);
    setRecords(next);
    setMessage(`CD Key가 발급되었습니다: ${record.cd_key}`);
  }

  function downloadLatest() {
    if (!records[0]) return;
    downloadText(`${records[0].cd_key}.txt`, JSON.stringify(records[0], null, 2), 'application/json;charset=utf-8');
  }

  return (
    <Guard>
      <main className="portal-shell">
        <Header />
        <section className="portal-card">
          <p className="eyebrow">PILOT ACCESS CODE</p>
          <h1>CD Key 발급</h1>
          <p className="muted">Pilot 포털 접근용 CD Key를 발급합니다. 이 키는 Evidence가 아니며 상태 전이를 유발하지 않습니다.</p>
        </section>
        <GovernanceBanner />
        <section className="form-layout">
          <form className="portal-form" onSubmit={(event) => event.preventDefault()}>
            <label>
              회사 / 조합명
              <input value={organizationName} onChange={(event) => setOrganizationName(event.target.value)} />
            </label>
            <label>
              수신자명
              <input value={recipientName} onChange={(event) => setRecipientName(event.target.value)} />
            </label>
            <label>
              수신자 이메일
              <input type="email" value={recipientEmail} onChange={(event) => setRecipientEmail(event.target.value)} />
            </label>
            <label>
              계정 유형
              <select value={accountType} onChange={(event) => setAccountType(event.target.value)}>
                <option value="taxi_union">택시조합</option>
                <option value="taxi_company">법인택시</option>
                <option value="factory">공장</option>
                <option value="charging_operator">충전사업자</option>
                <option value="partner">파트너</option>
              </select>
            </label>
            <label>
              만료일
              <input type="date" value={expiresAt} onChange={(event) => setExpiresAt(event.target.value)} />
            </label>
            <label>
              권한 범위
              <div className="check-grid">
                {scopeOptions.map((item) => (
                  <label key={item} className="check-item">
                    <input
                      type="checkbox"
                      checked={scope.includes(item)}
                      onChange={(event) => toggleScope(item, event.target.checked)}
                    />
                    {item}
                  </label>
                ))}
              </div>
            </label>
            <div className="action-row">
              <button type="button" onClick={issueKey}>
                CD Key 발급
              </button>
              <button type="button" onClick={downloadLatest} disabled={records.length === 0}>
                최신 Key 파일 다운로드
              </button>
            </div>
            {message && <p className="form-success">{message}</p>}
          </form>
          <aside className="preview-panel">
            <h2>Issued CD Keys</h2>
            <p className="muted">브라우저 로컬 저장소에 보관됩니다. 운영 DB 적용은 별도 migration 이후 연결합니다.</p>
            <div className="saved-list">
              {records.length === 0 ? (
                <p>발급된 CD Key가 없습니다.</p>
              ) : (
                records.map((record) => (
                  <p key={record.id}>
                    <strong>{record.cd_key}</strong>
                    <br />
                    {record.organization_name || '-'} / {record.account_type}
                    <br />
                    {record.created_at}
                  </p>
                ))
              )}
            </div>
          </aside>
        </section>
      </main>
    </Guard>
  );
}

export function ReferralCodePage() {
  const [records, setRecords] = useState<ReferralCodeRecord[]>([]);
  const [hubName, setHubName] = useState('');
  const [partnerName, setPartnerName] = useState('');
  const [partnerEmail, setPartnerEmail] = useState('');
  const [partnerType, setPartnerType] = useState('taxi_union');
  const [region, setRegion] = useState('');
  const [codeScope, setCodeScope] = useState<'PARTNER' | 'DRIVER'>('DRIVER');
  const [parentDriverId, setParentDriverId] = useState('');
  const [message, setMessage] = useState('');
  const [lang, setLang] = useState<AdminLang>('ko');
  const [sessionContext, setSessionContext] = useState({ role: '', partnerCode: '', partnerName: '' });
  const [sessionReady, setSessionReady] = useState(false);
  const t = adminI18n[lang];
  const partnerCodeIssueAllowed = canIssuePartnerCode(sessionContext);

  useEffect(() => {
    const savedLang = getStoredPortalLang();
    if (savedLang) {
      setLang(savedLang);
    }
    ensureAnsanReferralSeed();
    const currentSession = getSessionContext();
    setSessionContext(currentSession);
    if (canIssuePartnerCode(currentSession)) {
      setCodeScope('PARTNER');
    } else {
      setCodeScope('DRIVER');
    }
    if (currentSession.partnerCode === ANSAN_PARTNER_LOGIN_CODE) {
      setHubName('안산교통');
      setPartnerName('안산교통 하위 추천 파트너');
      setPartnerType('taxi_company');
      setRegion('Ansan');
    }
    setRecords(readReferralCodes());
    setSessionReady(true);
  }, []);

  useEffect(() => {
    window.localStorage.setItem('zenov_admin_dashboard_lang', lang);
    window.localStorage.setItem('zenov_partner_login_lang', lang);
  }, [lang]);

  async function issueReferralCode() {
    const now = new Date().toISOString();
    const currentSession = getSessionContext();
    if (codeScope === 'PARTNER' && !canIssuePartnerCode(currentSession)) {
      setMessage('파트너 코드는 관리자 권한에서만 발행할 수 있습니다. 일반 회원은 코드 조회 및 발급이 불가합니다.');
      setCodeScope('DRIVER');
      return;
    }
    const isAnsanPartner = currentSession.partnerCode === ANSAN_PARTNER_LOGIN_CODE;
    const record: ReferralCodeRecord = {
      id: `zenov_referral_code_${Date.now()}`,
      referral_code: codeScope === 'PARTNER' && isAnsanPartner ? ANSAN_REFERRAL_CODE : makeReferralCode(region || (isAnsanPartner ? 'ANSAN' : 'KR'), codeScope),
      code_scope: codeScope,
      owner_partner_code: isAnsanPartner ? ANSAN_PARTNER_LOGIN_CODE : currentSession.partnerCode || '',
      parent_partner_code: isAnsanPartner ? ANSAN_REFERRAL_CODE : currentSession.partnerCode || '',
      parent_driver_id: codeScope === 'DRIVER' ? parentDriverId : '',
      issued_by_login_code: currentSession.partnerCode || '',
      reward_basis: codeScope === 'DRIVER' ? 'referral_count' : 'organization_scale',
      reward_policy_label:
        codeScope === 'DRIVER' ? '개인 추천 수 기반 포인트/혜택 후보' : '조직 규모 기반 운영 혜택 후보',
      hub_name: hubName,
      partner_name: partnerName,
      partner_email: partnerEmail,
      partner_type: partnerType,
      region,
      status: codeScope === 'DRIVER' || (isAnsanPartner && codeScope === 'PARTNER') ? 'approved' : 'pending_approval',
      created_at: now,
      approved_at: codeScope === 'DRIVER' || (isAnsanPartner && codeScope === 'PARTNER') ? now : undefined,
      metadata: {
        document_type: 'PILOT_REFERRAL_CODE',
        evidence_file: false,
        production_ready_trigger: false,
        commercial_ready_trigger: false,
      },
    };
    const next = [record, ...records];
    writeReferralCodes(next);
    setRecords(next);
    setMessage(`${t.referral_created}: ${record.referral_code} / DB 저장 확인 중`);

    try {
      const dbResult = await persistReferralCodeToDb(record);
      const dbStatus = dbResult.supabase_inserted ? 'SUPABASE_INSERTED' : dbResult.status || 'SUPABASE_PENDING';
      const updatedRecord = {
        ...record,
        db_delivery_status: dbStatus,
        db_error_message: dbResult.error || dbResult.auth_status || '',
      };
      const updated = [updatedRecord, ...records];
      writeReferralCodes(updated);
      setRecords(updated);
      setMessage(`${t.referral_created}: ${record.referral_code} / DB=${dbStatus}`);
    } catch (error) {
      const updatedRecord = {
        ...record,
        db_delivery_status: 'FAILED',
        db_error_message: error instanceof Error ? error.message : 'unknown_db_error',
      };
      const updated = [updatedRecord, ...records];
      writeReferralCodes(updated);
      setRecords(updated);
      setMessage(`${t.referral_created}: ${record.referral_code} / DB=FAILED`);
    }
  }

  function signupCountForCode(code: string) {
    return readMemberSignups().filter((record) => String(record.values?.referral_code || '') === code).length;
  }

  const partnerCodeRecords = records.filter((record) => record.code_scope === 'PARTNER');
  const driverCodeRecords = records.filter((record) => record.code_scope === 'DRIVER');

  function downloadLatest() {
    if (!records[0]) return;
    downloadText(
      `${records[0].referral_code}.json`,
      JSON.stringify(records[0], null, 2),
      'application/json;charset=utf-8',
    );
  }

  return (
    <Guard>
      <main className="portal-shell">
        <PortalLanguageTabs lang={lang} setLang={setLang} label={t.language} />
        <Header t={t} />
        {!sessionReady ? (
          <section className="portal-card">
            <p className="eyebrow">LOADING</p>
            <h1>세션 확인 중</h1>
            <p className="muted">관리자 권한을 확인한 뒤 코드 관리 화면을 표시합니다.</p>
          </section>
        ) : !isAdminRole(sessionContext.role) ? (
          <section className="portal-card">
            <p className="eyebrow">ADMIN ONLY</p>
            <h1>관리자 전용 코드 관리</h1>
            <p className="muted">레퍼럴 코드와 파트너 코드 조회 및 발급은 관리자만 사용할 수 있습니다.</p>
            <Link href="/partner-dashboard" className="primary-link">
              파트너 대시보드로 이동
            </Link>
          </section>
        ) : null}
        {sessionReady && isAdminRole(sessionContext.role) ? (
          <>
        <section className="portal-card">
          <p className="eyebrow">PILOT REFERRAL ATTRIBUTION</p>
          <h1>{t.referral_title}</h1>
          <p className="muted">{t.referral_desc}</p>
          <p className="muted">{t.dashboard_referral_approval_note}</p>
        </section>
        <section className="portal-card referral-join-guide">
          <p className="eyebrow">{t.referral_join_eyebrow}</p>
          <h1>{t.referral_join_title}</h1>
          <div className="document-section-card">
            <h2>{t.referral_join_why_title}</h2>
            <p className="muted">{t.referral_join_why_desc}</p>
          </div>
          <div className="file-list" style={{ marginTop: 14 }}>
            <h2>{t.referral_join_benefits_title}</h2>
            {t.referral_join_benefits.map(([title, desc]) => (
              <article key={title} className="file-row">
                <div>
                  <strong>{title}</strong>
                  <p className="muted">{desc}</p>
                </div>
              </article>
            ))}
          </div>
          <p className="form-error" style={{ marginTop: 14 }}>
            {t.referral_join_disclaimer}
          </p>
          <div className="form-layout" style={{ marginTop: 14 }}>
            <article className="preview-panel">
              <h2>{t.referral_join_invite_title}</h2>
              <p className="muted">{t.referral_join_invite_desc}</p>
            </article>
            <article className="preview-panel">
              <h2>{t.referral_join_steps_title}</h2>
              <ol>
                {t.referral_join_steps.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </article>
          </div>
          <div className="preview-panel" style={{ marginTop: 14 }}>
            <h2>{t.referral_join_goal_title}</h2>
            <p className="muted">{t.referral_join_goal_desc}</p>
          </div>
        </section>
        <GovernanceBanner />
        <section className="form-layout">
          <form className="portal-form" onSubmit={(event) => event.preventDefault()}>
            <label>
              {t.referral_code_scope_label}
              <select value={codeScope} onChange={(event) => setCodeScope(event.target.value as 'PARTNER' | 'DRIVER')}>
                {partnerCodeIssueAllowed ? <option value="PARTNER">{t.referral_scope_partner}</option> : null}
                <option value="DRIVER">{t.referral_scope_driver}</option>
              </select>
            </label>
            {!partnerCodeIssueAllowed ? (
              <p className="form-error">파트너 코드는 관리자 권한에서만 발행할 수 있습니다.</p>
            ) : null}
            <p className="muted">
              {codeScope === 'DRIVER' ? t.referral_driver_policy_note : t.referral_partner_policy_note}
            </p>
            <label>
              {t.referral_hub_label}
              <input value={hubName} onChange={(event) => setHubName(event.target.value)} />
            </label>
            <label>
              {t.referral_partner_label}
              <input value={partnerName} onChange={(event) => setPartnerName(event.target.value)} />
            </label>
            <label>
              {t.referral_email_label}
              <input type="email" value={partnerEmail} onChange={(event) => setPartnerEmail(event.target.value)} />
            </label>
            <label>
              {t.referral_type_label}
              <select value={partnerType} onChange={(event) => setPartnerType(event.target.value)}>
                <option value="taxi_union">{t.partner_type_taxi_union}</option>
                <option value="taxi_company">{t.partner_type_taxi_company}</option>
                <option value="factory">{t.partner_type_factory}</option>
                <option value="charging_operator">{t.partner_type_charging_operator}</option>
                <option value="consultant">{t.partner_type_consultant}</option>
                <option value="regional_partner">{t.partner_type_regional_partner}</option>
              </select>
            </label>
            <label>
              {t.referral_region_label}
              <input value={region} onChange={(event) => setRegion(event.target.value)} placeholder={t.referral_region_placeholder} />
            </label>
            {codeScope === 'DRIVER' && (
              <label>
                {t.referral_driver_id_label}
                <input value={parentDriverId} onChange={(event) => setParentDriverId(event.target.value)} placeholder="D001" />
              </label>
            )}
            <div className="action-row">
              <button type="button" onClick={issueReferralCode}>
                {t.referral_button}
              </button>
              <button type="button" onClick={downloadLatest} disabled={records.length === 0}>
                {t.referral_download_latest}
              </button>
            </div>
            {message && <p className="form-success">{message}</p>}
          </form>
          <aside className="preview-panel">
            <h2>{t.referral_preview_title}</h2>
            <p className="muted">{t.referral_preview_desc}</p>
            <div className="saved-list">
              <h3>파트너 코드 관리</h3>
              {partnerCodeRecords.length === 0 ? (
                <p>{t.referral_empty}</p>
              ) : (
                partnerCodeRecords.map((record) => (
                  <p key={record.id}>
                    <strong>파트너명: {record.hub_name || record.partner_name || '-'}</strong>
                    <br />
                    파트너 코드: <code>{record.referral_code}</code>
                    <br />
                    발급일: {record.created_at}
                    <br />
                    상태: {referralStatusLabel(record.status, t)}
                    <br />
                    연결 가입자 수: {signupCountForCode(record.referral_code)}명
                    <br />
                    DB: {record.db_delivery_status || 'LOCAL_ONLY'}
                    {record.db_error_message ? ` / ${record.db_error_message}` : ''}
                  </p>
                ))
              )}
            </div>
            <div className="saved-list">
              <h3>개인 레퍼럴 코드 관리</h3>
              {driverCodeRecords.length === 0 ? (
                <p>{t.referral_empty}</p>
              ) : (
                driverCodeRecords.map((record) => (
                  <p key={record.id}>
                    <strong>회원명: {record.partner_name || '-'}</strong>
                    <br />
                    휴대폰: 내부 가입 데이터 기준 조회
                    <br />
                    개인 레퍼럴 코드: <code>{record.referral_code}</code>
                    <br />
                    발급일: {record.created_at}
                    <br />
                    상태: {referralStatusLabel(record.status, t)}
                    <br />
                    추천 가입자 수: {signupCountForCode(record.referral_code)}명
                    <br />
                    DB: {record.db_delivery_status || 'LOCAL_ONLY'}
                    {record.db_error_message ? ` / ${record.db_error_message}` : ''}
                  </p>
                ))
              )}
            </div>
          </aside>
        </section>
          </>
        ) : null}
      </main>
    </Guard>
  );
}

export function FileDeliveryPage() {
  const [lang, setLang] = useState<AdminLang>('ko');
  const [recipientName, setRecipientName] = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<string[]>(salesKitFiles.map((file) => file.filename));
  const [records, setRecords] = useState<DeliveryRecord[]>([]);
  const [codeRecords, setCodeRecords] = useState<ReferralCodeRecord[]>([]);
  const [message, setMessage] = useState('');
  const [sessionContext, setSessionContext] = useState({ role: '', partnerCode: '', partnerName: '' });
  const [sessionReady, setSessionReady] = useState(false);
  const t = adminI18n[lang];

  useEffect(() => {
    const savedLang = getStoredPortalLang();
    if (savedLang) {
      setLang(savedLang);
    }
    setSessionContext(getSessionContext());
    setSessionReady(true);
    setRecords(readDeliveries());
    setCodeRecords(readReferralCodes());
  }, []);

  useEffect(() => {
    window.localStorage.setItem('zenov_admin_dashboard_lang', lang);
    window.localStorage.setItem('zenov_partner_login_lang', lang);
  }, [lang]);

  function toggleFile(filename: string, checked: boolean) {
    setSelectedFiles((current) => (checked ? [...current, filename] : current.filter((item) => item !== filename)));
  }

  function createManifest() {
    const record: DeliveryRecord = {
      id: `zenov_delivery_${Date.now()}`,
      recipient_name: recipientName,
      recipient_email: recipientEmail,
      organization_name: organizationName,
      selected_files: selectedFiles,
      created_at: new Date().toISOString(),
      metadata: {
        document_type: 'PILOT_FILE_DELIVERY_MANIFEST',
        evidence_file: false,
        production_ready_trigger: false,
        commercial_ready_trigger: false,
      },
    };
    const next = [record, ...records];
    writeDeliveries(next);
    setRecords(next);
    downloadText(`ZENOV-FILE-DELIVERY-${Date.now()}.json`, JSON.stringify(record, null, 2), 'application/json;charset=utf-8');
    setMessage(t.delivery_created_message);
  }

  return (
    <Guard>
      <main className="portal-shell">
        <PortalLanguageTabs lang={lang} setLang={setLang} label={t.language} />
        <Header t={t} />
        {!sessionReady ? (
          <section className="portal-card">
            <p className="eyebrow">LOADING</p>
            <h1>세션 확인 중</h1>
            <p className="muted">관리자 권한을 확인한 뒤 파일 폴더를 표시합니다.</p>
          </section>
        ) : !isAdminRole(sessionContext.role) ? (
          <section className="portal-card">
            <p className="eyebrow">ADMIN ONLY</p>
            <h1>관리자 전용 파일 폴더</h1>
            <p className="muted">파일 폴더와 전달 매니페스트는 관리자 비밀번호 세션에서만 열 수 있습니다.</p>
            <Link href="/partner-login" className="primary-link">
              관리자 로그인
            </Link>
          </section>
        ) : null}
        {sessionReady && isAdminRole(sessionContext.role) ? (
          <>
        <section className="portal-card">
          <p className="eyebrow">PILOT FILE DELIVERY</p>
          <h1>{t.menu_file_delivery}</h1>
          <p className="muted">{t.delivery_desc}</p>
        </section>
        <section className="portal-card">
          <p className="eyebrow">ADMIN CODE FILE LEDGER</p>
          <h2>파일 폴더 연동 코드 원장</h2>
          <p className="muted">발급된 레퍼럴 코드와 파트너 코드 파일 내용을 파일 폴더에서도 확인합니다. 이 정보는 관리자 비밀번호 세션에서만 표시됩니다.</p>
          <div className="metric-grid">
            <article>
              <span>파트너 코드</span>
              <strong>{codeRecords.filter((record) => record.code_scope === 'PARTNER').length}</strong>
            </article>
            <article>
              <span>개인 레퍼럴 코드</span>
              <strong>{codeRecords.filter((record) => record.code_scope === 'DRIVER').length}</strong>
            </article>
            <article>
              <span>전체 코드 원장</span>
              <strong>{codeRecords.length}</strong>
            </article>
          </div>
          <div className="saved-list">
            {codeRecords.length === 0 ? (
              <p>발급된 코드 파일이 없습니다.</p>
            ) : (
              codeRecords.map((record) => (
                <p key={record.id}>
                  <strong>{record.code_scope === 'PARTNER' ? '파트너 코드' : '개인 레퍼럴 코드'}</strong>
                  <br />
                  코드: <code>{record.referral_code}</code>
                  <br />
                  소유자: {record.hub_name || record.partner_name || '-'}
                  <br />
                  상태: {referralStatusLabel(record.status, t)}
                </p>
              ))
            )}
          </div>
        </section>
        <GovernanceBanner />
        <section className="form-layout">
          <form className="portal-form" onSubmit={(event) => event.preventDefault()}>
            <label>
              {t.delivery_org_label}
              <input value={organizationName} onChange={(event) => setOrganizationName(event.target.value)} />
            </label>
            <label>
              {t.delivery_recipient_label}
              <input value={recipientName} onChange={(event) => setRecipientName(event.target.value)} />
            </label>
            <label>
              {t.delivery_email_label}
              <input type="email" value={recipientEmail} onChange={(event) => setRecipientEmail(event.target.value)} />
            </label>
            <label>
              {t.delivery_files_label}
              <div className="file-list">
                {salesKitFiles.map((file) => (
                  <div key={file.filename} className="file-row">
                    <label className="check-item">
                      <input
                        type="checkbox"
                        checked={selectedFiles.includes(file.filename)}
                        onChange={(event) => toggleFile(file.filename, event.target.checked)}
                      />
                      {salesKitFileLabels[lang][file.labelKey]}
                    </label>
                    <a href={file.href} download>
                      {t.delivery_download}
                    </a>
                  </div>
                ))}
              </div>
            </label>
            <div className="action-row">
              <button type="button" onClick={createManifest}>
                {t.delivery_create_manifest}
              </button>
            </div>
            {message && <p className="form-success">{message}</p>}
          </form>
          <aside className="preview-panel">
            <h2>{t.delivery_preview_title}</h2>
            <p className="muted">{t.delivery_preview_desc}</p>
            <div className="print-area">
              <p>{t.delivery_preview_recipient}: {recipientName || '-'}</p>
              <p>{t.delivery_preview_email}: {recipientEmail || '-'}</p>
              <p>{t.delivery_preview_organization}: {organizationName || '-'}</p>
              <p>{t.delivery_preview_selected_files}: {selectedFiles.length}</p>
              <p>Evidence File: false</p>
            </div>
            <div className="saved-list">
              <h3>{t.delivery_latest_manifest}</h3>
              {records.length === 0 ? <p>{t.delivery_empty_manifest}</p> : <p>{records[0].id}</p>}
            </div>
          </aside>
        </section>
          </>
        ) : null}
      </main>
    </Guard>
  );
}

export function FormPage({ formKey }: { formKey: keyof typeof forms }) {
  const baseConfig = forms[formKey];
  const [lang, setLang] = useState<AdminLang>('ko');
  const [values, setValues] = useState<Record<string, string | string[]>>(() => emptyValues(baseConfig.fields));
  const [status, setStatus] = useState<FormStatus>('draft');
  const [records, setRecords] = useState<SavedRecord[]>([]);
  const [message, setMessage] = useState('');
  const t = adminI18n[lang];
  const config = useMemo(() => localizeFormConfig(formKey, baseConfig, lang), [baseConfig, formKey, lang]);

  useEffect(() => {
    const savedLang = getStoredPortalLang();
    if (savedLang) {
      setLang(savedLang);
    }
    setRecords(readRecords(baseConfig.storageKey));
  }, [baseConfig.storageKey]);

  useEffect(() => {
    window.localStorage.setItem('zenov_admin_dashboard_lang', lang);
    window.localStorage.setItem('zenov_partner_login_lang', lang);
  }, [lang]);

  const latest = useMemo(() => records[0], [records]);

  function updateValue(name: string, value: string | string[]) {
    setValues((current) => ({ ...current, [name]: value }));
  }

  function saveRecord() {
    const now = new Date().toISOString();
    const record: SavedRecord = {
      id: `${config.storageKey}-${Date.now()}`,
      status,
      created_at: now,
      updated_at: now,
      metadata: {
        document_type: 'PILOT_ACQUISITION_FORM',
        evidence_file: false,
        production_ready_trigger: false,
        commercial_ready_trigger: false,
      },
      values,
    };
    const next = [record, ...records];
    writeRecords(config.storageKey, next);
    if (formKey === 'taxiSurvey') {
      syncTaxiCarbonDiagnosis(record);
    }
    setRecords(next);
    setMessage(
      formKey === 'taxiSurvey'
        ? t.form_taxi_save_success
        : t.form_save_success,
    );
  }

  function printPdf(kind: string) {
    setMessage(`${kind} ${t.form_print_suffix}`);
    window.setTimeout(() => window.print(), 80);
  }

  function downloadCsv() {
    downloadText(`${config.storageKey}.csv`, makeCsv(records, config.fields), 'text/csv;charset=utf-8');
  }

  return (
    <Guard>
      <main className="portal-shell">
        <PortalLanguageTabs lang={lang} setLang={setLang} label={t.language} />
        <Header t={t} />
        <section className="portal-card">
          <p className="eyebrow">{config.tableName}</p>
          <h1>{config.title}</h1>
          <p className="muted">{config.subtitle}</p>
        </section>
        <GovernanceBanner />
        {formKey === 'dataChecklist' && (
          <section className="portal-card">
            <h2>{t.data_checklist_title}</h2>
            <p className="muted">{t.data_checklist_desc}</p>
            <div className="download-grid">
              {salesKitFiles.slice(0, 7).map((file) => (
                <Link key={file.filename} href={`/files/${file.slug}`} className="download-card">
                  <span>{salesKitFileLabels[lang][file.labelKey]}</span>
                  <strong>{t.open_apply}</strong>
                  <small>{file.filename}</small>
                </Link>
              ))}
            </div>
          </section>
        )}
        <section className="form-layout">
          <form className="portal-form" onSubmit={(event) => event.preventDefault()}>
            <label>
              {t.form_status_label}
              <select value={status} onChange={(event) => setStatus(event.target.value as FormStatus)}>
                {allowedStatuses.map((item) => (
                  <option key={item} value={item}>
                    {getStatusLabel(item, t)}
                  </option>
                ))}
              </select>
            </label>
            {config.fields.map((field) => (
              <label key={field.name}>
                {field.label}
                <FieldInput
                  field={field}
                  value={values[field.name]}
                  onChange={(value) => updateValue(field.name, value)}
                  selectPlaceholder={t.form_select}
                />
              </label>
            ))}
            <div className="action-row">
              <button type="button" onClick={saveRecord}>
                {t.form_save}
              </button>
              <button type="button" onClick={() => printPdf(t.form_internal_pdf)}>
                {t.form_internal_pdf}
              </button>
              <button type="button" onClick={() => printPdf(t.form_customer_pdf)}>
                {t.form_customer_pdf}
              </button>
              <button type="button" onClick={downloadCsv} disabled={records.length === 0}>
                {t.form_excel}
              </button>
              {formKey === 'taxiSurvey' && (
                <>
                  <Link className="secondary-button" href="/taxi-carbon-os-diagnosis">
                    {t.taxi_diagnosis_file_link}
                  </Link>
                  <Link className="secondary-button" href="/taxi-carbon-os-dashboard">
                    {t.taxi_dashboard_link}
                  </Link>
                </>
              )}
            </div>
            {message && <p className="form-success">{message}</p>}
          </form>
          <aside className="preview-panel">
            <h2>{t.form_submitted_preview}</h2>
            <p className="muted">{t.form_not_evidence}</p>
            <div className="print-area">
              <h3>{config.title}</h3>
              <p>{t.preview_table}: {config.tableName}</p>
              <p>{t.preview_status}: {getStatusLabel(status, t)}</p>
              <p>{t.preview_document_type}: PILOT_ACQUISITION_FORM</p>
              <p>{t.preview_evidence_file}: false</p>
              <hr />
              {config.fields.map((field) => {
                const value = values[field.name];
                return (
                  <p key={field.name}>
                    <strong>{field.label}: </strong>
                    {Array.isArray(value) ? value.join(', ') : value || '-'}
                  </p>
                );
              })}
            </div>
            <div className="saved-list">
              <h3>{t.form_latest_saved}</h3>
              {latest ? (
                <p>
                  {latest.id}
                  <br />
                  {t.preview_status}: {getStatusLabel(latest.status, t)}
                  <br />
                  {latest.updated_at}
                </p>
              ) : (
                <p>{t.form_no_saved}</p>
              )}
              <span>
                {records.length} {t.records_suffix}
              </span>
            </div>
          </aside>
        </section>
      </main>
    </Guard>
  );
}
