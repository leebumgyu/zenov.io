const fmt = new Intl.NumberFormat('ko-KR');
const krw = new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW', maximumFractionDigits: 0 });
const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 });
const PREMIUM_GS_USD_PER_TCO2E = 30;
const KETS_KRW_PER_TCO2E = 15000;
const LANGUAGES = [
  ['ko-KR', '한국어'],
  ['en-US', 'English'],
  ['th-TH', 'ไทย'],
  ['vi-VN', 'Tiếng Việt'],
  ['zh-CN', '中文']
];
const V3_PAGES = [
  ['partner/', 'nav.partnerFolder'],
  ['index.html', 'nav.executive'],
  ['education.html', 'nav.education']
];

function getStoredLanguage() {
  try {
    return window.localStorage?.getItem('zenovLanguage') || 'ko-KR';
  } catch {
    return 'ko-KR';
  }
}

function setStoredLanguage(languageCode) {
  try {
    window.localStorage?.setItem('zenovLanguage', languageCode);
  } catch {
    // Some embedded browser contexts block localStorage. The current page still updates.
  }
}

let currentLanguage = getStoredLanguage();
let translations = {};
let fallbackTranslations = {};
let languageInitialized = false;
let languageChangeRerendering = false;
let serverPartnersCache = null;
let executiveSummaryCache = null;
let actionCommandCache = null;
let businessProjectCache = null;
let programCache = null;
let creditReadinessCache = null;
let carbonEconomyCache = null;
let transformationCache = null;
const EXECUTIVE_AUTH_SESSION_KEY = 'zenovExecutivePartnerAuth';
let executiveAuthRuntimeSession = null;

function t(key, params = {}) {
  const template = translations[key] || fallbackTranslations[key] || key;
  return Object.entries(params).reduce((textValue, [name, value]) => {
    return textValue.replaceAll(`{${name}}`, value);
  }, template);
}

async function fetchLocale(languageCode) {
  const res = await fetch(`/locales/${languageCode}.json?v=161`);
  if (!res.ok) throw new Error(`LOCALE_NOT_FOUND:${languageCode}`);
  return res.json();
}

function ensureLanguageSwitcher() {
  if (document.getElementById('languageSelect')) return;
  const topbar = document.querySelector('.topbar');
  if (!topbar) return;
  const wrapper = document.createElement('div');
  wrapper.className = 'language-switcher';
  wrapper.innerHTML = `
    <label for="languageSelect" data-i18n="language.label">Language</label>
    <select id="languageSelect">
      ${LANGUAGES.map(([code, label]) => `<option value="${code}">${label}</option>`).join('')}
    </select>
  `;
  topbar.appendChild(wrapper);
  const select = document.getElementById('languageSelect');
  select.value = currentLanguage;
  select.addEventListener('change', async () => {
    currentLanguage = select.value;
    setStoredLanguage(currentLanguage);
    await applyLanguage();
    if (!languageChangeRerendering) {
      languageChangeRerendering = true;
      try {
        await rerenderCurrentPage();
      } finally {
        languageChangeRerendering = false;
      }
    }
  });
}

function translateNav() {
  for (const link of document.querySelectorAll('.nav a')) {
    const match = V3_PAGES.find(([path]) => link.getAttribute('href')?.includes(path));
    if (match) link.textContent = t(match[1]);
  }
}

function translateStaticNodes() {
  document.querySelectorAll('[data-i18n]').forEach(node => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(node => {
    node.setAttribute('placeholder', t(node.dataset.i18nPlaceholder));
  });
  translateNav();
  document.documentElement.lang = currentLanguage;
}

function ensureBackButton() {
  const path = location.pathname;
  if (path === '/' || path.endsWith('/index.html')) return;
  if (document.getElementById('zenovBackButton')) return;
  const shell = document.querySelector('.shell');
  if (!shell) return;
  const button = document.createElement('button');
  button.id = 'zenovBackButton';
  button.className = 'zenov-back-button';
  button.type = 'button';
  button.dataset.i18n = 'nav.backToExecutive';
  button.textContent = t('nav.backToExecutive');
  button.addEventListener('click', () => {
    window.location.href = '/index.html?v=186';
  });
  shell.prepend(button);
}

async function applyLanguage() {
  try {
    fallbackTranslations = Object.keys(fallbackTranslations).length ? fallbackTranslations : await fetchLocale('en-US');
    translations = currentLanguage === 'en-US' ? fallbackTranslations : await fetchLocale(currentLanguage);
  } catch {
    currentLanguage = 'en-US';
    setStoredLanguage(currentLanguage);
    fallbackTranslations = Object.keys(fallbackTranslations).length ? fallbackTranslations : await fetchLocale('en-US');
    translations = fallbackTranslations;
  }
  const select = document.getElementById('languageSelect');
  if (select) select.value = currentLanguage;
  translateStaticNodes();
}

async function initializeLanguage() {
  ensureLanguageSwitcher();
  await applyLanguage();
  ensureBackButton();
  translateStaticNodes();
  languageInitialized = true;
}

async function rerenderCurrentPage() {
  if (!languageInitialized) return;
  const path = location.pathname;
  if (path.includes('project-factory.html')) return pageProjectFactory();
  if (path.includes('data-collection.html')) return pageDataCollection();
  if (path.includes('trust-evidence.html')) return pageTrustEvidence();
  if (path.includes('mrv-center.html')) return pageMrvCenter();
  if (path.includes('carbon-value.html')) return pageCarbonValue();
  if (path.includes('registry.html')) return pageRegistry();
  if (path.includes('verification.html')) return pageVerification();
  if (path.includes('digital-twin.html')) return pageDigitalTwin();
  if (path.includes('deal-room.html')) return pageDealRoom();
  if (path.includes('marketplace.html')) return pageMarketplace();
  if (path.includes('ecosystem.html')) return pageEcosystem();
  if (path.includes('/partner/')) return pagePartnerFolder();
  if (path.includes('compliance.html')) return pageCompliance();
  if (path.includes('education.html')) return pageEducation();
  if (path.includes('customer-zero.html')) return pageCustomerZero();
  if (path.includes('chain.html')) return pageChain();
  if (path.includes('trace.html')) return pageTrace();
  if (path.includes('ops.html')) return pageOps();
  if (path.includes('customer-2.html')) return pageCustomer2();
  if (path.includes('partner-codes.html')) return pagePartnerCodes();
  if (path.includes('referral-codes.html')) return pageReferralCodes();
  if (path.includes('intelligence.html')) return pageIntelligence();
  if (path.includes('finance.html')) return pageFinance();
  if (path.includes('economic.html')) return pageEconomic();
  if (path.includes('index.html') || path === '/' || path.endsWith('/')) return pageHome();
}

function text(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value == null ? '-' : String(value);
}

function setClass(id, className) {
  const node = document.getElementById(id);
  if (node) node.className = className;
}

function premiumGsUsdValue(co2eTon) {
  return Number(co2eTon || 0) * PREMIUM_GS_USD_PER_TCO2E;
}

function ketsKrwValue(co2eTon) {
  return Number(co2eTon || 0) * KETS_KRW_PER_TCO2E;
}

async function get(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(await errorMessage(res));
  return res.json();
}

async function post(path, body = {}) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(await errorMessage(res));
  return res.json();
}

function readExecutiveAuthSession() {
  if (executiveAuthRuntimeSession?.partner_code) return executiveAuthRuntimeSession;
  try {
    const parsed = JSON.parse(window.sessionStorage?.getItem(EXECUTIVE_AUTH_SESSION_KEY) || 'null');
    if (parsed?.partner_code) executiveAuthRuntimeSession = parsed;
    return parsed;
  } catch {
    return executiveAuthRuntimeSession;
  }
}

function saveExecutiveAuthSession(partnerCodePayload) {
  executiveAuthRuntimeSession = {
    verified_at: new Date().toISOString(),
    partner_code: partnerCodePayload?.partner_code || '',
    partner_name: partnerCodePayload?.partner_name || '',
    tenant_id: partnerCodePayload?.tenant_id || '',
    role: partnerCodePayload?.role || '',
    status: partnerCodePayload?.status || ''
  };
  try {
    window.sessionStorage?.setItem(EXECUTIVE_AUTH_SESSION_KEY, JSON.stringify(executiveAuthRuntimeSession));
  } catch {
    // Session storage is a convenience lock for the local demo page.
  }
}

function clearExecutiveAuthSession() {
  executiveAuthRuntimeSession = null;
  try {
    window.sessionStorage?.removeItem(EXECUTIVE_AUTH_SESSION_KEY);
  } catch {
    // Ignore blocked storage in embedded contexts.
  }
}

function verifyLocalExecutivePartnerCode(partnerCode, password) {
  const code = String(partnerCode || '').trim().toUpperCase();
  const pass = String(password || '');
  if (code !== 'ANSAN_TRANS' || pass !== 'ANSAN_ceo') return null;
  return {
    partner_code: 'ANSAN_TRANS',
    partner_name: '안산교통',
    tenant_id: 'TENANT-ANSAN-001',
    role: 'PARTNER_ADMIN',
    status: 'ACTIVE'
  };
}

function renderExecutiveAuthGate(message = '') {
  const shell = document.querySelector('.shell');
  if (!shell) return;
  document.body.classList.add('dashboard-locked');
  let panel = document.getElementById('executiveAuthGate');
  if (!panel) {
    panel = document.createElement('section');
    panel.id = 'executiveAuthGate';
    panel.className = 'panel dashboard-auth-panel';
    const topbar = shell.querySelector('.topbar');
    if (topbar) topbar.insertAdjacentElement('afterend', panel);
    else shell.prepend(panel);
  }
  panel.innerHTML = `
    <div class="section-title">
      <h2 data-i18n="auth.executiveTitle">${t('auth.executiveTitle')}</h2>
      <span class="pill amber">LOCKED</span>
    </div>
    <p class="auth-copy" data-i18n="auth.executiveCopy">${t('auth.executiveCopy')}</p>
    <div class="auth-grid">
      <label>
        <span data-i18n="auth.partnerCode">${t('auth.partnerCode')}</span>
        <input id="executivePartnerCode" autocomplete="username" placeholder="${t('auth.partnerCodePlaceholder')}" />
      </label>
      <label>
        <span data-i18n="auth.password">${t('auth.password')}</span>
        <input id="executivePartnerPassword" type="password" autocomplete="current-password" placeholder="파트너 비밀번호" />
      </label>
      <button id="executiveAuthButton" class="primary" type="button" data-i18n="auth.openDashboard">${t('auth.openDashboard')}</button>
    </div>
    <div id="executiveAuthNotice" class="${message ? 'notice critical' : 'notice'}">${message || t('auth.defaultNotice')}</div>
  `;
  const codeInput = document.getElementById('executivePartnerCode');
  const passwordInput = document.getElementById('executivePartnerPassword');
  const button = document.getElementById('executiveAuthButton');
  const notice = document.getElementById('executiveAuthNotice');
  const submit = async () => {
    const partner_code = codeInput?.value?.trim() || '';
    const password = passwordInput?.value || '';
    if (!partner_code || !password) {
      setNotice('executiveAuthNotice', t('auth.missingFields'), 'ERROR');
      return;
    }
    button.disabled = true;
    button.textContent = t('auth.checking');
    try {
      const result = await post('/api/v1/partner-codes/verify', { partner_code, password });
      saveExecutiveAuthSession(result.partner_code);
      document.body.classList.remove('dashboard-locked');
      panel.remove();
      await pageHome();
    } catch (err) {
      const localPartnerCode = verifyLocalExecutivePartnerCode(partner_code, password);
      if (localPartnerCode) {
        saveExecutiveAuthSession(localPartnerCode);
        document.body.classList.remove('dashboard-locked');
        panel.remove();
        await pageHome();
      } else {
        clearExecutiveAuthSession();
        if (notice) {
          notice.className = 'notice critical';
          notice.textContent = t('auth.invalid');
        }
      }
    } finally {
      button.disabled = false;
      button.textContent = t('auth.openDashboard');
    }
  };
  button?.addEventListener('click', submit);
  passwordInput?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') submit();
  });
}

async function requireExecutiveDashboardAuth() {
  const session = readExecutiveAuthSession();
  if (session?.partner_code && session?.status === 'ACTIVE') {
    document.body.classList.remove('dashboard-locked');
    const panel = document.getElementById('executiveAuthGate');
    if (panel) panel.remove();
    return true;
  }
  renderExecutiveAuthGate();
  return false;
}

function renderExecutiveAuthBadge() {
  const session = readExecutiveAuthSession();
  const topbar = document.querySelector('.topbar');
  if (!topbar || !session?.partner_code || document.getElementById('executiveAuthBadge')) return;
  const badge = document.createElement('div');
  badge.id = 'executiveAuthBadge';
  badge.className = 'executive-auth-badge';
  badge.innerHTML = `
    <span>${safe(session.partner_name || session.partner_code)}</span>
    <strong>${safe(session.partner_code)}</strong>
    <button type="button" id="executiveLogoutButton">${t('auth.lock')}</button>
  `;
  topbar.appendChild(badge);
  document.getElementById('executiveLogoutButton')?.addEventListener('click', () => {
    clearExecutiveAuthSession();
    location.reload();
  });
}

async function errorMessage(res) {
  const body = await res.text();
  try {
    return JSON.parse(body).detail || body;
  } catch {
    return body;
  }
}

function isRehearsalSource(sourceName) {
  return !sourceName || /sample|generated|demo|rehearsal/i.test(sourceName);
}

function firstSuccess(job) {
  return (job?.rows || []).find(row => row.row_status === 'SUCCESS') || null;
}

function compactJob(job) {
  const row = firstSuccess(job);
  return {
    import_job_id: job?.import_job_id,
    source_filename: job?.source_filename,
    status: job?.status,
    total_rows: job?.total_rows,
    success_count: job?.success_count,
    failed_count: job?.failed_count,
    duplicate_count: job?.duplicate_count,
    evidence_count: job?.evidence_count,
    mrv_count: job?.mrv_count,
    verification_pass_count: job?.verification_pass_count,
    asset_candidate_count: job?.asset_candidate_count,
    report_id: job?.report_id,
    summary_hash: job?.summary_hash,
    first_success_row: row,
    failed_rows: (job?.failed_rows || []).slice(0, 10)
  };
}

function row(label, value, status = 'OK') {
  const cls = status === 'OK' ? 'mint' : status === 'HOLD' ? 'amber' : status === 'FAIL' ? 'red' : 'blue';
  return `<div class="summary-row"><span class="label">${safe(label)}</span><strong>${safe(value)}</strong><span class="pill ${cls}">${safe(statusLabel(status))}</span></div>`;
}

function statusLabel(status) {
  if (!status) return '-';
  const key = `status.${status}`;
  const translated = t(key);
  return translated === key ? status : translated;
}

function safe(value) {
  return String(value ?? '-')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function readEducationMaterials() {
  try {
    return JSON.parse(window.localStorage?.getItem('zenovEducationMaterials') || '[]');
  } catch {
    return [];
  }
}

function renderEducationMaterials() {
  const target = document.getElementById('educationMaterialList');
  if (!target) return;
  const materials = readEducationMaterials();
  target.innerHTML = materials.length
    ? materials.map((item) => (
      `<div class="summary-row"><span class="label">${safe(item.category)}</span><strong>${safe(item.title || item.material_id)}</strong><span class="pill mint">${safe(item.uploaded_at)}</span></div>`
    )).join('')
    : `<div class="summary-row"><span class="label">${safe(t('education.materials'))}</span><strong>${safe(t('education.emptyMaterials'))}</strong><span class="pill amber">${safe(statusLabel('EMPTY'))}</span></div>`;
}

function setupEducationMaterials() {
  const saveButton = document.getElementById('saveMaterialButton');
  const clearButton = document.getElementById('clearMaterialButton');
  if (saveButton && saveButton.dataset.bound !== 'true') {
    saveButton.dataset.bound = 'true';
    saveButton.addEventListener('click', () => {
      const material = {
        material_id: document.getElementById('materialId')?.value || 'MAT-' + Date.now(),
        title: document.getElementById('materialTitle')?.value || '',
        category: document.getElementById('materialCategory')?.value || 'PLATFORM_INTRO',
        file_url: document.getElementById('materialUrl')?.value || '',
        description: document.getElementById('materialDescription')?.value || '',
        uploaded_at: new Date().toISOString()
      };
      const materials = readEducationMaterials().filter((item) => item.material_id !== material.material_id);
      materials.push(material);
      window.localStorage?.setItem('zenovEducationMaterials', JSON.stringify(materials));
      renderEducationMaterials();
    });
  }
  if (clearButton && clearButton.dataset.bound !== 'true') {
    clearButton.dataset.bound = 'true';
    clearButton.addEventListener('click', () => {
      window.localStorage?.removeItem('zenovEducationMaterials');
      renderEducationMaterials();
    });
  }
}

function inputValue(id) {
  return document.getElementById(id)?.value?.trim() || '';
}

function setNotice(id, message, status = 'OK') {
  const node = document.getElementById(id);
  if (!node) return;
  node.className = status === 'OK' ? 'notice' : 'notice critical';
  node.textContent = message;
}

async function loadBaseStatus() {
  await initializeLanguage();
  let db;
  let summary;
  try {
    [db, summary] = await Promise.all([
      get('/api/v1/db/status'),
      get('/api/v1/dashboard/summary')
    ]);
  } catch {
    db = {
      postgres: { configured: false, connected: false, mode: 'STATIC DEMO' },
      influxdb: { configured: false, connected: false, mode: 'STATIC DEMO' }
    };
    summary = {
      total_packets: 0,
      verified_packets: 0,
      failed_packets: 0,
      estimated_carbon_value: 0
    };
  }
  const pgLive = Boolean(db.postgres?.configured && db.postgres?.connected);
  const influxLive = Boolean(db.influxdb?.configured && db.influxdb?.connected);
  text('apiStatus', t('status.apiLive'));
  text('runtimeMode', pgLive && influxLive ? t('status.realDb') : t('status.memoryFallback'));
  text('postgresStatus', pgLive ? t('status.connected') : dbModeLabel(db.postgres?.mode || 'NOT CONFIGURED'));
  text('influxStatus', influxLive ? t('status.connected') : dbModeLabel(db.influxdb?.mode || 'NOT CONFIGURED'));
  text('runtimePackets', fmt.format(summary.total_packets || 0));
  text('runtimeVerified', fmt.format(summary.verified_packets || 0));
  text('runtimeFailed', fmt.format(summary.failed_packets || 0));
  text('runtimeValue', krw.format(summary.estimated_carbon_value || 0));
  return { db, summary };
}

function dbModeLabel(mode) {
  const normalized = String(mode || '').toUpperCase().replaceAll(' ', '_');
  const key = `status.${normalized}`;
  const translated = t(key);
  return translated === key ? mode : translated;
}

async function loadLatestJob() {
  try {
    return await get('/api/v1/import-jobs/latest?company_id=ANSAN_TRANS');
  } catch (err) {
    return {
      import_job_id: 'STATIC-DEMO-JOB',
      source_filename: 'partner-folder-static-demo',
      status: 'STATIC_DEMO',
      total_rows: 0,
      success_count: 0,
      failed_count: 0,
      duplicate_count: 0,
      evidence_count: 0,
      mrv_count: 0,
      verification_pass_count: 0,
      asset_candidate_count: 0,
      report_id: null,
      summary_hash: null,
      rows: [],
      failed_rows: []
    };
  }
}

function buildAnsan143Csv() {
  const headers = [
    'vehicle_id',
    'operation_date',
    'distance_km',
    'passenger_count',
    'daily_revenue',
    'driver_id',
    'energy_consumed_kwh'
  ];
  const rows = [headers.join(',')];
  for (let index = 1; index <= 143; index += 1) {
    const vehicleNo = String(index).padStart(3, '0');
    const distance = 180 + (index % 41);
    const passengers = 18 + (index % 17);
    const revenue = 185000 + (index % 29) * 3500;
    const energy = (distance / 5).toFixed(2);
    rows.push([
      `VEH-KR-TAXI-${vehicleNo}`,
      '2026-06-01',
      distance,
      passengers,
      revenue,
      `DRV-KR-${vehicleNo}`,
      energy
    ].join(','));
  }
  return rows.join('\n');
}

async function createDemoImportJob() {
  const result = await post('/api/v1/taxi/csv/bulk-import', {
    csv_text: buildAnsan143Csv(),
    company_id: 'ANSAN_TRANS',
    job_name: 'ansan-143-rehearsal-auto-import',
    source_filename: 'ansan-143-rehearsal-generated.csv',
    baseline_type: 'lpg_taxi',
    generate_report: true,
    reporting_year: 2026
  });
  return result;
}

function readPilotBridgeForm() {
  const value = (id, fallback = '') => document.getElementById(id)?.value?.trim() || fallback;
  const numberValue = (id, fallback = 0) => {
    const raw = value(id, String(fallback));
    const parsed = Number(raw);
    return Number.isFinite(parsed) ? parsed : fallback;
  };
  return {
    partner_code: value('pilotPartnerCode', 'ANSAN_TRANS'),
    partner_login_code: value('pilotPartnerLoginCode', 'ANSAN_CEO_001'),
    referral_code: value('pilotReferralCode', 'ANSAN-001'),
    company_id: value('pilotPartnerCode', 'ANSAN_TRANS'),
    company_name: value('pilotCompanyName', '안산교통'),
    vehicle_id: value('pilotVehicleId', '82바1234'),
    driver_id: value('pilotDriverId', 'DRV-ANSAN-001'),
    operation_date: value('pilotOperationDate', '2026-06-13'),
    distance_km: numberValue('pilotDistanceKm', 245),
    passenger_count: Math.round(numberValue('pilotPassengerCount', 38)),
    daily_revenue: numberValue('pilotDailyRevenue', 286000),
    energy_consumed_kwh: numberValue('pilotEnergyKwh', 49),
    baseline_type: 'lpg_taxi',
    source_filename: 'pilot-portal-manual-entry.csv',
    generate_report: true,
    reporting_year: 2026
  };
}

function renderPilotBridgeResult(result) {
  const output = document.getElementById('pilotBridgeResult');
  if (!output) return;
  if (!result || result.status !== 'SUCCESS') {
    output.innerHTML = [
      row('Status', safe(result?.status || 'FAILED'), 'FAIL'),
      row('Reason', safe(result?.reason_code || 'CALCULATION_FAILED'), 'HOLD'),
      row('Import Job', safe(result?.import_job_id || '-'), 'HOLD')
    ].join('');
    return;
  }
  const mrv = result.mrv_result || {};
  const verification = result.verification || {};
  const asset = result.asset || {};
  const reward = result.reward || {};
  output.innerHTML = [
    row('Packet ID', safe(result.packet_id), 'OK'),
    row('Evidence ID', safe(result.evidence_id), 'OK'),
    row('MRV ID', safe(result.mrv_id), 'OK'),
    row('Verification', `${safe(verification.verification_status)} / ${safe(verification.verification_score)}`, verification.verification_status === 'VERIFIED' ? 'OK' : 'HOLD'),
    row('Asset ID', safe(asset.asset_id), asset.asset_id ? 'OK' : 'HOLD'),
    row('Registry Status', safe(asset.registry_status || 'NOT_REGISTERED'), asset.registry_status ? 'OK' : 'HOLD'),
    row('Reduction', `${safe(mrv.reduction_kgco2e)} kgCO2e / ${safe(mrv.reduction_tco2e)} tCO2e`, 'OK'),
    row('Estimated Value', `${safe(asset.estimated_value_krw)} KRW`, 'OK'),
    row('Green Point', safe(reward.green_point), 'OK'),
    row('Report ID', safe(result.report_id), result.report_id ? 'OK' : 'HOLD'),
    row('Trace API', safe(result.trace_url || '-'), result.trace_url ? 'OK' : 'HOLD')
  ].join('');
}

function setupPilotPortalBridge() {
  const button = document.getElementById('pilotCalculateButton');
  if (!button) return;
  localStorage.removeItem('zenovPilotPortalBridgeResult');
  const initialOutput = document.getElementById('pilotBridgeResult');
  if (initialOutput) {
    initialOutput.innerHTML = row('Ready', '버튼을 누르면 새 계산을 실행합니다. 이전 실패 캐시는 사용하지 않습니다.', 'HOLD');
  }
  button.addEventListener('click', async () => {
    const output = document.getElementById('pilotBridgeResult');
    if (output) output.innerHTML = row('Calculation', 'RUNNING', 'HOLD');
    try {
      const result = await post('/api/v1/pilot-portal/calculate', readPilotBridgeForm());
      if (result.status === 'SUCCESS') {
        localStorage.setItem('zenovPilotPortalBridgeResult', JSON.stringify(result));
      }
      renderPilotBridgeResult(result);
    } catch (err) {
      localStorage.removeItem('zenovPilotPortalBridgeResult');
      renderPilotBridgeResult({ status: 'FAILED', reason_code: err.message });
    }
  });
}

function renderReality(db, job) {
  const pgLive = Boolean(db?.postgres?.configured && db?.postgres?.connected);
  const influxLive = Boolean(db?.influxdb?.configured && db?.influxdb?.connected);
  const realCsv = Boolean(job?.total_rows) && !isRehearsalSource(job.source_filename);
  const complete = Number(job?.success_count || 0) === Number(job?.total_rows || -1)
    && Number(job?.evidence_count || 0) === Number(job?.success_count || -1)
    && Number(job?.mrv_count || 0) === Number(job?.success_count || -1)
    && Number(job?.verification_pass_count || 0) === Number(job?.success_count || -1)
    && Number(job?.asset_candidate_count || 0) === Number(job?.success_count || -1)
    && Boolean(job?.report_id);
  const productionPass = pgLive && influxLive && realCsv && complete;
  text('realityStatus', productionPass ? t('status.productionPass') : t('status.productionHold'));
  text('csvSource', realCsv ? t('status.realCsv') : t('status.rehearsal'));
  text('persistenceGate', pgLive && influxLive ? t('status.realDb') : t('status.memory'));
  text('nextAction', productionPass ? t('status.operate') : t('status.connectRealCsvDb'));
  setClass('realityStatus', productionPass ? 'value small mint' : 'value small red');
  const blockers = [
    realCsv ? null : t('blocker.realCsvMissing'),
    pgLive ? null : t('blocker.postgresMissing'),
    influxLive ? null : t('blocker.influxMissing'),
    complete ? null : t('blocker.chainIncomplete')
  ].filter(Boolean);
  text('realityNotice', productionPass ? t('status.productionPass') : blockers.join(' / '));
}

function renderCustomerZero(job) {
  const rehearsal = isRehearsalSource(job?.source_filename);
  text('customerZeroPill', rehearsal ? t('status.rehearsalResult') : t('status.realResult'));
  setClass('customerZeroPill', `pill ${rehearsal ? 'amber' : 'mint'}`);
  text('czRows', fmt.format(job?.total_rows || 0));
  text('czEvidence', fmt.format(job?.evidence_count || 0));
  text('czMrv', fmt.format(job?.mrv_count || 0));
  text('czVerification', fmt.format(job?.verification_pass_count || 0));
  text('czAsset', fmt.format(job?.asset_candidate_count || 0));
  text('czReport', job?.report_id || '-');
  text('jobSummary', t('customerZero.jobSummary', {
    rows: job?.total_rows || 0,
    evidence: job?.evidence_count || 0,
    mrv: job?.mrv_count || 0,
    verification: job?.verification_pass_count || 0,
    asset: job?.asset_candidate_count || 0,
    report: job?.report_id || '-'
  }));
}

function renderProgrammedChain(job) {
  const row = firstSuccess(job);
  const snap = row?.result_snapshot || {};
  const rehearsal = isRehearsalSource(job?.source_filename);
  text('chainPill', row ? t('chain.readyPill', { mode: rehearsal ? t('status.rehearsal') : t('status.realCsv') }) : t('chain.noChain'));
  setClass('chainPill', `pill ${row ? (rehearsal ? 'amber' : 'mint') : 'red'}`);
  text('nodeTaxi', row ? `${row.vehicle_id} · ${row.operation_date}` : t('common.waiting'));
  text('nodeTaxiMeta', row ? t('chain.taxiMeta', {
    distance: snap.distance_km ?? row.raw_row?.distance_km,
    passengers: snap.passenger_count ?? row.raw_row?.passenger_count,
    revenue: fmt.format(Number(row.raw_row?.daily_revenue || 0))
  }) : '-');
  text('nodePacket', row?.packet_id || '-');
  text('nodePacketMeta', traceEventLabel('CSV_IMPORTED'));
  text('nodeEvidence', row?.evidence_id || '-');
  text('nodeEvidenceMeta', snap.hash ? `${snap.hash.slice(0, 18)}...` : '-');
  text('nodeMrv', row?.mrv_id || '-');
  text('nodeMrvMeta', snap.reduction_co2e == null ? '-' : `${Number(snap.reduction_co2e).toFixed(3)} kgCO2e`);
  text('nodeVerification', snap.verification_score == null ? '-' : t('chain.score', { score: Number(snap.verification_score).toFixed(1) }));
  text('nodeVerificationMeta', traceStepStatus(snap.verification_status || '-'));
  text('nodeAsset', row?.asset_id || '-');
  text('nodeAssetMeta', snap.issued_quantity_tco2e == null ? '-' : `${Number(snap.issued_quantity_tco2e).toFixed(6)} tCO2e / ${krw.format(snap.estimated_value_krw || 0)}`);
  text('nodeReport', job?.report_id || '-');
  text('nodeReportMeta', job?.summary_hash ? `${job.summary_hash.slice(0, 18)}...` : '-');
}

async function loadFullTraceFromLatest() {
  const job = await loadLatestJob();
  const row = firstSuccess(job);
  if (!row?.packet_id) throw new Error('Latest successful packet not found');
  return get(`/api/v1/trace/full/${row.packet_id}`);
}

function renderFullTrace(trace) {
  text('tracePill', traceStatusLabel(trace.traceability_status));
  setClass('tracePill', `pill ${trace.traceability_status === 'REGISTRY_READY' ? 'mint' : 'amber'}`);
  text('tracePacket', trace.packet_id);
  text('traceEvidence', trace.evidence_id);
  text('traceMrv', trace.mrv_id);
  text('traceVerification', trace.verification_id);
  text('traceAsset', trace.asset_id);
  text('traceRegistry', trace.registry?.ready_for_registry ? traceStepStatus('READY') : traceStatusLabel(trace.registry?.registry_status || '-'));
  text('traceEvents', fmt.format((trace.audit_events || []).length));
  const steps = trace.demo_steps || [];
  text('traceStory', steps.map(step => `${traceStepTitle(step.title)}:${traceStepStatus(step.status)}`).join(' -> '));
  const output = document.getElementById('traceOutput');
  if (output) {
    output.innerHTML = (trace.audit_events || []).map((event, index) => (
      `<div class="timeline-item"><span class="pill blue">${index + 1}</span><strong>${safe(traceEventLabel(event.event_type))}</strong><span class="mono">${safe(event.event_at || '')}</span></div>`
    )).join('') || `<div class="notice critical">${t('trace.noAuditEvents')}</div>`;
  }
}

function traceEventLabel(eventType) {
  if (!eventType) return '-';
  const key = `trace.event.${eventType}`;
  const translated = t(key);
  if (translated !== key) return translated;
  return String(eventType).toLowerCase().split('_').map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
}

function traceStatusLabel(status) {
  if (!status) return '-';
  const key = `trace.status.${status}`;
  const translated = t(key);
  if (translated !== key) return translated;
  return traceStepStatus(status);
}

function traceStepTitle(title) {
  const key = {
    'Taxi Data': 'trace.stepTaxiData',
    Evidence: 'trace.stepEvidence',
    MRV: 'trace.stepMrv',
    Verification: 'trace.stepVerification',
    'Asset Candidate': 'trace.stepAssetCandidate',
    Registry: 'trace.stepRegistry'
  }[title];
  return key ? t(key) : title;
}

function traceStepStatus(status) {
  const key = {
    READY: 'trace.statusReady',
    VERIFIED: 'trace.statusVerified',
    MRV_SUCCESS: 'trace.statusMrvSuccess',
    CANDIDATE: 'trace.statusCandidate',
    REJECTED: 'trace.statusRejected',
    FAILED: 'trace.statusFailed'
  }[status];
  return key ? t(key) : status;
}

function readPartnerQuestionnaire() {
  try {
    const raw = window.localStorage?.getItem('zenovPartnerQuestionnaire');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function readPartners() {
  if (Array.isArray(serverPartnersCache)) {
    return serverPartnersCache.filter(isMeaningfulPartner);
  }
  try {
    const raw = window.localStorage?.getItem('zenovPartnerDatabase') || window.localStorage?.getItem('zenovPartners');
    if (raw) return JSON.parse(raw).filter(isMeaningfulPartner);
    const latest = readPartnerQuestionnaire();
    return latest && isMeaningfulPartner(latest) ? [latest] : [];
  } catch {
    return [];
  }
}

async function syncPartnerPipelineFromServer() {
  try {
    const [partnersResult, summaryResult] = await Promise.all([
      get('/api/v1/partners'),
      get('/api/v1/executive-dashboard/summary')
    ]);
    serverPartnersCache = (partnersResult.partners || []).filter(isMeaningfulPartner);
    executiveSummaryCache = summaryResult;
    try {
      window.localStorage?.setItem('zenovPartnerDatabase', JSON.stringify(serverPartnersCache));
      window.localStorage?.setItem('zenovPartners', JSON.stringify(serverPartnersCache));
    } catch {}
    return true;
  } catch {
    serverPartnersCache = null;
    executiveSummaryCache = null;
    return false;
  }
}

function isMeaningfulPartner(partner) {
  if (!partner) return false;
  const mobility = partner.mobility || {};
  const energy = partner.energy || {};
  const carbon = partner.carbon_esg || {};
  return Boolean(
    partner.company_name
    || partner.business_type
    || Number(mobility.taxi_count || 0)
    || Number(mobility.ev_taxi_count || 0)
    || Number(mobility.bus_count || 0)
    || Number(mobility.ev_bus_count || 0)
    || Number(mobility.logistics_vehicle_count || 0)
    || Number(mobility.ev_logistics_vehicle_count || 0)
    || Number(energy.solar_capacity_kw || 0)
    || Number(energy.ess_capacity_kwh || 0)
    || Number(energy.charger_count || 0)
    || carbon.mrv_interest
    || carbon.carbon_credit_interest
  );
}

function sumBy(partners, getter) {
  return partners.reduce((total, partner) => total + Number(getter(partner) || 0), 0);
}

function isoToday() {
  return new Date().toISOString().slice(0, 10);
}

function isPastDate(value) {
  return Boolean(value && String(value) < isoToday());
}

function simpleHash(input) {
  const textValue = String(input || '');
  let hash = 0x811c9dc5;
  for (let index = 0; index < textValue.length; index += 1) {
    hash ^= textValue.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return 'ASH-' + (hash >>> 0).toString(16).toUpperCase().padStart(8, '0');
}

function currentAssumptionRegistry() {
  const assumptions = {
    electricity_price_krw_per_kwh: 160,
    carbon_price_krw_per_tco2e: 17000,
    ev_efficiency_km_per_kwh: 5.0,
    solar_generation_kwh_per_kw_year: 1200,
    ess_round_trip_efficiency_pct: 88,
    mrv_factor_version: 'ZENOV-MRV-FACTOR-V1.0',
    discount_rate_pct: 6.5,
    inflation_rate_pct: 2.3
  };
  const payload = JSON.stringify(assumptions);
  return {
    version: 'ASSUMPTION-KR-MOBILITY-SOLAR-V1.0',
    hash: simpleHash(payload),
    created_at: '2026-06-19',
    approved_by: 'Zenov Finance Review',
    assumptions
  };
}

function sensitivityAnalysis(baseValue) {
  const value = Number(baseValue || 0);
  return {
    low: Math.round(value * 0.82),
    base: Math.round(value),
    high: Math.round(value * 1.18)
  };
}

function normalizedPartnerStatus(partner) {
  const status = String(partner?.status || 'NEW').toUpperCase();
  if (status === 'REVIEW') return 'UNDER_REVIEW';
  if (status === 'MEETING') return 'MEETING_SCHEDULED';
  if (status === 'PROPOSAL') return 'PROPOSAL_IN_PROGRESS';
  if (status === 'CONTRACT') return 'CONTRACT_IN_PROGRESS';
  if (status === 'PROPOSAL_READY') return 'PROPOSAL_IN_PROGRESS';
  if (status === 'MEETING_READY') return 'MEETING_SCHEDULED';
  if (status === 'CONTRACT_READY') return 'CONTRACT_IN_PROGRESS';
  if (status === 'PROPOSAL_SENT') return 'PROPOSAL_IN_PROGRESS';
  if (status === 'PROPOSAL_VIEWED') return 'PROPOSAL_IN_PROGRESS';
  if (status === 'FEEDBACK_RECEIVED') return 'PROPOSAL_IN_PROGRESS';
  if (status === 'CONTRACT_REVIEW') return 'CONTRACT_IN_PROGRESS';
  return status;
}

function partnerOpportunity(partner) {
  const mobility = partner?.mobility || {};
  const energy = partner?.energy || {};
  const carbon = partner?.carbon_esg || {};
  const taxiGap = Math.max(0, Number(mobility.taxi_count || 0) - Number(mobility.ev_taxi_count || 0));
  const busGap = Math.max(0, Number(mobility.bus_count || 0) - Number(mobility.ev_bus_count || 0));
  const motorcycleGap = Math.max(0, Number(mobility.motorcycle_count || 0) - Number(mobility.ev_motorcycle_count || 0));
  const logisticsGap = Math.max(0, Number(mobility.logistics_vehicle_count || 0) - Number(mobility.ev_logistics_vehicle_count || 0));
  const evCount = Number(mobility.ev_taxi_count || 0) + Number(mobility.ev_bus_count || 0) + Number(mobility.ev_motorcycle_count || 0) + Number(mobility.ev_logistics_vehicle_count || 0);
  const chargerCount = Number(energy.charger_count || 0);
  const chargingGap = Math.max(0, Math.ceil(evCount / 5) - chargerCount);
  const solarInstalled = String(energy.solar_installed || '').toUpperCase();
  const solarMissing = solarInstalled === 'NO' || (solarInstalled === 'REVIEW' && Number(energy.solar_capacity_kw || 0) === 0);
  const mrvCandidate = ['HIGH', 'MEDIUM', 'YES'].includes(String(carbon.mrv_interest || '').toUpperCase())
    || ['HIGH', 'MEDIUM', 'YES'].includes(String(carbon.carbon_credit_interest || '').toUpperCase());
  const expectedProject = partner?.opportunity?.expected_project
    || carbon.expected_project_type
    || (taxiGap > 0 ? 'EV_TAXI_MRV' : solarMissing ? 'SOLAR_MRV' : 'CARBON_MRV');
  const estimatedCo2e = Number(partner?.opportunity?.estimated_co2e_ton)
    || Math.round((taxiGap * 3.2 + busGap * 18 + motorcycleGap * 0.4 + logisticsGap * 8 + Number(energy.solar_capacity_kw || 0) * 0.45) * 10) / 10;
  const estimatedValue = Number(partner?.opportunity?.estimated_carbon_value_krw) || estimatedCo2e * 17000;
  const actions = [];
  if (Number(mobility.taxi_count || 0) >= 100 && Number(mobility.ev_taxi_count || 0) === 0) actions.push('EV Taxi Carbon MRV 제안 필요');
  if (solarMissing && chargerCount > 0) actions.push('Solar + EV Charging Carbon Project 제안 필요');
  if (mrvCandidate) actions.push('MRV 미팅 일정 제안');
  if (!actions.length && taxiGap + busGap + motorcycleGap + logisticsGap > 0) actions.push('EV 전환 탄소기회 검토');
  if (!actions.length) actions.push('기초 정보 보완 요청');
  return {
    taxiGap,
    busGap,
    motorcycleGap,
    logisticsGap,
    evOpportunity: taxiGap + busGap + motorcycleGap + logisticsGap,
    chargingGap,
    solarMissing,
    mrvCandidate,
    expectedProject,
    estimatedCo2e,
    estimatedValue,
    nextAction: partner?.opportunity?.next_action || actions[0]
  };
}

function clampScore(value) {
  return Math.max(0, Math.min(100, Math.round(Number(value || 0))));
}

function marketIntelligence(partner) {
  const mobility = partner?.mobility || {};
  const energy = partner?.energy || {};
  const carbon = partner?.carbon_esg || {};
  const opportunity = partnerOpportunity(partner);
  const taxiCount = Number(mobility.taxi_count || 0);
  const busCount = Number(mobility.bus_count || 0);
  const logisticsCount = Number(mobility.logistics_vehicle_count || 0);
  const fleetScale = taxiCount + busCount * 4 + logisticsCount * 2 + Number(mobility.motorcycle_count || 0) * 0.2;
  const evGap = opportunity.evOpportunity;
  const chargerCount = Number(energy.charger_count || 0);
  const solarKw = Number(energy.solar_capacity_kw || 0);
  const hasSolarOpportunity = opportunity.solarMissing ? 1 : 0;
  const mrvInterest = ['HIGH', 'YES'].includes(String(carbon.mrv_interest || '').toUpperCase()) ? 1
    : String(carbon.mrv_interest || '').toUpperCase() === 'MEDIUM' ? 0.6 : 0;
  const creditInterest = ['HIGH', 'YES'].includes(String(carbon.carbon_credit_interest || '').toUpperCase()) ? 1
    : String(carbon.carbon_credit_interest || '').toUpperCase() === 'MEDIUM' ? 0.6 : 0;
  const carbonPotentialScore = clampScore(
    Math.min(35, opportunity.estimatedCo2e / 12)
    + Math.min(25, evGap / 5)
    + (hasSolarOpportunity ? 15 : Math.min(15, solarKw / 50))
    + Math.min(10, chargerCount)
    + Math.round((mrvInterest + creditInterest) * 7.5)
  );
  const revenuePotential = Math.round(
    3000000
    + evGap * 250000
    + chargerCount * 120000
    + solarKw * 15000
    + opportunity.estimatedValue * 0.08
  );
  const revenuePotentialScore = clampScore(revenuePotential / 500000);
  const accountScore = clampScore(
    Math.min(30, fleetScale / 5)
    + Math.min(25, evGap / 5)
    + Math.min(20, opportunity.estimatedValue / 1000000)
    + (opportunity.mrvCandidate ? 15 : 0)
    + (chargerCount > 0 ? 5 : 0)
    + (hasSolarOpportunity ? 5 : 0)
  );
  const regionPriority = ['안산', '수원', '서울', '부산', '대구'].includes(String(partner?.region || '').trim()) ? 5 : 0;
  const opportunityScore = clampScore(accountScore * 0.35 + carbonPotentialScore * 0.35 + revenuePotentialScore * 0.2 + regionPriority);
  let recommendedProject = opportunity.expectedProject;
  if (evGap >= 100 && hasSolarOpportunity && chargerCount > 0) recommendedProject = 'EV_SOLAR_COMBINED';
  else if (evGap >= 50) recommendedProject = taxiCount >= busCount ? 'EV_TAXI_MRV' : 'EV_BUS_MRV';
  else if (hasSolarOpportunity) recommendedProject = 'SOLAR_MRV';
  const recommendations = [];
  if (opportunityScore >= 85) recommendations.push('대표 미팅 우선 배정');
  if (evGap >= 100) recommendations.push('EV Taxi Project 제안');
  if (hasSolarOpportunity && chargerCount > 0) recommendations.push('Solar + Charger Project 제안');
  if (opportunity.mrvCandidate) recommendations.push('MRV 프로젝트 제안');
  if (!recommendations.length) recommendations.push('기초 데이터 보완 후 재평가');
  return {
    partnerId: partner?.partner_id || '-',
    companyName: partner?.company_name || partner?.partner_id || '-',
    region: partner?.region || '-',
    businessType: partner?.business_type || '-',
    opportunityScore,
    carbonPotentialScore,
    accountScore,
    revenuePotential,
    arrPotential: Math.round(revenuePotential * 0.35),
    expansionRevenue: Math.round(revenuePotential * 0.45),
    estimatedCo2e: opportunity.estimatedCo2e,
    estimatedValue: opportunity.estimatedValue,
    recommendedProject,
    nextAction: recommendations[0]
  };
}

function renderMarketIntelligence(partners) {
  const output = document.getElementById('marketIntelligenceList');
  if (!output) return;
  if (!partners.length) {
    output.innerHTML = '<div class="summary-row"><span class="label">Market Intelligence</span><strong>파트너 데이터를 저장하면 Top 10 Priority Accounts가 생성됩니다.</strong><span class="pill amber">WAITING</span></div>';
    text('topOpportunityScore', '0');
    text('topCarbonPotential', '0');
    text('topRevenuePotential', krw.format(0));
    text('topPriorityAccounts', '0');
    return;
  }
  const rows = partners
    .map(marketIntelligence)
    .sort((a, b) => b.opportunityScore - a.opportunityScore || b.revenuePotential - a.revenuePotential)
    .slice(0, 10);
  const top = rows[0] || {};
  text('topOpportunityScore', String(top.opportunityScore || 0));
  text('topCarbonPotential', String(top.carbonPotentialScore || 0));
  text('topRevenuePotential', krw.format(top.revenuePotential || 0));
  text('topPriorityAccounts', fmt.format(rows.length));
  output.innerHTML = [
    '<div class="opportunity-row market-intelligence-row header"><span>우선순위</span><span>고객</span><span>지역</span><span>기회점수</span><span>탄소잠재력</span><span>예상매출</span><span>추천 액션</span></div>',
    ...rows.map((item, index) => `
      <div class="opportunity-row market-intelligence-row">
        <strong>#${index + 1}</strong>
        <span>${safe(item.companyName)}<br><small>${safe(item.businessType)}</small></span>
        <span>${safe(item.region)}</span>
        <span>${safe(item.opportunityScore)}</span>
        <span>${safe(item.carbonPotentialScore)} / ${safe(Math.round(item.estimatedCo2e))}t</span>
        <span>${safe(krw.format(item.revenuePotential))}<br><small>ARR ${safe(krw.format(item.arrPotential))}</small></span>
        <span>${safe(item.recommendedProject)}<br><small>${safe(item.nextAction)}</small></span>
      </div>
    `)
  ].join('');
}

async function syncActionCommandsFromServer() {
  try {
    await post('/api/v1/action-commands/generate', {});
    actionCommandCache = await get('/api/v1/action-commands');
    return true;
  } catch {
    actionCommandCache = null;
    return false;
  }
}

async function syncBusinessProjectsFromServer() {
  try {
    await post('/api/v1/projects/generate', {});
    businessProjectCache = await get('/api/v1/projects');
    return true;
  } catch {
    businessProjectCache = null;
    return false;
  }
}

async function syncProgramsFromServer() {
  try {
    await post('/api/v1/programs/generate', {});
    programCache = await get('/api/v1/programs');
    return true;
  } catch {
    programCache = null;
    return false;
  }
}

async function syncCreditReadinessFromServer() {
  try {
    await post('/api/v1/credit-readiness/generate', {});
    creditReadinessCache = await get('/api/v1/credit-readiness');
    return true;
  } catch {
    creditReadinessCache = null;
    return false;
  }
}

async function syncCarbonEconomyFromServer() {
  try {
    await post('/api/v1/economy/generate', {});
    carbonEconomyCache = await get('/api/v1/economy/summary');
    return true;
  } catch {
    carbonEconomyCache = null;
    return false;
  }
}

async function syncTransformationFromServer() {
  try {
    await post('/api/v1/transformation/generate', {});
    transformationCache = await get('/api/v1/transformation/summary');
    return true;
  } catch {
    transformationCache = null;
    return false;
  }
}

function renderBusinessProjectCenter() {
  const summary = businessProjectCache || {};
  const solarProject = (summary.projects || []).find((project) => project.project_type === 'SOLAR_EV_CHARGING') || {};
  const projects = [
    {
      ...solarProject,
      project_name: t('projectFactory.ansanSolarChargingProject'),
      project_type: 'SOLAR_EV_CHARGING',
      partner_name: t('projectFactory.ansanTransport'),
      status: 'QUALIFIED',
      expected_co2e_ton: 282,
      opportunity_level: 'HIGH',
    },
    {
      ...solarProject,
      project_id: 'PRJ-PARTNER-ANSAN-001-SOLAR-600KW',
      project_name: t('projectFactory.ansanSolar600kwProject'),
      project_type: 'SOLAR_EV_CHARGING',
      partner_name: t('projectFactory.ansanTransport'),
      status: 'QUALIFIED',
      expected_co2e_ton: 324,
      opportunity_level: 'HIGH',
    },
  ];
  const totalPremiumGsUsd = projects.reduce((sum, project) => sum + premiumGsUsdValue(project.expected_co2e_ton), 0);
  const totalKetsKrw = projects.reduce((sum, project) => sum + ketsKrwValue(project.expected_co2e_ton), 0);
  text('businessTotalProjects', fmt.format(projects.length || 0));
  text('businessActiveProjects', fmt.format(projects.length || 0));
  text('businessProposalProjects', fmt.format(summary.projects_in_proposal || 0));
  text('businessContractProjects', fmt.format(summary.projects_in_contract || 0));
  text('businessOperatingProjects', fmt.format(summary.operating_projects || 0));
  text('businessExpansionProjects', fmt.format(summary.expansion_projects || 0));
  text('businessTotalCo2e', `${fmt.format(Math.round(projects.reduce((sum, project) => sum + Number(project.expected_co2e_ton || 0), 0)))} t`);
  text('businessCarbonValue', krw.format(totalKetsKrw));
  text('businessSetupRevenue', krw.format(summary.total_setup_revenue_krw || 0));
  text('businessArr', krw.format(summary.total_arr_krw || 0));
  text('businessExpansionValue', krw.format(summary.total_expansion_revenue_krw || 0));
  const output = document.getElementById('businessProjectList');
  if (!output) return;
  output.innerHTML = [
    `<div class="opportunity-row market-intelligence-row project-value-row header"><span>${safe(t('projectFactory.status'))}</span><span>${safe(t('projectFactory.project'))}</span><span>${safe(t('projectFactory.partner'))}</span><span>${safe(t('projectFactory.expectedCo2e'))}</span><span>${safe(t('projectFactory.ketsHeader'))}<br><small>₩15,000/tCO₂e</small></span><span>${safe(t('projectFactory.premiumGsHeader'))}<br><small>$30/tCO₂e</small></span><span>${safe(t('projectFactory.priority'))}</span></div>`,
    ...projects.slice(0, 10).map((project) => `
      <div class="opportunity-row market-intelligence-row project-value-row">
        <strong>${safe(statusLabel(project.status || 'IDEA'))}</strong>
        <span>${safe(project.project_name || project.project_id)}</span>
        <span>${safe(project.partner_name || project.partner_id || '-')}</span>
        <span>${safe(`${fmt.format(Math.round(project.expected_co2e_ton || 0))} t`)}</span>
        <span>${safe(krw.format(ketsKrwValue(project.expected_co2e_ton)))}<br><small>${safe(t('projectFactory.growthEveryTwoYears'))}</small></span>
        <span>${safe(usd.format(premiumGsUsdValue(project.expected_co2e_ton)))}<br><small>${safe(t('projectFactory.growthEveryTwoYears'))}</small></span>
        <span>${safe(t(`projectFactory.priority.${project.opportunity_level || '-'}`))}</span>
      </div>
    `),
    `
      <div class="opportunity-row market-intelligence-row project-value-row total-row">
        <strong>${safe(t('projectFactory.total'))}</strong>
        <span>${safe(t('projectFactory.ansanTotal'))}</span>
        <span>${safe(t('projectFactory.ansanTransport'))}</span>
        <span>${safe(`${fmt.format(Math.round(projects.reduce((sum, project) => sum + Number(project.expected_co2e_ton || 0), 0)))} t`)}</span>
        <span>${safe(krw.format(totalKetsKrw))}<br><small>${safe(t('projectFactory.growthEveryTwoYears'))}</small></span>
        <span>${safe(usd.format(totalPremiumGsUsd))}<br><small>${safe(t('projectFactory.growthEveryTwoYears'))}</small></span>
        <span>${safe(t('projectFactory.priority.HIGH'))}</span>
      </div>
    `
  ].join('');
}

function renderTransformationCenter() {
  const summary = transformationCache || {};
  const items = summary.transformations || [];
  const report = summary.latest_report || {};
  const golden = summary.golden_template || {};
  const commercial = summary.commercial_case || {};
  const impact = report.impact || {};
  const before = report.before_report || {};
  const after = report.after_report || {};
  const targetMarkets = golden.target_markets || [];
  const proposal = commercial.proposal_first_page || {};
  text('transformationScore', `${summary.average_transformation_score || 0}`);
  text('carbonReadiness', summary.top_carbon_readiness || '-');
  text('growthStage', summary.top_growth_stage || '-');
  text('fiveYearRevenue', krw.format(summary.total_5y_revenue_krw || 0));
  text('fiveYearCarbonValue', krw.format(summary.total_5y_carbon_value_krw || 0));
  text('transformationProgress', `${impact.transformation_progress_pct || 0}%`);
  text('beforeValue', krw.format(before.current_carbon_value_krw || 0));
  text('afterValue', krw.format(after.expected_carbon_value_krw || 0));
  text('transformationRoi', `${after.expected_roi_pct || 0}%`);
  text('goldenTemplateScore', `${golden.golden_template_score || 0}`);
  text('goldenTemplateStatus', golden.status || '-');
  text('replicationReadiness', golden.replication_readiness || '-');
  text('nextTargetMarket', targetMarkets[0]?.region || '-');
  text('annualCostSaving', krw.format(proposal.annual_cost_saving_krw || 0));
  text('annualNewRevenue', krw.format(proposal.annual_new_revenue_krw || 0));
  text('annualCarbonValue', krw.format(proposal.expected_carbon_value_krw || 0));
  text('paybackPeriod', `${proposal.payback_period_years || 0}y`);
  text('commercialExpectedCo2e', `${fmt.format(proposal.expected_co2e_ton || 0)} t`);
  text('commercialRoi', `${proposal.roi_pct || 0}%`);
  const output = document.getElementById('transformationList');
  const commercialOutput = document.getElementById('commercialCaseList');
  const goldenOutput = document.getElementById('goldenTemplateList');
  if (commercialOutput) {
    const basis = commercial.input_basis || {};
    const breakdown = commercial.benefit_breakdown || {};
    if (commercial.commercial_case_id) {
      commercialOutput.innerHTML = `
        <div class="opportunity-row market-intelligence-row header"><span>Business Case</span><span>Vehicles</span><span>EV</span><span>New Revenue</span><span>Carbon Value</span><span>Total Benefit</span><span>Message</span></div>
        <div class="opportunity-row market-intelligence-row">
          <strong>${safe(commercial.partner_name || '-')}<br><small>${safe(commercial.commercial_case_id || '-')}</small></strong>
          <span>${safe(basis.vehicle_count || 0)}</span>
          <span>${safe(`${basis.ev_count || 0} → ${basis.target_ev_count || 0}`)}</span>
          <span>${safe(krw.format(proposal.annual_new_revenue_krw || 0))}</span>
          <span>${safe(krw.format(proposal.expected_carbon_value_krw || 0))}</span>
          <span>${safe(krw.format(breakdown.annual_total_benefit_krw || 0))}</span>
          <span>${safe('절감액과 수익 중심 제안')}</span>
        </div>
      `;
    } else {
      commercialOutput.innerHTML = '<div class="summary-row"><span class="label">Business Case</span><strong>Partner Folder 저장 후 제안서 첫 페이지 숫자를 생성합니다.</strong><span class="pill amber">WAITING</span></div>';
    }
  }
  if (goldenOutput) {
    if (golden.golden_template_score) {
      const breakdown = golden.score_breakdown || {};
      goldenOutput.innerHTML = `
        <div class="opportunity-row market-intelligence-row header"><span>Golden Template</span><span>Data</span><span>Trust</span><span>MRV</span><span>Stability</span><span>Business</span><span>Markets</span></div>
        <div class="opportunity-row market-intelligence-row">
          <strong>${safe(golden.partner_name || '-')}<br><small>${safe(golden.certification_id || '-')}</small></strong>
          <span>${safe(breakdown.data_quality || 0)}</span>
          <span>${safe(breakdown.trust || 0)}</span>
          <span>${safe(breakdown.mrv_accuracy || 0)}</span>
          <span>${safe(breakdown.operational_stability || 0)}</span>
          <span>${safe(breakdown.business_value || 0)}</span>
          <span>${safe(targetMarkets.slice(0, 4).map((item) => item.region).join(' → ') || '-')}</span>
        </div>
      `;
    } else {
      goldenOutput.innerHTML = '<div class="summary-row"><span class="label">Golden Template</span><strong>안산교통 인증 데이터를 생성하는 중입니다.</strong><span class="pill amber">WAITING</span></div>';
    }
  }
  if (!output) return;
  if (!items.length) {
    output.innerHTML = '<div class="summary-row"><span class="label">Transformation</span><strong>Partner Folder 저장 후 Carbon Business Operator 전환 계획을 생성합니다.</strong><span class="pill amber">WAITING</span></div>';
    return;
  }
  output.innerHTML = [
    '<div class="opportunity-row market-intelligence-row header"><span>Partner</span><span>Score</span><span>Readiness</span><span>Stage</span><span>Before Value</span><span>After Value</span><span>ROI</span></div>',
    ...items.slice(0, 10).map((item) => `
      <div class="opportunity-row market-intelligence-row">
        <strong>${safe(item.partner_name || item.partner_id)}</strong>
        <span>${safe(item.transformation_score || 0)}</span>
        <span>${safe(item.carbon_readiness || '-')}</span>
        <span>${safe(item.growth_stage || '-')}</span>
        <span>${safe(krw.format(before.current_carbon_value_krw || 0))}</span>
        <span>${safe(krw.format(after.expected_carbon_value_krw || 0))}</span>
        <span>${safe(`${after.expected_roi_pct || 0}%`)}</span>
      </div>
    `)
  ].join('');
}

function renderCarbonEconomyCenter() {
  const project = {
    project_name: t('projectFactory.ansanSolar600kwProject'),
    partner_name: t('projectFactory.ansanTransport'),
    expected_co2e_ton: 324,
    opportunity_level: 'HIGH',
  };
  text('economyCarbonValue', usd.format(premiumGsUsdValue(project.expected_co2e_ton)));
  text('economyDistributed', krw.format(ketsKrwValue(project.expected_co2e_ton)));
  text('economyStakeholders', `${fmt.format(project.expected_co2e_ton)} t`);
  text('economyValueScore', project.opportunity_level);
  const output = document.getElementById('carbonEconomyList');
  if (!output) return;
  output.innerHTML = [
    `<div class="opportunity-row market-intelligence-row project-value-row header"><span>${safe(t('projectFactory.status'))}</span><span>${safe(t('projectFactory.project'))}</span><span>${safe(t('projectFactory.partner'))}</span><span>${safe(t('projectFactory.expectedCo2e'))}</span><span>${safe(t('projectFactory.ketsHeader'))}<br><small>₩15,000/tCO₂e</small></span><span>${safe(t('projectFactory.premiumGsHeader'))}<br><small>$30/tCO₂e</small></span><span>${safe(t('projectFactory.priority'))}</span></div>`,
    `
      <div class="opportunity-row market-intelligence-row project-value-row">
        <strong>${safe(statusLabel('QUALIFIED'))}</strong>
        <span>${safe(project.project_name)}</span>
        <span>${safe(project.partner_name)}</span>
        <span>${safe(`${fmt.format(project.expected_co2e_ton)} t`)}</span>
        <span>${safe(krw.format(ketsKrwValue(project.expected_co2e_ton)))}<br><small>${safe(t('projectFactory.growthEveryTwoYears'))}</small></span>
        <span>${safe(usd.format(premiumGsUsdValue(project.expected_co2e_ton)))}<br><small>${safe(t('projectFactory.growthEveryTwoYears'))}</small></span>
        <span>${safe(t(`projectFactory.priority.${project.opportunity_level}`))}</span>
      </div>
    `
  ].join('');
}

function renderCreditReadinessCenter() {
  const summary = creditReadinessCache || {};
  const items = (summary.credit_readiness || []).filter((item) => item.project_type !== 'EV_TAXI_CARBON_MRV');
  text('creditReadyCount', fmt.format(items.filter((item) => item.credit_status === 'READY_FOR_REGISTRY').length));
  text('registryReadyCount', fmt.format(items.filter((item) => item.registry_readiness === 'READY').length));
  text('verificationReadyCount', fmt.format(items.filter((item) => item.verification_ready).length));
  text('topCreditGrade', items[0]?.credit_grade || '-');
  text('creditReadinessScore', `${items.length ? Math.round((items.reduce((sum, item) => sum + Number(item.credit_readiness_score || 0), 0) / items.length) * 10) / 10 : 0}`);
  const output = document.getElementById('creditReadinessList');
  if (!output) return;
  if (!items.length) {
    output.innerHTML = `<div class="summary-row"><span class="label">${safe(t('projectFactory.creditReadiness'))}</span><strong>${safe(t('projectFactory.creditWaiting'))}</strong><span class="pill amber">${safe(t('status.WAITING'))}</span></div>`;
    return;
  }
  output.innerHTML = [
    `<div class="opportunity-row market-intelligence-row header"><span>${safe(t('projectFactory.status'))}</span><span>${safe(t('projectFactory.project'))}</span><span>${safe(t('projectFactory.score'))}</span><span>${safe(t('projectFactory.grade'))}</span><span>${safe(t('projectFactory.verification'))}</span><span>${safe(t('projectFactory.registry'))}</span></div>`,
    ...items.slice(0, 10).map((item) => `
      <div class="opportunity-row market-intelligence-row">
        <strong>${safe(t(`projectFactory.creditStatus.${item.credit_status || '-'}`))}</strong>
        <span>${safe(item.project_name || item.project_id)}<br><small>${safe(item.methodology_id || '-')}</small></span>
        <span>${safe(item.credit_readiness_score || 0)}</span>
        <span>${safe(item.credit_grade || '-')}</span>
        <span>${safe(t(`projectFactory.creditStatus.${item.verification_ready ? 'READY' : 'NOT_READY'}`))}</span>
        <span>${safe(t(`projectFactory.creditStatus.${item.registry_readiness || 'NOT_READY'}`))}</span>
      </div>
    `)
  ].join('');
}

function renderProgramCenter() {
  const summary = programCache || {};
  const programs = summary.programs || [];
  text('programTotalPrograms', fmt.format(summary.total_programs || programs.length || 0));
  text('programOperatingPrograms', fmt.format(summary.operating_programs || 0));
  text('programProjectCount', fmt.format(summary.project_count || 0));
  text('programPartnerCount', fmt.format(summary.partner_count || 0));
  text('programTotalCo2e', `${fmt.format(Math.round(summary.total_co2e_ton || 0))} t`);
  text('programCarbonValue', krw.format(summary.total_carbon_value_krw || 0));
  text('programRevenue', krw.format(summary.total_revenue_krw || 0));
  text('programArr', krw.format(summary.total_arr_krw || 0));
  text('programExpansionValue', krw.format(summary.total_expansion_value_krw || 0));
  const output = document.getElementById('programPortfolioList');
  if (!output) return;
  if (!programs.length) {
    output.innerHTML = '<div class="summary-row"><span class="label">Program Portfolio</span><strong>Project가 생성되면 Program이 자동 생성됩니다.</strong><span class="pill amber">WAITING</span></div>';
    return;
  }
  output.innerHTML = [
    '<div class="opportunity-row market-intelligence-row header"><span>상태</span><span>프로그램</span><span>지역</span><span>Project</span><span>Partner</span><span>CO₂e</span><span>ARR</span></div>',
    ...programs.slice(0, 10).map((program) => `
      <div class="opportunity-row market-intelligence-row">
        <strong>${safe(statusLabel(program.status || 'IDEA'))}</strong>
        <span>${safe(program.program_name || program.program_id)}<br><small>${safe(program.program_type || '-')} / Risk ${safe(program.risk || '-')}</small></span>
        <span>${safe(program.region || '-')}</span>
        <span>${safe(program.project_count || 0)}</span>
        <span>${safe(program.partner_count || 0)}</span>
        <span>${safe(`${fmt.format(Math.round(program.total_co2e_ton || 0))} t`)}</span>
        <span>${safe(krw.format(program.arr_krw || 0))}</span>
      </div>
    `)
  ].join('');
}

function renderActionCommandCenter() {
  const output = document.getElementById('actionCommandList');
  if (!output) return;
  const summary = actionCommandCache || {};
  const commands = summary.commands || [];
  text('totalActionCommands', fmt.format(summary.total_action_commands || commands.length || 0));
  text('highPriorityActions', fmt.format(summary.high_priority_actions || 0));
  text('dueThisWeekActions', fmt.format(summary.due_this_week || 0));
  text('overdueActions', fmt.format(summary.overdue_actions || 0));
  text('completedActionCommands', fmt.format(summary.completed_actions || 0));
  text('actionCompletionRate', `${summary.action_completion_rate || 0}%`);
  const next = commands.find((command) => command.action_status !== 'DONE') || commands[0];
  text('primaryActionOwner', next?.owner || '-');
  text('nextActionCommandTitle', next?.action_title || '-');
  if (!commands.length) {
    output.innerHTML = '<div class="summary-row"><span class="label">오늘 해야 할 일</span><strong>파트너 저장 후 추천 액션이 표시됩니다.</strong><span class="pill amber">WAITING</span></div>';
    return;
  }
  output.innerHTML = [
    '<div class="opportunity-row market-intelligence-row header"><span>상태</span><span>액션</span><span>담당자</span><span>기한</span><span>우선순위</span><span>필요 자료</span><span>성공 기준</span></div>',
    ...commands.slice(0, 10).map((command) => `
      <div class="opportunity-row market-intelligence-row">
        <strong>${safe(command.action_status || 'TODO')}</strong>
        <span>${safe(command.action_title)}<br><small>${safe(command.partner_name || command.partner_id)}</small></span>
        <span>${safe(command.owner || '-')}</span>
        <span>${safe(command.due_date || '-')}</span>
        <span>${safe(command.priority === 'HIGH' ? '높음' : command.priority === 'MEDIUM' ? '보통' : command.priority || '-')}</span>
        <span>${safe((command.required_materials || []).slice(0, 2).join(' / '))}</span>
        <span>${safe((command.success_metric || []).slice(0, 2).join(' / '))}</span>
      </div>
    `)
  ].join('');
}

function setupExecutiveTabs() {
  const tabs = Array.from(document.querySelectorAll('[data-exec-tab]'));
  const panes = Array.from(document.querySelectorAll('[data-exec-pane]'));
  if (!tabs.length || tabs.some((tab) => tab.dataset.bound === 'true')) return;
  tabs.forEach((tab) => {
    tab.dataset.bound = 'true';
    tab.addEventListener('click', () => {
      const key = tab.dataset.execTab;
      tabs.forEach((item) => item.classList.toggle('active', item === tab));
      panes.forEach((pane) => pane.classList.toggle('active', pane.dataset.execPane === key));
    });
  });
}

function productOperationsForPartner(partner) {
  const mobility = partner?.mobility || {};
  const energy = partner?.energy || {};
  const success = partner?.partner_success || {};
  const fleetCount = Number(mobility.taxi_count || 0) + Number(mobility.bus_count || 0) + Number(mobility.logistics_vehicle_count || 0) + Number(mobility.motorcycle_count || 0);
  const chargerCount = Number(energy.charger_count || 0) + Number(energy.fast_charger_count || 0) + Number(energy.slow_charger_count || 0);
  const solarLinked = ['YES', 'REVIEW'].includes(String(energy.solar_installed || '').toUpperCase()) || Number(energy.solar_capacity_kw || 0) > 0 || chargerCount > 0;
  const programReady = (businessProjectCache?.total_projects || 0) >= 2 || normalizedPartnerStatus(partner) === 'OPERATING';
  const eligibleProduct = fleetCount >= 500 || programReady && fleetCount >= 300
    ? 'Enterprise'
    : fleetCount > 100 || (chargerCount > 0 && solarLinked)
      ? 'Professional'
      : 'Starter';
  const dataConnectedDays = Number(success.monthly_performance?.data_connected_days || success.data_connected_days || 0);
  const validPackets = Number(success.monthly_performance?.valid_packets || success.valid_packets || 0);
  const packets = Number(success.monthly_performance?.packets_collected || success.packets_collected || 0);
  const reportViewed = ['SENT', 'REVIEWED'].includes(success.monthly_report?.report_status);
  const taskDone = partner?.next_action?.action_status === 'DONE';
  const dataConnectionRate = packets ? Math.round((validPackets / packets) * 100) : dataConnectedDays ? Math.min(100, Math.round((dataConnectedDays / 30) * 100)) : 60;
  const usageScore = Math.round((dataConnectionRate * 0.45) + (reportViewed ? 25 : 10) + (taskDone ? 20 : 8) + (normalizedPartnerStatus(partner) === 'OPERATING' ? 10 : 5));
  const productHealth = usageScore >= 75 ? 'Healthy' : usageScore >= 45 ? 'At Risk' : 'Inactive';
  const upsell = eligibleProduct === 'Starter' && fleetCount > 100
    ? 'Professional 추천'
    : eligibleProduct === 'Professional' && programReady
      ? 'Enterprise 추천'
      : '현재 상품 유지';
  const churnRisk = productHealth === 'Inactive' || dataConnectionRate < 40 || (!reportViewed && normalizedPartnerStatus(partner) === 'OPERATING') ? 'Churn Risk' : 'Low Risk';
  const playbook = eligibleProduct === 'Enterprise'
    ? 'Program / Portfolio / Governance'
    : eligibleProduct === 'Professional'
      ? 'Carbon Value / Solar Integration'
      : '데이터 연결 / 월간 리포트';
  const arr = eligibleProduct === 'Enterprise' ? 120000000 : eligibleProduct === 'Professional' ? 50400000 : 12000000;
  return { eligibleProduct, productHealth, usageScore, upsell, churnRisk, playbook, arr };
}

function productOperationsSummary(partners) {
  const items = partners.map((partner) => ({ partner, product: productOperationsForPartner(partner) }));
  return {
    items,
    starterCount: items.filter((item) => item.product.eligibleProduct === 'Starter').length,
    professionalCount: items.filter((item) => item.product.eligibleProduct === 'Professional').length,
    enterpriseCount: items.filter((item) => item.product.eligibleProduct === 'Enterprise').length,
    upgradeCandidates: items.filter((item) => item.product.upsell !== '현재 상품 유지').length,
    churnRiskCustomers: items.filter((item) => item.product.churnRisk === 'Churn Risk').length,
    arrByProduct: sumBy(items, (item) => item.product.arr),
  };
}

function riskLabel(score) {
  const value = Number(score || 0);
  if (value >= 70) return 'HIGH';
  if (value >= 40) return 'MEDIUM';
  return 'LOW';
}

function buildPredictivePerformance(partners, productSummary, projectsSummary, proposal, commands, metrics = {}) {
  const opportunityRows = partners.map((partner) => partnerOpportunity(partner));
  const opportunityCo2e = sumBy(opportunityRows, (item) => item.estimatedCo2e);
  const opportunityCarbonValue = sumBy(opportunityRows, (item) => item.estimatedValue);
  const annualCo2e = Number(projectsSummary.total_co2e_ton || 0) || opportunityCo2e;
  const annualRevenue = Number(proposal.annual_new_revenue_krw || 0)
    || Number(projectsSummary.total_arr_krw || 0)
    || Number(productSummary.arrByProduct || 0);
  const annualCarbonValue = Number(projectsSummary.total_carbon_value_krw || 0)
    || Number(proposal.expected_carbon_value_krw || 0)
    || opportunityCarbonValue;
  const avgHealth = Number(metrics.avgHealth || 0);
  const overdue = Number(metrics.overdue || 0);
  const highPriority = Number(metrics.highPriority || 0);
  const projectProgress = Number(metrics.projectProgress || 0);
  const executionFactor = Math.max(0.58, Math.min(1.18, 0.78 + (avgHealth / 220) + (projectProgress / 420) - (overdue * 0.04)));
  const forecastFor = (days) => ({
    days,
    co2e: Math.round((annualCo2e * (days / 365) * executionFactor) * 10) / 10,
    revenue: Math.round(annualRevenue * (days / 365) * executionFactor),
    carbonValue: Math.round(annualCarbonValue * (days / 365) * executionFactor)
  });
  const forecasts = {
    d30: forecastFor(30),
    d90: forecastFor(90),
    d180: forecastFor(180),
    y1: forecastFor(365)
  };
  const revenueRiskScore = clampScore(
    (annualRevenue ? 18 : 55)
    + overdue * 12
    + productSummary.churnRiskCustomers * 18
    + Math.max(0, 70 - avgHealth) * 0.45
    + Math.max(0, 60 - projectProgress) * 0.25
  );
  const carbonRiskScore = clampScore(
    (annualCarbonValue ? 15 : 60)
    + Math.max(0, 65 - projectProgress) * 0.35
    + Math.max(0, highPriority - 1) * 8
    + (opportunityCo2e > annualCo2e ? 8 : 0)
  );
  const actions = [];
  if (revenueRiskScore >= 40) actions.push('30일 매출 부족 가능성 점검');
  if (carbonRiskScore >= 40) actions.push('MRV/실데이터 품질 확인');
  if (productSummary.upgradeCandidates > 0) actions.push('업그레이드 후보 미팅 배정');
  if (!actions.length) actions.push('현재 추세 유지, 우선 파트너 후속');
  return {
    forecasts,
    revenueRiskScore,
    revenueRisk: riskLabel(revenueRiskScore),
    carbonRiskScore,
    carbonValueRisk: riskLabel(carbonRiskScore),
    recommendedActions: actions
  };
}

function buildDigitalTwinSimulation(partners, productSummary, projectsSummary, proposal) {
  const assumption = currentAssumptionRegistry();
  const opportunityRows = partners.map((partner) => partnerOpportunity(partner));
  const currentRevenue = Number(proposal.annual_new_revenue_krw || 0)
    || Number(projectsSummary.total_arr_krw || 0)
    || Number(productSummary.arrByProduct || 0);
  const currentCarbonValue = Number(projectsSummary.total_carbon_value_krw || 0)
    || sumBy(opportunityRows, (item) => item.estimatedValue);
  const currentValue = currentRevenue + currentCarbonValue;
  const currentCo2e = Number(projectsSummary.total_co2e_ton || 0)
    || sumBy(opportunityRows, (item) => item.estimatedCo2e);
  const futureEvOpportunity = Math.max(1, sumBy(opportunityRows, (item) => item.evOpportunity));
  const solarScenarioKw = Math.max(500, partners.length * 500);
  const essScenarioKwh = solarScenarioKw * 1.6;
  const futureCo2e = Math.round((currentCo2e + futureEvOpportunity * 3.2 + solarScenarioKw * 0.45) * 10) / 10;
  const futureCarbonValue = Math.round(futureCo2e * 17000);
  const futureRevenue = Math.max(currentRevenue, 120000000 * Math.max(1, partners.length));
  const futureValue = futureRevenue + futureCarbonValue;
  const investment = Math.max(10000000, futureEvOpportunity * 1500000 + solarScenarioKw * 900000 + essScenarioKwh * 350000);
  const incrementalValue = Math.max(1, futureValue - currentValue);
  const payback = Math.round((investment / incrementalValue) * 10) / 10;
  const risk = clampScore((payback > 8 ? 62 : payback > 5 ? 45 : 28) + (futureEvOpportunity > 100 ? 8 : 0) - (futureValue > currentValue * 1.6 ? 8 : 0));
  const recommendation = futureValue > currentValue * 1.6
    ? 'EV + Solar + ESS 확대 투자 검토'
    : payback <= 5
      ? 'Digital Twin 시나리오를 제안서에 반영'
      : '투자비/회수기간 재조정 후 검토';
  return {
    currentValue,
    futureValue,
    futureCo2e,
    futureCarbonValue,
    futureRevenue,
    payback,
    risk,
    recommendation,
    assumption,
    sensitivity: sensitivityAnalysis(futureValue),
    scenario: `EV 확대 ${futureEvOpportunity}대 / Solar ${solarScenarioKw}kW / ESS ${essScenarioKwh}kWh`
  };
}

function buildCarbonAssetLedger(partners, twin) {
  const totalAssets = Math.max(1, partners.length);
  const currentValue = Number(twin?.futureValue || 0);
  const owner = partners[0]?.company_name || 'Zenov Partner Pool';
  const assetId = 'AST-ZNV-' + isoToday().replaceAll('-', '') + '-000001';
  const evidenceId = 'EVD-ZNV-' + isoToday().replaceAll('-', '') + '-000001';
  const mrvId = 'MRV-ZNV-' + isoToday().replaceAll('-', '') + '-000001';
  return {
    asset_id: assetId,
    evidence_id: evidenceId,
    mrv_id: mrvId,
    owner,
    current_value: currentValue,
    status: 'VERIFIED',
    created_at: isoToday(),
    verified_at: isoToday(),
    retired_at: '-',
    total_assets: totalAssets,
    verified_assets: totalAssets,
    transferred_assets: 1,
    retired_assets: 0,
    total_asset_value: currentValue,
    lifecycle: ['Evidence', 'Draft', 'Pending', 'Verified', 'Transferred', 'Retired'],
    ownership_ledger: [
      { from: 'Origin Evidence', to: owner, event: 'ASSET_CREATED' },
      { from: owner, to: 'Zenov Custody', event: 'TRANSFER_REQUEST' },
      { from: 'Zenov Custody', to: owner, event: 'TRANSFER_COMPLETED' }
    ],
    value_ledger: [
      Math.round(currentValue * 0.82),
      Math.round(currentValue),
      Math.round(currentValue * 1.18)
    ]
  };
}

function renderExecutiveTabs() {
  setupExecutiveTabs();
  const partners = readPartners();
  const productSummary = productOperationsSummary(partners);
  const statusCount = (status) => partners.filter((partner) => normalizedPartnerStatus(partner) === status).length;
  const successRecords = partners.map((partner) => partner.partner_success || {});
  const commands = (actionCommandCache || {}).commands || [];
  const projectsSummary = businessProjectCache || {};
  const programsSummary = programCache || {};
  const creditSummary = creditReadinessCache || {};
  const transformationSummaryData = transformationCache || {};
  const commercial = transformationSummaryData.commercial_case || {};
  const proposal = commercial.proposal_first_page || {};
  const today = isoToday();
  const todayMeetings = partners.filter((partner) => partner.meeting?.meeting_date === today && !['COMPLETED', 'CANCELLED'].includes(partner.meeting?.meeting_status)).length;
  const todayDue = commands.filter((command) => command.due_date === today && command.action_status !== 'DONE').length
    || partners.filter((partner) => partner.next_action?.due_date === today && partner.next_action?.action_status !== 'DONE').length;
  const overdue = (actionCommandCache || {}).overdue_actions
    || partners.filter((partner) => isPastDate(partner.next_action?.due_date) && partner.next_action?.action_status !== 'DONE').length;
  const highPriority = (actionCommandCache || {}).high_priority_actions || commands.filter((command) => command.priority === 'HIGH').length;
  const totalProjects = Number(projectsSummary.total_projects || 0);
  const activeProjects = Number(projectsSummary.active_projects || 0);
  const operatingProjects = Number(projectsSummary.operating_projects || 0);
  const projectProgress = totalProjects ? Math.round((operatingProjects / totalProjects) * 100) : 0;
  const totalPrograms = Number(programsSummary.total_programs || 0);
  const operatingPrograms = Number(programsSummary.operating_programs || 0);
  const programProgress = totalPrograms ? Math.round((operatingPrograms / totalPrograms) * 100) : 0;
  const healthScores = successRecords.map((success) => Number(success.customer_health?.health_score || 0)).filter(Boolean);
  const avgHealth = healthScores.length ? Math.round(sumBy(healthScores, (score) => score) / healthScores.length) : 0;
  const expansionCount = successRecords.filter((success) => (success.expansion_opportunity?.recommendations || []).length > 0).length;
  const monthlyReports = successRecords.filter((success) => ['CREATED', 'SENT', 'REVIEWED'].includes(success.monthly_report?.report_status)).length;
  text('tabTodayMeetings', fmt.format(todayMeetings));
  text('tabTodayDue', fmt.format(todayDue));
  text('tabHighPriority', fmt.format(highPriority));
  text('tabOverdue', fmt.format(overdue));
  text('tabNewPartners', fmt.format(statusCount('NEW')));
  text('tabProposalsSent', fmt.format((executiveSummaryCache?.sales_execution_summary || {}).proposals_sent || 0));
  text('tabContractsInProgress', fmt.format(statusCount('CONTRACT_IN_PROGRESS')));
  text('tabContractsDone', fmt.format(statusCount('OPERATING')));
  text('tabActiveProjects', fmt.format(activeProjects));
  text('tabOperatingProjects', fmt.format(operatingProjects));
  text('tabBlockedProjects', fmt.format((actionCommandCache || {}).blocked_actions || 0));
  text('tabProjectProgress', `${projectProgress}%`);
  text('tabActualCo2e', `${fmt.format(Number(projectsSummary.total_co2e_ton || 0))} t`);
  text('tabCarbonValue', krw.format(projectsSummary.total_carbon_value_krw || 0));
  text('tabCreditReady', fmt.format(creditSummary.carbon_credits_ready || 0));
  text('tabRegistryReady', fmt.format(creditSummary.registry_ready || 0));
  const solarFinance = {
    generationKwh: 750000,
    lowSavingKrw: 112500000,
    highSavingKrw: 135000000,
    reductionTon: 315,
    voluntaryLowKrw: 3150000,
    voluntaryHighKrw: 15750000,
    premiumLowKrw: 15750000,
    premiumHighKrw: 47250000,
    capexKrw: 800000000,
    simplePaybackYears: 7.1,
    targetPaybackYears: 5
  };
  text('tabSolarGeneration', `${fmt.format(solarFinance.generationKwh)} kWh`);
  text('tabAnnualSaving', `${krw.format(solarFinance.lowSavingKrw)}~${krw.format(solarFinance.highSavingKrw)}`);
  text('tabSolarReduction', `${fmt.format(solarFinance.reductionTon)} t`);
  text('tabPayback', `${solarFinance.targetPaybackYears}${t('financeSolar.yearsTarget')}`);
  text('tabPartnerTotal', fmt.format(partners.length));
  text('tabPartnerOperating', fmt.format(statusCount('OPERATING')));
  text('tabPartnerHealth', fmt.format(avgHealth));
  text('tabExpansionOpportunities', fmt.format(expansionCount));
  text('tabStarterCount', fmt.format(productSummary.starterCount));
  text('tabProfessionalCount', fmt.format(productSummary.professionalCount));
  text('tabEnterpriseCount', fmt.format(productSummary.enterpriseCount));
  text('tabUpgradeCandidates', fmt.format(productSummary.upgradeCandidates));
  text('tabChurnRiskCustomers', fmt.format(productSummary.churnRiskCustomers));
  text('tabMonthlyReports', fmt.format(monthlyReports));
  text('tabAuditReports', fmt.format(transformationSummaryData.golden_template ? 1 : 0));
  text('tabMrvReports', fmt.format(totalProjects));
  text('tabExecutiveReports', fmt.format(transformationSummaryData.latest_report ? 1 : 0));

  const todayList = document.getElementById('tabTodayList');
  if (todayList) {
    const next = commands.find((command) => command.action_status !== 'DONE') || commands[0];
    todayList.innerHTML = next
      ? `<div class="summary-row"><span class="label">${safe(next.owner || 'Owner')}</span><strong>${safe(next.action_title || '오늘 처리할 액션')}</strong><span class="pill amber">${safe(next.action_status || 'TODO')}</span></div>`
      : '<div class="summary-row"><span class="label">TODAY</span><strong>오늘 즉시 처리할 액션이 없습니다.</strong><span class="pill mint">CLEAR</span></div>';
  }
  const priorityList = document.getElementById('tabPriorityPartners');
  const financeSolarList = document.getElementById('tabFinanceSolarList');
  if (financeSolarList) {
    financeSolarList.innerHTML = [
      row(t('financeSolar.project'), t('financeSolar.projectValue'), t('common.ready')),
      row(t('financeSolar.generationBasis'), t('financeSolar.generationBasisValue'), t('common.ready')),
      row(t('financeSolar.energySaving'), t('financeSolar.energySavingValue'), t('common.ready')),
      row(t('financeSolar.carbonReduction'), t('financeSolar.carbonReductionValue'), t('common.ready')),
      row(t('financeSolar.voluntaryCredit'), t('financeSolar.voluntaryCreditValue'), t('common.ready')),
      row(t('financeSolar.premiumCredit'), t('financeSolar.premiumCreditValue'), t('common.ready')),
      row(t('financeSolar.payback'), t('financeSolar.paybackValue'), t('common.ready')),
      row(t('financeSolar.assetization'), t('financeSolar.assetizationValue'), t('common.ready'))
    ].join('');
  }
  const productList = document.getElementById('tabPartnerProductList');
  if (productList) {
    productList.innerHTML = [
      row(t('execPartnerProduct.expectedProduct'), 'Solar + EV Charging Project', 'OK'),
      row(t('execPartnerProduct.ketsValue'), '₩4,230,000', 'OK'),
      row(t('execPartnerProduct.ketsCalculation'), '282t × 15,000원 = 4,230,000원', 'OK'),
      row(t('execPartnerProduct.premiumGsValue'), '$8,460.00', 'OK'),
      row(t('execPartnerProduct.premiumGsCalculation'), '282t × $30 = $8,460.00', 'OK')
    ].join('');
  }
  if (priorityList) {
    const rows = partners.slice(0, 5).map((partner) => {
      const opportunity = partnerOpportunity(partner);
      return `<div class="summary-row"><span class="label">${safe(partner.business_type || 'Partner')}</span><strong>${safe(partner.company_name || partner.partner_id)}</strong><span class="pill amber">${safe(opportunity.nextAction || 'REVIEW')}</span></div>`;
    });
    priorityList.innerHTML = rows.length
      ? rows.join('')
      : '<div class="summary-row"><span class="label">PARTNER</span><strong>Partner Folder에 고객 정보를 입력하면 자동으로 여기에 연결됩니다.</strong><span class="pill amber">WAITING</span></div>';
  }
  const reportList = document.getElementById('tabReportSummaryList');
  if (reportList) {
    reportList.innerHTML = [
      row(t('execReport.partnerData'), `${fmt.format(partners.length)} ${t('execReport.partners')} / ${fmt.format(statusCount('OPERATING'))} ${t('execReport.operating')}`, partners.length ? 'OK' : 'HOLD'),
      row(t('execReport.carbonSummary'), `${fmt.format(Number(projectsSummary.total_co2e_ton || 0))} t / ${krw.format(projectsSummary.total_carbon_value_krw || 0)}`, Number(projectsSummary.total_co2e_ton || 0) ? 'OK' : 'HOLD'),
      row(t('execReport.mrv'), `${fmt.format(totalProjects)} ${t('execReport.projects')}`, totalProjects ? 'OK' : 'HOLD')
    ].join('');
  }
}

function renderOpportunityList(partners) {
  const output = document.getElementById('opportunityList');
  if (!output) return;
  if (!partners.length) {
    output.innerHTML = '<div class="summary-row"><span class="label">우선 관리 파트너</span><strong>Partner Folder에서 파트너 정보를 먼저 저장하세요.</strong><span class="pill amber">WAITING</span></div>';
    return;
  }
  const rows = partners
    .map((partner) => ({ partner, opportunity: partnerOpportunity(partner) }))
    .sort((a, b) => b.opportunity.estimatedValue - a.opportunity.estimatedValue)
    .slice(0, 10);
  output.innerHTML = [
    '<div class="opportunity-row header"><span>회사명</span><span>사업유형</span><span>예상 프로젝트</span><span>예상 CO₂e</span><span>예상 가치</span><span>다음 액션</span></div>',
    ...rows.map(({ partner, opportunity }) => `
      <div class="opportunity-row">
        <strong>${safe(partner.company_name || partner.partner_id || '-')}</strong>
        <span>${safe(partner.business_type || '-')}</span>
        <span>${safe(opportunity.expectedProject)}</span>
        <span>${safe(`${fmt.format(Math.round(opportunity.estimatedCo2e))} t`)}</span>
        <span>${safe(krw.format(opportunity.estimatedValue))}</span>
        <span>${safe(opportunity.nextAction)}</span>
      </div>
    `)
  ].join('');
}

function renderExecutivePartnerSummary() {
  const partners = readPartners();
  const statusCount = (status) => partners.filter((partner) => normalizedPartnerStatus(partner) === status).length;
  const totalTaxi = sumBy(partners, (partner) => partner.mobility?.taxi_count);
  const totalEvTaxi = sumBy(partners, (partner) => partner.mobility?.ev_taxi_count);
  const totalBus = sumBy(partners, (partner) => partner.mobility?.bus_count);
  const totalEvBus = sumBy(partners, (partner) => partner.mobility?.ev_bus_count);
  const totalMotorcycle = sumBy(partners, (partner) => partner.mobility?.motorcycle_count);
  const totalEvMotorcycle = sumBy(partners, (partner) => partner.mobility?.ev_motorcycle_count);
  const totalLogistics = sumBy(partners, (partner) => partner.mobility?.logistics_vehicle_count);
  const totalEvLogistics = sumBy(partners, (partner) => partner.mobility?.ev_logistics_vehicle_count);
  const solarKw = sumBy(partners, (partner) => partner.energy?.solar_capacity_kw);
  const essKwh = sumBy(partners, (partner) => partner.energy?.ess_capacity_kwh);
  const chargers = sumBy(partners, (partner) => partner.energy?.charger_count);
  const fastChargers = sumBy(partners, (partner) => partner.energy?.fast_charger_count);
  const slowChargers = sumBy(partners, (partner) => partner.energy?.slow_charger_count);
  const opportunities = partners.map(partnerOpportunity);
  const taxiOpportunity = sumBy(opportunities, (item) => item.taxiGap);
  const busOpportunity = sumBy(opportunities, (item) => item.busGap);
  const evOpportunity = sumBy(opportunities, (item) => item.evOpportunity);
  const chargingGap = sumBy(opportunities, (item) => item.chargingGap);
  const solarOpportunity = opportunities.filter((item) => item.solarMissing).length;
  const mrvPipeline = opportunities.filter((item) => item.mrvCandidate).length;
  const estimatedCo2e = sumBy(opportunities, (item) => item.estimatedCo2e);
  const estimatedValue = sumBy(opportunities, (item) => item.estimatedValue);
  const activeOpportunities = opportunities.filter((item) => item.evOpportunity > 0 || item.solarMissing || item.mrvCandidate || item.chargingGap > 0).length;
  const today = isoToday();
  const todayActions = partners.filter((partner) => partner.next_action?.due_date === today && !['DONE', 'BLOCKED'].includes(partner.next_action?.action_status)).length;
  const delayedActions = partners.filter((partner) => isPastDate(partner.next_action?.due_date) && !['DONE'].includes(partner.next_action?.action_status)).length;
  const upcomingMeetings = partners.filter((partner) => partner.meeting?.meeting_date && !['COMPLETED', 'CANCELLED'].includes(partner.meeting?.meeting_status)).length;
  const writingProposals = partners.filter((partner) => ['WRITING', 'REVISED', 'FEEDBACK_RECEIVED'].includes(partner.proposal?.proposal_status)).length;
  const completedActions = partners.filter((partner) => partner.next_action?.action_status === 'DONE').length;
  const blockedActions = partners.filter((partner) => partner.next_action?.action_status === 'BLOCKED').length;
  const workflowLogCount = sumBy(partners, (partner) => partner.audit_logs?.length || 0);
  const proposalPackagesCreated = partners.filter((partner) => partner.sales_automation?.proposal_ready).length;
  const roiEstimatesGenerated = partners.filter((partner) => partner.sales_automation?.roi_ready).length;
  const meetingScriptsReady = partners.filter((partner) => partner.sales_automation?.meeting_script_ready).length;
  const contractReadyPartners = partners.filter((partner) => partner.sales_automation?.contract_ready).length;
  const operatingReadyPartners = partners.filter((partner) => partner.sales_automation?.onboarding_ready || normalizedPartnerStatus(partner) === 'ONBOARDING_READY').length;
  const missingDocuments = sumBy(partners, (partner) => (partner.sales_automation?.contract_checklist || []).filter((item) => !item.ready).length);
  const highOpportunityPartners = opportunities.filter((item) => item.estimatedValue >= 10000000 || item.evOpportunity >= 100).length;
  const salesAutomationReady = partners.filter((partner) => partner.sales_automation?.proposal_ready && partner.sales_automation?.roi_ready && partner.sales_automation?.meeting_script_ready).length;
  const proposalsSent = partners.filter((partner) => partner.sales_execution?.send_log?.send_status === 'SENT').length;
  const notOpened = partners.filter((partner) => partner.sales_execution?.send_log?.send_status === 'SENT' && (!partner.sales_execution?.view_tracking?.view_status || partner.sales_execution.view_tracking.view_status === 'NOT_OPENED')).length;
  const openedMaterials = partners.filter((partner) => ['OPENED', 'MULTIPLE_VIEWS'].includes(partner.sales_execution?.view_tracking?.view_status)).length;
  const feedbackReceived = partners.filter((partner) => Boolean(partner.sales_execution?.feedback_log?.feedback_type)).length;
  const followupsDue = partners.filter((partner) => (partner.sales_execution?.follow_up_actions || []).length > 0 && partner.next_action?.action_status !== 'DONE').length;
  const highInterestPartners = partners.filter((partner) => ['HIGH', 'HOT'].includes(partner.sales_execution?.conversion_status) || Number(partner.sales_execution?.view_tracking?.view_count || 0) >= 2).length;
  const conversionProbabilityAvg = partners.length
    ? Math.round(sumBy(partners, (partner) => partner.sales_execution?.conversion_score || 0) / partners.length)
    : 0;
  const hotPartners = partners.filter((partner) => partner.sales_execution?.conversion_status === 'HOT').length;
  const successRecords = partners.map((partner) => partner.partner_success || {});
  const monthlyReportsCreated = successRecords.filter((success) => ['CREATED', 'SENT', 'REVIEWED'].includes(success.monthly_report?.report_status)).length;
  const reportsSent = successRecords.filter((success) => ['SENT', 'REVIEWED'].includes(success.monthly_report?.report_status)).length;
  const healthScores = successRecords
    .map((success) => Number(success.customer_health?.health_score || 0))
    .filter((score) => score > 0);
  const averageCustomerHealthScore = healthScores.length
    ? Math.round(sumBy(healthScores, (score) => score) / healthScores.length)
    : 0;
  const atRiskPartners = successRecords.filter((success) => ['AT_RISK', 'CHURN_RISK'].includes(success.customer_health?.health_status)).length;
  const expansionOpportunities = successRecords.filter((success) => (success.expansion_opportunity?.recommendations || []).length > 0).length;
  const estimatedExpansionValue = sumBy(successRecords, (success) => success.expansion_opportunity?.estimated_additional_value || 0);
  const renewalDuePartners = successRecords.filter((success) => {
    const days = success.renewal_status?.days_to_renewal;
    return typeof days === 'number' && days <= 90;
  }).length;

  text('totalPartners', fmt.format(partners.length));
  text('newPartners', fmt.format(statusCount('NEW')));
  text('questionnaireSubmitted', fmt.format(statusCount('QUESTIONNAIRE_SUBMITTED')));
  text('underReviewPartners', fmt.format(statusCount('UNDER_REVIEW')));
  text('meetingScheduled', fmt.format(statusCount('MEETING_SCHEDULED')));
  text('proposalPartners', fmt.format(statusCount('PROPOSAL_IN_PROGRESS')));
  text('contractPartners', fmt.format(statusCount('CONTRACT_IN_PROGRESS')));
  text('reviewHoldPartners', fmt.format(statusCount('HOLD') + statusCount('REJECTED')));
  text('operatingPartners', fmt.format(statusCount('OPERATING')));
  text('activeOpportunities', fmt.format(activeOpportunities));
  text('mobilityTaxiSummary', `${fmt.format(totalTaxi)} / ${fmt.format(totalEvTaxi)}`);
  text('taxiConversionOpportunity', fmt.format(taxiOpportunity));
  text('mobilityBusSummary', `${fmt.format(totalBus)} / ${fmt.format(totalEvBus)}`);
  text('busConversionOpportunity', fmt.format(busOpportunity));
  text('mobilityMotorcycleSummary', `${fmt.format(totalMotorcycle)} / ${fmt.format(totalEvMotorcycle)}`);
  text('mobilityLogisticsSummary', `${fmt.format(totalLogistics)} / ${fmt.format(totalEvLogistics)}`);
  text('energySolarSummary', `${fmt.format(solarKw)} kW / ${fmt.format(essKwh)} kWh`);
  text('energyChargerSummary', fmt.format(chargers));
  text('energyChargerSplit', `${fmt.format(fastChargers)} / ${fmt.format(slowChargers)}`);
  text('evOpportunity', fmt.format(evOpportunity));
  text('chargingGap', fmt.format(chargingGap));
  text('solarOpportunity', fmt.format(solarOpportunity));
  text('mrvPipelineCount', fmt.format(mrvPipeline));
  text('estimatedCo2e', `${fmt.format(Math.round(estimatedCo2e))} t`);
  text('estimatedCarbonValue', krw.format(estimatedValue));
  text('topEstimatedCo2e', `${fmt.format(Math.round(estimatedCo2e))} t`);
  text('topEstimatedCarbonValue', krw.format(estimatedValue));
  text('todayActions', fmt.format(todayActions));
  text('delayedActions', fmt.format(delayedActions));
  text('upcomingMeetings', fmt.format(upcomingMeetings));
  text('writingProposals', fmt.format(writingProposals));
  text('contractProgress', fmt.format(statusCount('CONTRACT_IN_PROGRESS')));
  text('completedActions', fmt.format(completedActions));
  text('blockedActions', fmt.format(blockedActions));
  text('workflowLogCount', fmt.format(workflowLogCount));
  text('proposalPackagesCreated', fmt.format(proposalPackagesCreated));
  text('roiEstimatesGenerated', fmt.format(roiEstimatesGenerated));
  text('meetingScriptsReady', fmt.format(meetingScriptsReady));
  text('contractReadyPartners', fmt.format(contractReadyPartners));
  text('operatingReadyPartners', fmt.format(operatingReadyPartners));
  text('missingDocuments', fmt.format(missingDocuments));
  text('highOpportunityPartners', fmt.format(highOpportunityPartners));
  text('salesAutomationReady', fmt.format(salesAutomationReady));
  text('proposalsSent', fmt.format(proposalsSent));
  text('notOpened', fmt.format(notOpened));
  text('openedMaterials', fmt.format(openedMaterials));
  text('feedbackReceived', fmt.format(feedbackReceived));
  text('followupsDue', fmt.format(followupsDue));
  text('highInterestPartners', fmt.format(highInterestPartners));
  text('conversionProbabilityAvg', `${fmt.format(conversionProbabilityAvg)}`);
  text('hotPartners', fmt.format(hotPartners));
  text('monthlyReportsCreated', fmt.format(monthlyReportsCreated));
  text('reportsSent', fmt.format(reportsSent));
  text('averageCustomerHealthScore', `${fmt.format(averageCustomerHealthScore)}`);
  text('atRiskPartners', fmt.format(atRiskPartners));
  text('expansionOpportunities', fmt.format(expansionOpportunities));
  text('estimatedExpansionValue', krw.format(estimatedExpansionValue));
  text('renewalDuePartners', fmt.format(renewalDuePartners));
  text('partnerSuccessEngine', partners.length ? 'CONNECTED' : 'READY');
  text('pipelineNew', fmt.format(statusCount('NEW')));
  text('pipelineReview', fmt.format(statusCount('QUESTIONNAIRE_SUBMITTED') + statusCount('UNDER_REVIEW')));
  text('pipelineMeeting', fmt.format(statusCount('MEETING_SCHEDULED')));
  text('pipelineProposal', fmt.format(statusCount('PROPOSAL_IN_PROGRESS')));
  text('pipelineContract', fmt.format(statusCount('CONTRACT_IN_PROGRESS')));
  text('pipelineOperating', fmt.format(statusCount('OPERATING')));
  if (executiveSummaryCache) {
    const partnerSummary = executiveSummaryCache.partner_summary || {};
    const mobilitySummary = executiveSummaryCache.mobility_summary || {};
    const energySummary = executiveSummaryCache.energy_summary || {};
    const successSummary = executiveSummaryCache.partner_success || {};
    text('totalPartners', fmt.format(partnerSummary.total_partners || partners.length));
    text('newPartners', fmt.format(partnerSummary.new_partners || 0));
    text('questionnaireSubmitted', fmt.format(partnerSummary.questionnaire_submitted || 0));
    text('underReviewPartners', fmt.format(partnerSummary.under_review || 0));
    text('meetingScheduled', fmt.format(partnerSummary.meeting_scheduled || 0));
    text('proposalPartners', fmt.format(partnerSummary.proposal_in_progress || 0));
    text('contractPartners', fmt.format(partnerSummary.contract_in_progress || 0));
    text('operatingPartners', fmt.format(partnerSummary.operating_partners || 0));
    text('mobilityTaxiSummary', `${fmt.format(mobilitySummary.total_taxi_count || 0)} / ${fmt.format(mobilitySummary.total_ev_taxi_count || 0)}`);
    text('mobilityBusSummary', `${fmt.format(mobilitySummary.total_bus_count || 0)} / ${fmt.format(mobilitySummary.total_ev_bus_count || 0)}`);
    text('energySolarSummary', `${fmt.format(energySummary.total_solar_capacity_kw || 0)} kW / ${fmt.format(energySummary.total_ess_capacity_kwh || 0)} kWh`);
    text('energyChargerSummary', fmt.format(energySummary.total_charger_count || 0));
    text('energyChargerSplit', `${fmt.format(energySummary.total_fast_charger_count || 0)} / ${fmt.format(energySummary.total_slow_charger_count || 0)}`);
    text('monthlyReportsCreated', fmt.format(successSummary.monthly_reports_created || 0));
    text('reportsSent', fmt.format(successSummary.reports_sent || 0));
    text('averageCustomerHealthScore', fmt.format(successSummary.average_customer_health_score || 0));
    text('atRiskPartners', fmt.format(successSummary.at_risk_partners || 0));
    text('expansionOpportunities', fmt.format(successSummary.expansion_opportunities || 0));
    text('estimatedExpansionValue', krw.format(successSummary.estimated_expansion_value || 0));
    text('partnerSuccessEngine', executiveSummaryCache.storage_mode === 'postgres' ? 'POSTGRES' : 'SERVER FILE');
  }
  renderOpportunityList(partners);
  renderMarketIntelligence(partners);
  renderActionCommandCenter();
  renderBusinessProjectCenter();
  renderProgramCenter();
}

function partnerToReviewQuestionnaire(partner) {
  if (!partner) return null;
  const mobility = partner.mobility || {};
  const energy = partner.energy || {};
  const carbon = partner.carbon_esg || {};
  const opportunity = partnerOpportunity(partner);
  const hasMobility = Boolean(
    Number(mobility.taxi_count || 0)
    || Number(mobility.bus_count || 0)
    || Number(mobility.motorcycle_count || 0)
    || Number(mobility.logistics_vehicle_count || 0)
  );
  const hasEnergy = Boolean(
    Number(energy.charger_count || 0)
    || Number(energy.solar_capacity_kw || 0)
    || Number(energy.ess_capacity_kwh || 0)
  );
  const dataSource = hasMobility && hasEnergy ? 'FLEET_AND_ENERGY' : hasMobility ? 'FLEET' : hasEnergy ? 'ENERGY' : 'QUESTIONNAIRE';
  const completionChecks = [
    Boolean(partner.company_name),
    Boolean(partner.business_type),
    Boolean(partner.contact_name || partner.ceo_name || partner.owner?.owner_name),
    hasMobility,
    hasEnergy,
    Boolean(carbon.mrv_interest || carbon.carbon_credit_interest),
    Boolean(carbon.expected_project_type || opportunity.expectedProject),
    Boolean(partner.next_action?.action_title || opportunity.nextAction)
  ];
  const progress = Math.round((completionChecks.filter(Boolean).length / completionChecks.length) * 100);
  const status = normalizedPartnerStatus(partner);
  return {
    partner_type: partner.business_type || '-',
    data_source: dataSource,
    ev_transition_interest: opportunity.evOpportunity > 0 ? 'HIGH' : 'REVIEW',
    charging_installable: Number(energy.charger_count || 0) > 0 ? 'YES' : 'REVIEW',
    solar_installable: String(energy.solar_installed || '').toUpperCase() === 'YES' ? 'YES' : opportunity.solarMissing ? 'REVIEW' : 'NO',
    data_connection_consent: status === 'OPERATING' ? 'YES' : partner.data_connection_consent || 'REVIEW',
    pilot_timing: status === 'OPERATING' ? 'READY' : status === 'MEETING_SCHEDULED' ? 'READY' : 'REVIEW',
    completion_rate: progress,
    status: status === 'OPERATING' ? 'ONBOARDING_READY' : status,
    data_ready: hasMobility || hasEnergy,
    fleet_ready: hasMobility,
    driver_signup_ready: Boolean(partner.driver_signup_ready || partner.owner?.owner_name),
    vehicle_registration_ready: hasMobility,
    saved_at: partner.updated_at || partner.created_at,
    next_action: partner.next_action?.action_title || opportunity.nextAction,
    onboarding: {
      totalVehicles: Number(mobility.taxi_count || 0)
        + Number(mobility.bus_count || 0)
        + Number(mobility.motorcycle_count || 0)
        + Number(mobility.logistics_vehicle_count || 0)
    }
  };
}

function analyzePartnerQuestionnaire(questionnaire) {
  if (!questionnaire) {
    return {
      progress: 0,
      status: 'WAITING',
      reviewLabel: t('executive.partnerWaiting'),
      dataStatus: t('executive.partnerNoQuestionnaire'),
      nextAction: t('executive.partnerNextQuestionnaire'),
      rows: [[t('executive.partnerQuestionnaire'), t('executive.partnerNoQuestionnaire'), 'HOLD']]
    };
  }

  const fields = [
    'partner_type',
    'data_source',
    'ev_transition_interest',
    'charging_installable',
    'solar_installable',
    'data_connection_consent',
    'pilot_timing'
  ];
  const completed = fields.filter((field) => {
    const value = questionnaire[field];
    return value && value !== 'NONE' && value !== 'UNKNOWN';
  }).length;
  const progress = Number.isFinite(Number(questionnaire.completion_rate))
    ? Number(questionnaire.completion_rate)
    : Math.round((completed / fields.length) * 100);
  const onboarding = questionnaire.onboarding || {};
  const consentReady = questionnaire.data_connection_consent === 'YES';
  const dataReady = Boolean(questionnaire.data_ready) || ['CSV', 'TMONEY', 'DTG_GPS', 'API', 'OCPP'].includes(questionnaire.data_source);
  const siteReady = ['YES', 'REVIEW'].includes(questionnaire.charging_installable) || questionnaire.solar_installable === 'YES';
  const fleetReady = Boolean(questionnaire.fleet_ready) || Number(onboarding.totalVehicles || 0) > 0;
  const driverReady = Boolean(questionnaire.driver_signup_ready);
  const vehicleReady = Boolean(questionnaire.vehicle_registration_ready);

  let status = 'REVIEW_NEEDED';
  let reviewLabel = t('executive.partnerReviewNeeded');
  let dataStatus = t('executive.partnerDataBasic');
  let nextAction = t('executive.partnerNextDataConsent');

  if (questionnaire.status === 'QUESTIONNAIRE_SUBMITTED') {
    status = 'QUESTIONNAIRE_SUBMITTED';
    reviewLabel = '질문지 제출 완료';
    dataStatus = '경영진 검토 대기';
    nextAction = '관리자 검토를 시작하세요.';
  } else if (questionnaire.status === 'ONBOARDING_READY') {
    status = 'ONBOARDING_READY';
    reviewLabel = t('executive.partnerOnboardingReady');
    dataStatus = t('executive.partnerDataConnected');
    nextAction = t('executive.partnerNextOnboarding');
  } else if (!consentReady) {
    status = 'DATA_CONSENT_REQUIRED';
    reviewLabel = t('executive.partnerConsentRequired');
    dataStatus = t('executive.partnerDataConsentMissing');
  } else if (!dataReady) {
    status = 'BASIC_REVIEW';
    reviewLabel = t('executive.partnerBasicReview');
    dataStatus = t('executive.partnerDataCsv');
    nextAction = t('executive.partnerNextSampleCsv');
  } else if (siteReady) {
    status = 'PILOT_READY';
    reviewLabel = t('executive.partnerPilotReady');
    dataStatus = t('executive.partnerDataConnected');
    nextAction = t('executive.partnerNextPilot');
  } else {
    status = 'REVIEW_READY';
    reviewLabel = t('executive.partnerReviewReady');
    dataStatus = t('executive.partnerDataConnected');
    nextAction = t('executive.partnerNextSiteReview');
  }

  return {
    progress,
    status,
    reviewLabel,
    dataStatus,
    nextAction,
    rows: [
      [t('executive.partnerType'), questionnaire.partner_type || '-', 'OK'],
      [t('executive.partnerDataSource'), questionnaire.data_source || '-', dataReady ? 'OK' : 'HOLD'],
      [t('executive.partnerConsent'), questionnaire.data_connection_consent || '-', consentReady ? 'OK' : 'HOLD'],
      [t('executive.partnerEvPlan'), questionnaire.ev_transition_interest || '-', ['YES', 'HIGH'].includes(questionnaire.ev_transition_interest) ? 'OK' : 'HOLD'],
      [t('executive.partnerFleetScale'), `${onboarding.totalVehicles || '-'}`, fleetReady ? 'OK' : 'HOLD'],
      [t('executive.partnerDriverSignup'), driverReady ? 'READY' : 'REVIEW', driverReady ? 'OK' : 'HOLD'],
      [t('executive.partnerVehicleRegistration'), vehicleReady ? 'READY' : 'REVIEW', vehicleReady ? 'OK' : 'HOLD'],
      [t('executive.partnerChargingSolar'), `${questionnaire.charging_installable || '-'} / ${questionnaire.solar_installable || '-'}`, siteReady ? 'OK' : 'HOLD'],
      [t('executive.partnerPilotTiming'), questionnaire.pilot_timing || '-', ['IMMEDIATE', 'READY'].includes(questionnaire.pilot_timing) ? 'OK' : 'HOLD'],
      [t('executive.partnerSavedAt'), questionnaire.saved_at ? new Date(questionnaire.saved_at).toLocaleString() : '-', 'OK']
    ]
  };
}

function renderPartnerReview() {
  const statusEl = document.getElementById('partnerReviewStatus');
  const progressEl = document.getElementById('partnerProgressRate');
  const reviewEl = document.getElementById('partnerReviewable');
  const dataEl = document.getElementById('partnerDataStatus');
  const nextEl = document.getElementById('partnerNextStep');
  const outputEl = document.getElementById('partnerReviewOutput');
  if (!statusEl || !progressEl || !reviewEl || !dataEl || !nextEl || !outputEl) return;

  const partners = readPartners();
  const latestPartner = partners.find((partner) => partner.status === 'OPERATING') || partners[partners.length - 1];
  const analysis = analyzePartnerQuestionnaire(partnerToReviewQuestionnaire(latestPartner) || readPartnerQuestionnaire());
  statusEl.textContent = analysis.status;
  statusEl.className = `pill ${['QUESTIONNAIRE_SUBMITTED', 'ONBOARDING_READY', 'PILOT_READY', 'REVIEW_READY'].includes(analysis.status) ? 'mint' : 'amber'}`;
  progressEl.textContent = `${analysis.progress}%`;
  progressEl.className = `value small ${analysis.progress >= 80 ? 'mint' : 'amber'}`;
  reviewEl.textContent = analysis.reviewLabel;
  reviewEl.className = `value small ${['QUESTIONNAIRE_SUBMITTED', 'ONBOARDING_READY', 'PILOT_READY', 'REVIEW_READY'].includes(analysis.status) ? 'mint' : 'amber'}`;
  dataEl.textContent = analysis.dataStatus;
  nextEl.textContent = analysis.nextAction;
  outputEl.innerHTML = analysis.rows.map(([label, value, status]) => row(label, value, status)).join('');
  renderExecutivePartnerSummary();
}

async function pageHome() {
  await initializeLanguage();
  if (!await requireExecutiveDashboardAuth()) return;
  renderExecutiveAuthBadge();
  const { db } = await loadBaseStatus();
  const job = await loadLatestJob().catch(() => null);
  await syncPartnerPipelineFromServer();
  await syncActionCommandsFromServer();
  await syncBusinessProjectsFromServer();
  await syncProgramsFromServer();
  await syncCreditReadinessFromServer();
  await syncCarbonEconomyFromServer();
  await syncTransformationFromServer();
  renderReality(db, job);
  renderPartnerReview();
  renderActionCommandCenter();
  renderBusinessProjectCenter();
  renderProgramCenter();
  renderCreditReadinessCenter();
  renderCarbonEconomyCenter();
  renderTransformationCenter();
  renderExecutiveTabs();
  if (job) {
    text('executiveAssetCount', fmt.format(job.asset_candidate_count || 0));
    text('executiveCo2e', `${Number((job.success_count || 0) * 0.027).toFixed(3)} tCO2e`);
    text('executiveProjects', fmt.format(businessProjectCache?.total_projects || 0));
    text('executivePortfolio', krw.format(Number(job.asset_candidate_count || 0) * 1350));
  }
  window.addEventListener('storage', (event) => {
    if (event.key === 'zenovPartnerDatabase' || event.key === 'zenovPartners' || event.key === 'zenovPartnerQuestionnaire') {
      renderPartnerReview();
    }
  });
  try {
    const channel = new BroadcastChannel('zenov-partner-database');
    channel.onmessage = () => renderPartnerReview();
  } catch {}
  setInterval(renderPartnerReview, 2000);
}

async function pageV3Center(centerKey) {
  const { db, summary } = await loadBaseStatus();
  const job = await loadLatestJob().catch(() => null);
  const pgLive = Boolean(db?.postgres?.configured && db?.postgres?.connected);
  const influxLive = Boolean(db?.influxdb?.configured && db?.influxdb?.connected);
  const configs = {
    projectFactory: {
      status: 'QUALIFIED',
      metrics: [
        ['센터 순서', '안산교통 → 인천 → 원주'],
        ['현재 기준', '안산교통 QUALIFIED / 인천 준비 / 원주 다음'],
        ['예상 상태', 'QUALIFIED']
      ],
      rows: [
        ['안산교통', 'Solar + EV Charging Project / EV Taxi Carbon MRV 산정 완료', 'OK'],
        ['인천', '다음 파트너 연동 준비 상태', 'HOLD'],
        ['원주', '인천 다음 검토 순서', 'HOLD']
      ]
    },
    dataCollection: {
      status: job?.total_rows ? 'CONNECTED' : 'READINESS_REQUIRED',
      metrics: [
        ['label.telemetryPackets', fmt.format(Math.max(Number(summary.total_packets || 0), Number(job?.total_rows || 0)))],
        ['label.importRows', fmt.format(job?.total_rows || 0)],
        ['label.gatewayMode', pgLive && influxLive ? t('status.realDb') : t('status.memoryFallback')]
      ],
      rows: [
        ['feature.gateway', 'feature.gatewayDesc', job?.total_rows ? 'OK' : 'HOLD'],
        ['feature.telemetry', 'feature.telemetryDesc', summary.total_packets ? 'OK' : 'HOLD'],
        ['feature.storeForward', 'feature.storeForwardDesc', 'HOLD']
      ]
    },
    trustEvidence: {
      status: job?.evidence_count ? 'ACTIVE' : 'READINESS_REQUIRED',
      metrics: [
        ['label.packet', fmt.format(Math.max(Number(summary.total_packets || 0), Number(job?.total_rows || 0)))],
        ['label.evidence', fmt.format(job?.evidence_count || 0)],
        ['label.auditEvents', fmt.format(Math.max(Number(summary.total_packets || 0), Number(job?.evidence_count || 0)))]
      ],
      rows: [
        ['feature.trustPacket', 'feature.trustPacketDesc', 'OK'],
        ['feature.evidenceId', 'feature.evidenceIdDesc', job?.evidence_count ? 'OK' : 'HOLD'],
        ['feature.calibration', 'feature.calibrationDesc', 'HOLD']
      ]
    },
    mrvCenter: {
      status: job?.mrv_count ? 'ACTIVE' : 'READINESS_REQUIRED',
      metrics: [
        ['label.mrv', fmt.format(job?.mrv_count || 0)],
        ['label.methodology', 'ZENOV-MOBILITY-MRV-001'],
        ['label.reduction', `${Number((job?.success_count || 0) * 27).toFixed(1)} kgCO2e`]
      ],
      rows: [
        ['feature.mobilityMrv', 'feature.mobilityMrvDesc', 'OK'],
        ['feature.solarMrv', 'feature.solarMrvDesc', 'OK'],
        ['feature.doubleCounting', 'feature.doubleCountingDesc', 'HOLD']
      ]
    },
    carbonValue: {
      status: summary.estimated_carbon_value ? 'ACTIVE' : 'READINESS_REQUIRED',
      metrics: [
        ['label.runtimeValue', krw.format(summary.estimated_carbon_value || 0)],
        ['label.currency', 'KRW'],
        ['label.priceSource', 'INTERNAL_POC_PRICE']
      ],
      rows: [
        ['feature.valueCalculator', 'feature.valueCalculatorDesc', 'OK'],
        ['feature.currency', 'feature.currencyDesc', 'OK'],
        ['feature.priceLogging', 'feature.priceLoggingDesc', 'OK']
      ]
    },
    registry: {
      status: job?.asset_candidate_count ? 'PENDING' : 'DRAFT',
      metrics: [
        ['label.asset', fmt.format(job?.asset_candidate_count || 0)],
        ['label.registry', t('status.NOT_REGISTERED')],
        ['label.lifecycle', 'DRAFT / PENDING / VERIFIED / RETIRED']
      ],
      rows: [
        ['feature.carbonProject', 'feature.carbonProjectDesc', 'OK'],
        ['feature.carbonAsset', 'feature.carbonAssetDesc', job?.asset_candidate_count ? 'OK' : 'HOLD'],
        ['feature.statusAudit', 'feature.statusAuditDesc', 'OK']
      ]
    },
    verification: {
      status: job?.verification_pass_count ? 'UNDER_REVIEW' : 'REQUESTED',
      metrics: [
        ['label.verification', fmt.format(job?.verification_pass_count || 0)],
        ['label.verificationPass', job?.success_count ? `${((job.verification_pass_count || 0) / job.success_count * 100).toFixed(1)}%` : '0%'],
        ['label.evidencePackage', job?.report_id || '-']
      ],
      rows: [
        ['feature.verificationRequest', 'feature.verificationRequestDesc', 'OK'],
        ['feature.evidencePackage', 'feature.evidencePackageDesc', job?.evidence_count ? 'OK' : 'HOLD'],
        ['feature.reviewWorkflow', 'feature.reviewWorkflowDesc', 'HOLD']
      ]
    },
    digitalTwin: {
      status: 'DEFERRED',
      metrics: [
        ['label.scenario', 'Taxi 100 → 500'],
        ['label.solarScenario', 'Solar 1MW → 5MW'],
        ['label.developmentGate', t('rule.realDataFirst')]
      ],
      rows: [
        ['feature.scenarioBuilder', 'feature.scenarioBuilderDesc', 'HOLD'],
        ['feature.roiSimulator', 'feature.roiSimulatorDesc', 'HOLD'],
        ['feature.projectAutoDesign', 'feature.projectAutoDesignDesc', 'HOLD']
      ]
    },
    dealRoom: {
      status: 'GATED',
      metrics: [
        ['label.visibleAssetRule', t('rule.noVerificationNoInvestment')],
        ['label.documents', 'Evidence / MRV / Value / Audit'],
        ['label.investmentStatus', t('status.preparation')]
      ],
      rows: [
        ['feature.verifiedOnly', 'feature.verifiedOnlyDesc', 'HOLD'],
        ['feature.dataRoom', 'feature.dataRoomDesc', 'HOLD'],
        ['feature.investorSummary', 'feature.investorSummaryDesc', 'HOLD']
      ]
    },
    marketplace: {
      status: 'PROHIBITED_BEFORE_REGISTRY',
      metrics: [
        ['label.marketplaceRule', t('rule.noMarketplaceBeforeRegistry')],
        ['label.investorInterest', t('status.preparation')],
        ['label.forbidden', 'Token / Exchange / Auto Investment']
      ],
      rows: [
        ['feature.investorProfile', 'feature.investorProfileDesc', 'HOLD'],
        ['feature.projectMatching', 'feature.projectMatchingDesc', 'HOLD'],
        ['feature.interest', 'feature.interestDesc', 'HOLD']
      ]
    },
    ecosystem: {
      status: 'ACTIVE',
      metrics: [
        ['label.customer', 'Ansan Transport'],
        ['label.partnerAccounts', '3'],
        ['label.ecosystemTypes', 'Customer / Partner / Verifier / Investor']
      ],
      rows: [
        ['feature.partnerManagement', 'feature.partnerManagementDesc', 'OK'],
        ['feature.referralManagement', 'feature.referralManagementDesc', 'OK'],
        ['feature.tenantExpansion', 'feature.tenantExpansionDesc', 'HOLD']
      ]
    },
    compliance: {
      status: 'ACTIVE',
      metrics: [
        ['label.dailyAudit', t('status.preparation')],
        ['label.integrityReport', job?.summary_hash ? job.summary_hash.slice(0, 16) : '-'],
        ['label.complianceReport', job?.report_id || '-']
      ],
      rows: [
        ['feature.dailyAudit', 'feature.dailyAuditDesc', 'OK'],
        ['feature.integrityReport', 'feature.integrityReportDesc', 'OK'],
        ['feature.complianceReport', 'feature.complianceReportDesc', 'HOLD']
      ]
    }
  };
  const config = configs[centerKey];
  text('centerStatus', statusLabel(config.status));
  setClass('centerStatus', `pill ${['ACTIVE', 'CONNECTED', 'DESIGN_READY', 'PENDING', 'UNDER_REVIEW'].includes(config.status) ? 'mint' : 'amber'}`);
  const metrics = document.getElementById('centerMetrics');
  if (metrics) {
    metrics.innerHTML = config.metrics.map(([labelKey, value]) => (
      `<div class="card"><div class="label">${safe(t(labelKey))}</div><div class="value small">${safe(value)}</div></div>`
    )).join('');
  }
  const output = document.getElementById('centerOutput');
  if (output) {
    output.innerHTML = config.rows.map(([labelKey, descKey, status]) => row(t(labelKey), t(descKey), status)).join('');
  }
}

async function pageProjectFactory() {
  await pageV3Center('projectFactory');
  await syncBusinessProjectsFromServer();
  await syncProgramsFromServer();
  await syncCreditReadinessFromServer();
  await syncCarbonEconomyFromServer();
  await syncTransformationFromServer();
  renderBusinessProjectCenter();
  renderProgramCenter();
  renderCreditReadinessCenter();
  renderCarbonEconomyCenter();
  renderTransformationCenter();
}
async function pageDataCollection() {
  await pageV3Center('dataCollection');
  setupPilotPortalBridge();
}
const pageTrustEvidence = () => pageV3Center('trustEvidence');
async function pageMrvCenter() {
  await pageV3Center('mrvCenter');
  setupPilotPortalBridge();
}
const pageCarbonValue = () => pageV3Center('carbonValue');
const pageRegistry = () => pageV3Center('registry');
const pageVerification = () => pageV3Center('verification');
const pageDigitalTwin = () => pageV3Center('digitalTwin');
const pageDealRoom = () => pageV3Center('dealRoom');
const pageMarketplace = () => pageV3Center('marketplace');
const pageEcosystem = () => pageV3Center('ecosystem');
const pageCompliance = () => pageV3Center('compliance');
async function pageEducation() {
  await initializeLanguage();
  setupEducationMaterials();
  renderEducationMaterials();
}

async function pageCustomerZero() {
  const { db } = await loadBaseStatus();
  const job = await loadLatestJob();
  renderReality(db, job);
  renderCustomerZero(job);
  const output = document.getElementById('jobOutput');
  if (output) {
    output.innerHTML = [
      row(t('label.importJob'), safe(job.import_job_id), 'OK'),
      row(t('label.csvSource'), safe(job.source_filename), isRehearsalSource(job.source_filename) ? 'HOLD' : 'OK'),
      row(t('label.csvRows'), t('value.rows', { count: fmt.format(job.total_rows || 0) }), 'OK'),
      row(t('label.successFailed'), `${fmt.format(job.success_count || 0)} / ${fmt.format(job.failed_count || 0)}`, Number(job.failed_count || 0) === 0 ? 'OK' : 'HOLD'),
      row(t('label.evidenceMrvAsset'), `${fmt.format(job.evidence_count || 0)} / ${fmt.format(job.mrv_count || 0)} / ${fmt.format(job.asset_candidate_count || 0)}`, 'OK'),
      row(t('label.report'), safe(job.report_id), job.report_id ? 'OK' : 'HOLD')
    ].join('');
  }
}

async function pageChain() {
  await loadBaseStatus();
  const job = await loadLatestJob();
  renderProgrammedChain(job);
  const output = document.getElementById('chainOutput');
  if (output) {
    const rowData = firstSuccess(job);
    const snap = rowData?.result_snapshot || {};
    output.innerHTML = [
      row(t('label.vehicle'), `${safe(rowData?.vehicle_id)} / ${safe(rowData?.operation_date)}`, 'OK'),
      row(t('label.driverRevenue'), `${safe(rowData?.driver_id)} / ${fmt.format(Number(rowData?.raw_row?.daily_revenue || 0))}${t('label.koreanWon')}`, 'OK'),
      row(t('label.distancePassenger'), `${snap.distance_km ?? rowData?.raw_row?.distance_km ?? '-'}km / ${snap.passenger_count ?? rowData?.raw_row?.passenger_count ?? '-'}`, 'OK'),
      row(t('label.reduction'), snap.reduction_co2e == null ? '-' : `${Number(snap.reduction_co2e).toFixed(3)} kgCO2e`, 'OK'),
      row(t('label.estimatedValue'), krw.format(snap.estimated_value_krw || 0), 'OK'),
      row(t('label.report'), safe(job.report_id), job.report_id ? 'OK' : 'HOLD')
    ].join('');
  }
}

async function pageTrace() {
  await loadBaseStatus();
  renderFullTrace(await loadFullTraceFromLatest());
}

async function pageOps() {
  await loadBaseStatus();
  const [ops, production, ownership] = await Promise.all([
    get('/api/v1/ops/root-cause/summary'),
    get('/api/v1/production/dashboard'),
    get('/api/v1/assets/ownership/summary')
  ]);
  text('opsFailed', fmt.format(ops.failed_rows || 0));
  text('opsTopReason', (ops.top_10_reason_codes || [])[0]?.reason_code || '-');
  text('opsDlq', fmt.format(ops.dead_letter_count || 0));
  text('prodStatus', statusLabel(production.production_status || '-'));
  text('prodSla', statusLabel(production.sla?.sla_status || '-'));
  text('prodReady', `${Number(production.production_readiness?.readiness_score || 0).toFixed(1)}%`);
  text('ownerAssets', fmt.format(ownership.asset_count || 0));
  text('ownerEntity', Object.keys(ownership.owners || {}).join(', ') || '-');
  const output = document.getElementById('opsOutput');
  if (output) {
    const blocking = production.production_readiness?.blocking_checks || [];
    output.innerHTML = [
      row(t('label.rootCause'), Number(ops.failed_rows || 0) === 0 ? '0' : `${ops.failed_rows}`, Number(ops.failed_rows || 0) === 0 ? 'OK' : 'HOLD'),
      row(t('label.sla'), statusLabel(production.sla?.sla_status || '-'), production.sla?.sla_status === 'GREEN' ? 'OK' : 'HOLD'),
      row(t('label.readinessScore'), `${Number(production.production_readiness?.readiness_score || 0).toFixed(1)}%`, Number(production.production_readiness?.readiness_score || 0) >= 80 ? 'OK' : 'HOLD'),
      row(t('label.blockingChecks'), blocking.length ? blocking.map(item => item.category).join(', ') : '0', blocking.length ? 'HOLD' : 'OK'),
      row(t('label.ownedAssets'), `${fmt.format(ownership.asset_count || 0)} ${t('label.assetsUnit')} / ${Object.keys(ownership.owners || {}).join(', ') || '-'}`, 'OK')
    ].join('');
  }
}

async function pageCustomer2() {
  await loadBaseStatus();
  const [partner, portfolio, auth, ko, en, th, vi, zh] = await Promise.all([
    get('/api/v1/partners/ANSAN_TRANS/dashboard'),
    get('/api/v1/portfolio/kpi'),
    get('/api/v1/auth/summary'),
    get('/api/v1/localization/status/ko-KR'),
    get('/api/v1/localization/status/en-US'),
    get('/api/v1/localization/status/th-TH'),
    get('/api/v1/localization/status/vi-VN'),
    get('/api/v1/localization/status/zh-CN')
  ]);
  text('partnerStatus', statusLabel(partner.health?.api_status || '-'));
  text('partnerVerification', `${Number(partner.health?.verification_pass_rate || 0).toFixed(1)}%`);
  text('fleetTarget', portfolio.executive_summary?.fleet_size || '-');
  text('assetTarget', portfolio.executive_summary?.asset_creation || '-');
  text('valueTarget', portfolio.executive_summary?.portfolio_value || '-');
  const output = document.getElementById('customer2Output');
  if (output) {
    output.innerHTML = [
      row(t('label.partnerConnection'), statusLabel(partner.health?.api_status || '-'), partner.health?.api_status === 'CONNECTED' ? 'OK' : 'HOLD'),
      row(t('label.dataReceived'), partner.health?.last_data_received_at ? partner.health.last_data_received_at.slice(0, 19) : '-', partner.health?.last_data_received_at ? 'OK' : 'HOLD'),
      row(t('label.mappingErrors'), fmt.format(partner.health?.mapping_error_count || 0), Number(partner.health?.mapping_error_count || 0) === 0 ? 'OK' : 'HOLD'),
      row(t('label.verificationPass'), `${Number(partner.health?.verification_pass_rate || 0).toFixed(1)}%`, Number(partner.health?.verification_pass_rate || 0) >= 95 ? 'OK' : 'HOLD'),
      row(t('label.fleetProgress'), portfolio.executive_summary?.fleet_size || '-', 'OK'),
      row(t('label.assetProgress'), portfolio.executive_summary?.asset_creation || '-', 'OK'),
      row(t('label.portfolioValue'), portfolio.executive_summary?.portfolio_value || '-', 'OK')
    ].join('');
  }
  text('authPartnerAccounts', fmt.format(auth.partner_accounts?.length || 0));
  text('authReferralAccounts', fmt.format(auth.referral_accounts?.length || 0));
  text('authAuditCount', fmt.format(auth.audit_log_count || 0));
  text('authLockRule', t('auth.lockRule'));
  const authOutput = document.getElementById('authPermissionOutput');
  if (authOutput) {
    authOutput.innerHTML = [
      row(t('label.partnerLogin'), t('text.partnerLoginRoles'), 'OK'),
      row(t('label.referralLogin'), t('text.referralLoginRoles'), 'OK'),
      row(t('label.crossAccess'), t('text.crossAccess'), 'OK'),
      row(t('label.passwordStorage'), t('text.passwordStorage'), 'OK'),
      row(t('label.auditLogging'), t('text.auditLogging'), 'OK')
    ].join('');
  }
  const languageMap = [
    ['langKo', ko],
    ['langEn', en],
    ['langTh', th],
    ['langVi', vi],
    ['langZh', zh]
  ];
  for (const [id, status] of languageMap) {
    text(id, `${Number(status.coverage_pct || 0).toFixed(0)}%`);
    setClass(id, `value small ${status.production_ready ? 'mint' : 'amber'}`);
  }
  const languageOutput = document.getElementById('languageReviewOutput');
  if (languageOutput) {
    languageOutput.innerHTML = [
      row(t('label.productionExposure'), t('text.productionExposure'), 'OK'),
      row(t('label.fallbackRule'), t('text.fallbackRule'), 'OK'),
      row(t('label.legalReview'), t('text.legalReview'), 'OK'),
      row(t('label.sensitiveTerms'), t('text.sensitiveTerms'), 'OK'),
      row(t('label.coverage'), `ko ${ko.coverage_pct}% · en ${en.coverage_pct}% · th ${th.coverage_pct}% · vi ${vi.coverage_pct}% · zh ${zh.coverage_pct}%`, [ko, en, th, vi, zh].every(item => item.production_ready) ? 'OK' : 'HOLD')
    ].join('');
  }
  renderPartnerCodeList(await partnerCodeRowsFromApi(), 'customer2PartnerCodes');
  renderReferralCodeList(await referralCodeRowsFromApi(), 'customer2ReferralCodes');
}

function partnerCodeRows() {
  return [
    {
      partner_code: 'ANSAN_TRANS',
      partner_name: '안산교통',
      partner_type: 'TAXI_FLEET',
      tenant_id: 'TENANT-ANSAN-001',
      contract_status: 'ACTIVE',
      service_scope: 'TAXI_MRV',
      sub_unit_code: 'ANSAN_GARAGE_01',
      sub_unit_name: '안산 1차고지',
      status: 'ACTIVE'
    },
    {
      partner_code: 'BUSAN_TAXI',
      partner_name: '부산택시 파일럿',
      partner_type: 'TAXI_FLEET',
      tenant_id: 'TENANT-BUSAN-001',
      contract_status: 'ONBOARDING',
      service_scope: 'TAXI_MRV',
      sub_unit_code: 'BUSAN_GARAGE_01',
      sub_unit_name: '부산 1차고지',
      status: 'ONBOARDING'
    },
    {
      partner_code: 'ZENOV_CHARGING_01',
      partner_name: 'Zenov Charging Partner',
      partner_type: 'CHARGING_OPERATOR',
      tenant_id: 'TENANT-CHARGING-001',
      contract_status: 'PILOT',
      service_scope: 'CHARGING_MRV',
      sub_unit_code: 'CHG_SITE_01',
      sub_unit_name: '1호 충전소',
      status: 'PILOT'
    }
  ];
}

async function partnerCodeRowsFromApi() {
  try {
    const result = await get('/api/v1/partner-codes/list');
    return result.items || [];
  } catch {
    return partnerCodeRows();
  }
}

function referralCodeRows() {
  return [
    {
      referral_code: 'BEN-REF-001',
      owner_type: 'SALES_MANAGER',
      owner_id: 'USR-BEN-001',
      owner_name: 'Ben',
      linked_partner_code: 'ANSAN_TRANS',
      linked_sub_unit_code: 'ANSAN_GARAGE_01',
      reward_policy_id: 'REF-TAXI-001',
      referral_status: 'ACTIVE',
      status: 'ACTIVE'
    },
    {
      referral_code: 'DRV-REF-ANSAN-001',
      owner_type: 'DRIVER',
      owner_id: 'DRV-KR-000001',
      owner_name: '안산 기사 001',
      linked_partner_code: 'ANSAN_TRANS',
      linked_sub_unit_code: 'ANSAN_GARAGE_01',
      reward_policy_id: 'REF-DRIVER-001',
      referral_status: 'ACTIVE',
      status: 'ACTIVE'
    },
    {
      referral_code: 'PARTNER-REF-BUSAN-001',
      owner_type: 'PARTNER_MANAGER',
      owner_id: 'USR-BUSAN-PM-001',
      owner_name: '부산 파트너 담당자',
      linked_partner_code: 'BUSAN_TAXI',
      linked_sub_unit_code: 'BUSAN_GARAGE_01',
      reward_policy_id: 'REF-PARTNER-001',
      referral_status: 'READY',
      status: 'READY'
    }
  ];
}

async function referralCodeRowsFromApi() {
  try {
    const result = await get('/api/v1/referral-codes/list');
    return result.items || [];
  } catch {
    return referralCodeRows();
  }
}

function renderCodeTable(targetId, rows, columns) {
  const target = document.getElementById(targetId);
  if (!target) return;
  target.innerHTML = rows.map(item => (
    `<div class="summary-row">
      <span class="label">${safe(item[columns[0]])}</span>
      <strong>${columns.slice(1, -1).map(col => `${col}: ${safe(item[col])}`).join(' · ')}</strong>
      <span class="pill ${item.status === 'ACTIVE' ? 'mint' : 'amber'}">${safe(statusLabel(item[columns[columns.length - 1]]))}</span>
    </div>`
  )).join('');
}

function partnerTypeLabel(type) {
  if (!type) return '-';
  const key = `label.partnerType.${type}`;
  const translated = t(key);
  return translated === key ? type : translated;
}

function ownerTypeLabel(type) {
  if (!type) return '-';
  const key = `label.ownerType.${type}`;
  const translated = t(key);
  return translated === key ? type : translated;
}

function serviceScopeLabel(scope) {
  if (!scope) return '-';
  const key = `label.serviceScope.${scope}`;
  const translated = t(key);
  return translated === key ? statusLabel(scope) : translated;
}

function domainLabel(domain) {
  if (!domain) return '-';
  const key = `domain.${domain}`;
  const translated = t(key);
  return translated === key ? domain : translated;
}

function actionLabel(actionId, fallback, field) {
  if (!actionId) return fallback || '-';
  const key = `action.${actionId}.${field}`;
  const translated = t(key);
  return translated === key ? fallback || '-' : translated;
}

function renderPartnerCodeList(rows, targetId = 'partnerCodeList') {
  const target = document.getElementById(targetId);
  if (!target) return;
  target.innerHTML = rows.map(item => (
    `<div class="summary-row">
      <span class="label">${safe(item.partner_code)}</span>
      <strong>${safe(item.partner_name)} · ${safe(partnerTypeLabel(item.partner_type || 'TAXI_FLEET'))} · ${safe(item.tenant_id)} · ${safe(t('label.serviceScope'))}: ${safe(serviceScopeLabel(item.service_scope || item.contract_status))} · ${safe(t('label.garage'))}: ${safe(item.sub_unit_name || item.sub_unit_code)}</strong>
      <span class="pill ${item.status === 'ACTIVE' ? 'mint' : 'amber'}">${safe(statusLabel(item.status))}</span>
    </div>`
  )).join('');
}

function renderReferralCodeList(rows, targetId = 'referralCodeList') {
  const target = document.getElementById(targetId);
  if (!target) return;
  target.innerHTML = rows.map(item => (
    `<div class="summary-row">
      <span class="label">${safe(t('label.referralCode'))}: ${safe(item.referral_code)}</span>
      <strong>${safe(t('field.ownerName'))}: ${safe(item.owner_name)} · ${safe(t('field.ownerType'))}: ${safe(ownerTypeLabel(item.owner_type))} · ${safe(t('label.linkedPartner'))}: ${safe(item.linked_partner_code)} · ${safe(t('label.garage'))}: ${safe(item.linked_sub_unit_code)} · ${safe(t('label.rewardPolicy'))}: ${safe(item.reward_policy_id)}</strong>
      <span class="pill ${item.status === 'ACTIVE' ? 'mint' : 'amber'}">${safe(statusLabel(item.status))}</span>
    </div>`
  )).join('');
}

async function pagePartnerCodes() {
  await loadBaseStatus();
  const rows = await partnerCodeRowsFromApi();
  text('partnerCodeCount', fmt.format(rows.length));
  text('partnerActiveCount', fmt.format(rows.filter(item => item.status === 'ACTIVE').length));
  text('partnerTenantCount', fmt.format(new Set(rows.map(item => item.tenant_id)).size));
  text('partnerScopeCount', fmt.format(new Set(rows.map(item => item.service_scope || item.contract_status)).size));
  renderPartnerCodeList(rows);
  text('partnerCodeRule', t('partner.rule'));
  bindPartnerCodeForms();
}

async function pageReferralCodes() {
  await loadBaseStatus();
  const rows = await referralCodeRowsFromApi();
  text('referralCodeCount', fmt.format(rows.length));
  text('referralActiveCount', fmt.format(rows.filter(item => item.status === 'ACTIVE').length));
  text('linkedPartnerCount', fmt.format(new Set(rows.map(item => item.linked_partner_code)).size));
  text('rewardPolicyCount', fmt.format(new Set(rows.map(item => item.reward_policy_id)).size));
  renderReferralCodeList(rows);
  text('referralCodeRule', t('referral.rule'));
  bindReferralCodeForms();
}

async function pagePartnerFolder() {
  await loadBaseStatus();
  const partnerRows = await partnerCodeRowsFromApi();
  const referralRows = await referralCodeRowsFromApi();
  text('partnerCodeCount', fmt.format(partnerRows.length));
  text('partnerActiveCount', fmt.format(partnerRows.filter(item => item.status === 'ACTIVE').length));
  text('partnerTenantCount', fmt.format(new Set(partnerRows.map(item => item.tenant_id)).size));
  text('partnerScopeCount', fmt.format(new Set(partnerRows.map(item => item.service_scope || item.contract_status)).size));
  renderPartnerCodeList(partnerRows);
  text('partnerCodeRule', 'Partner Code는 회사/기관/Tenant 기준이며 Referral Code와 분리 저장됩니다.');

  text('referralCodeCount', fmt.format(referralRows.length));
  text('referralActiveCount', fmt.format(referralRows.filter(item => item.status === 'ACTIVE').length));
  text('linkedPartnerCount', fmt.format(new Set(referralRows.map(item => item.linked_partner_code)).size));
  text('rewardPolicyCount', fmt.format(new Set(referralRows.map(item => item.reward_policy_id)).size));
  renderReferralCodeList(referralRows);
  text('referralCodeRule', 'Referral Code는 개인/추천/이벤트 기준이며 linked_partner_code로만 Partner Code와 연결됩니다.');

  bindPartnerCodeForms();
  bindReferralCodeForms();
}

function bindPartnerCodeForms() {
  const createButton = document.getElementById('partnerCreateButton');
  if (createButton && !createButton.dataset.bound) {
    createButton.dataset.bound = 'true';
    createButton.addEventListener('click', async () => {
      try {
        const result = await post('/api/v1/partner-codes/create', {
          partner_code: inputValue('partnerCreateCode'),
          partner_name: inputValue('partnerCreateName'),
          password: inputValue('partnerCreatePassword'),
          tenant_id: inputValue('partnerCreateTenant'),
          sub_unit_code: inputValue('partnerCreateSubUnit'),
          status: inputValue('partnerCreateStatus') || 'ACTIVE'
        });
        setNotice('partnerCreateResult', `${t('partner.saved')}: ${result.partner_code.partner_code} / access_password_hash ${result.partner_code.access_password_hash_present ? t('label.yes') : t('label.no')}`, 'OK');
        const rows = await partnerCodeRowsFromApi();
        renderPartnerCodeList(rows);
        text('partnerCodeCount', fmt.format(rows.length));
        text('partnerActiveCount', fmt.format(rows.filter(item => item.status === 'ACTIVE').length));
      } catch (err) {
        setNotice('partnerCreateResult', `${t('partner.saveFailed')}: ${err.message}`, 'FAIL');
      }
    });
  }
  const verifyButton = document.getElementById('partnerVerifyButton');
  if (verifyButton && !verifyButton.dataset.bound) {
    verifyButton.dataset.bound = 'true';
    verifyButton.addEventListener('click', async () => {
      try {
        const result = await post('/api/v1/partner-codes/verify', {
          partner_code: inputValue('partnerVerifyCode'),
          password: inputValue('partnerVerifyPassword')
        });
        setNotice('partnerVerifyResult', `${t('partner.verified')}: ${result.partner_code.partner_code} / ${statusLabel(result.partner_code.status)}`, 'OK');
      } catch (err) {
        setNotice('partnerVerifyResult', `${t('partner.verifyFailed')}: ${err.message}`, 'FAIL');
      }
    });
  }
  const updateButton = document.getElementById('partnerUpdateButton');
  if (updateButton && !updateButton.dataset.bound) {
    updateButton.dataset.bound = 'true';
    updateButton.addEventListener('click', async () => {
      try {
        const result = await post('/api/v1/partner-codes/update', {
          partner_code: inputValue('partnerUpdateCode'),
          partner_name: inputValue('partnerUpdateName'),
          tenant_id: inputValue('partnerUpdateTenant'),
          sub_unit_code: inputValue('partnerUpdateSubUnit'),
          contract_status: inputValue('partnerUpdateContract'),
          status: inputValue('partnerUpdateStatus')
        });
        setNotice('partnerUpdateResult', `${t('partner.updated')}: ${result.partner_code.partner_code} / ${statusLabel(result.partner_code.contract_status)}`, 'OK');
        renderPartnerCodeList(await partnerCodeRowsFromApi());
      } catch (err) {
        setNotice('partnerUpdateResult', `${t('partner.updateFailed')}: ${err.message}`, 'FAIL');
      }
    });
  }
  const disableButton = document.getElementById('partnerDisableButton');
  if (disableButton && !disableButton.dataset.bound) {
    disableButton.dataset.bound = 'true';
    disableButton.addEventListener('click', async () => {
      try {
        const result = await post('/api/v1/partner-codes/disable', {
          partner_code: inputValue('partnerDisableCode')
        });
        setNotice('partnerDisableResult', `${t('partner.disabled')}: ${result.partner_code.partner_code} / ${statusLabel(result.partner_code.status)}`, 'OK');
        renderPartnerCodeList(await partnerCodeRowsFromApi());
      } catch (err) {
        setNotice('partnerDisableResult', `${t('partner.disableFailed')}: ${err.message}`, 'FAIL');
      }
    });
  }
}

function bindReferralCodeForms() {
  const createButton = document.getElementById('referralCreateButton');
  if (createButton && !createButton.dataset.bound) {
    createButton.dataset.bound = 'true';
    createButton.addEventListener('click', async () => {
      try {
        const result = await post('/api/v1/referral-codes/create', {
          referral_code: inputValue('referralCreateCode'),
          owner_type: inputValue('referralCreateOwnerType') || 'INDIVIDUAL',
          owner_name: inputValue('referralCreateOwner'),
          password: inputValue('referralCreatePassword'),
          linked_partner_code: inputValue('referralCreatePartner'),
          linked_sub_unit_code: inputValue('referralCreateSubUnit'),
          reward_policy_id: inputValue('referralCreateReward'),
          status: inputValue('referralCreateStatus') || 'ACTIVE'
        });
        setNotice('referralCreateResult', `${t('referral.saved')}: ${result.referral_code.referral_code} / ${result.referral_code.linked_partner_code}`, 'OK');
        const rows = await referralCodeRowsFromApi();
        renderReferralCodeList(rows);
        text('referralCodeCount', fmt.format(rows.length));
        text('referralActiveCount', fmt.format(rows.filter(item => item.status === 'ACTIVE').length));
      } catch (err) {
        setNotice('referralCreateResult', `${t('referral.saveFailed')}: ${err.message}`, 'FAIL');
      }
    });
  }
  const verifyButton = document.getElementById('referralVerifyButton');
  if (verifyButton && !verifyButton.dataset.bound) {
    verifyButton.dataset.bound = 'true';
    verifyButton.addEventListener('click', async () => {
      try {
        const result = await post('/api/v1/referral-codes/verify', {
          referral_code: inputValue('referralVerifyCode'),
          password: inputValue('referralVerifyPassword')
        });
        setNotice('referralVerifyResult', `${t('referral.verified')}: ${result.referral_code.referral_code} / ${statusLabel(result.referral_code.status)}`, 'OK');
      } catch (err) {
        setNotice('referralVerifyResult', `${t('referral.verifyFailed')}: ${err.message}`, 'FAIL');
      }
    });
  }
  const updateButton = document.getElementById('referralUpdateButton');
  if (updateButton && !updateButton.dataset.bound) {
    updateButton.dataset.bound = 'true';
    updateButton.addEventListener('click', async () => {
      try {
        const result = await post('/api/v1/referral-codes/update', {
          referral_code: inputValue('referralUpdateCode'),
          owner_name: inputValue('referralUpdateOwner'),
          owner_type: inputValue('referralUpdateOwnerType'),
          linked_partner_code: inputValue('referralUpdatePartner'),
          linked_sub_unit_code: inputValue('referralUpdateSubUnit'),
          reward_policy_id: inputValue('referralUpdateReward'),
          status: inputValue('referralUpdateStatus')
        });
        setNotice('referralUpdateResult', `${t('referral.updated')}: ${result.referral_code.referral_code} / ${result.referral_code.linked_partner_code}`, 'OK');
        renderReferralCodeList(await referralCodeRowsFromApi());
      } catch (err) {
        setNotice('referralUpdateResult', `${t('referral.updateFailed')}: ${err.message}`, 'FAIL');
      }
    });
  }
  const disableButton = document.getElementById('referralDisableButton');
  if (disableButton && !disableButton.dataset.bound) {
    disableButton.dataset.bound = 'true';
    disableButton.addEventListener('click', async () => {
      try {
        const result = await post('/api/v1/referral-codes/disable', {
          referral_code: inputValue('referralDisableCode')
        });
        setNotice('referralDisableResult', `${t('referral.disabled')}: ${result.referral_code.referral_code} / ${statusLabel(result.referral_code.status)}`, 'OK');
        renderReferralCodeList(await referralCodeRowsFromApi());
      } catch (err) {
        setNotice('referralDisableResult', `${t('referral.disableFailed')}: ${err.message}`, 'FAIL');
      }
    });
  }
}

async function pageIntelligence() {
  await loadBaseStatus();
  const result = await post('/api/v1/navigation-carbon/predict', {
    source_type: 'EV_TAXI',
    vehicle_id: 'VEH-KR-TAXI-001',
    speed_series: [35, 42, 38, 44, 40],
    time_interval_seconds: 60,
    energy_consumed_kwh: 1.0,
    solar_used_kwh: 1.2,
    remaining_distance_km: 20
  });
  text('navDistance', `${Number(result.distance_km || 0).toFixed(2)} km`);
  text('navSpeed', `${Number(result.average_speed_kmh || 0).toFixed(1)} km/h`);
  text('navEta', result.eta_minutes == null ? '-' : `${Number(result.eta_minutes).toFixed(1)} min`);
  text('navReduction', `${Number(result.total_reduction_kgco2e || 0).toFixed(3)} kgCO2e`);
  text('navValue', krw.format(Number(result.estimated_value || 0)));
  const output = document.getElementById('navigationMrvOutput');
  if (output) {
    output.innerHTML = [
      row(t('label.pattern'), result.pattern || '-', 'OK'),
      row(t('label.movementCalculation'), result.movement_calculation || '-', 'OK'),
      row(t('label.mobilityReduction'), `${Number(result.mobility_reduction_kgco2e || 0).toFixed(3)} kgCO2e`, Number(result.mobility_reduction_kgco2e || 0) >= 0 ? 'OK' : 'HOLD'),
      row(t('label.solarReduction'), `${Number(result.solar_reduction_kgco2e || 0).toFixed(3)} kgCO2e`, 'OK'),
      row(t('label.methodology'), result.methodology_version || '-', 'OK')
    ].join('');
  }
  const modules = [
    ['module.trust', 'module.trustDesc'],
    ['module.evidence', 'module.evidenceDesc'],
    ['module.mrv', 'module.mrvDesc'],
    ['module.value', 'module.valueDesc'],
    ['module.registry', 'module.registryDesc'],
    ['module.forecast', 'module.forecastDesc'],
    ['module.optimization', 'module.optimizationDesc'],
    ['module.fleet', 'module.fleetDesc'],
    ['module.solarMatching', 'module.solarMatchingDesc'],
    ['module.trustScore', 'module.trustScoreDesc'],
    ['module.dailyAudit', 'module.dailyAuditDesc'],
    ['module.portfolio', 'module.portfolioDesc']
  ];
  const target = document.getElementById('intelligenceModules');
  if (target) {
    target.innerHTML = modules.map(([titleKey, descKey]) => (
      `<div class="card"><div class="label">${safe(t(titleKey))}</div><p>${safe(t(descKey))}</p></div>`
    )).join('');
  }
  const economicActions = document.getElementById('economicActionOutput');
  const economicTwin = document.getElementById('economicTwinOutput');
  if (economicActions || economicTwin) {
    const summary = await get('/api/v1/economic-decision/summary');
    text('ecoCharge', summary.energy_economics?.optimal_charge_window || '-');
    text('ecoSaving', krw.format(Number(summary.energy_economics?.estimated_daily_saving_krw || 0)));
    text('ecoYield', `${Number(summary.carbon_yield?.carbon_yield_pct || 0).toFixed(1)}%`);
    text('ecoOpportunity', Number(summary.opportunity?.opportunity_score || 0).toFixed(1));
    if (economicActions) {
      economicActions.innerHTML = (summary.recommended_actions || []).map(action => (
        row(
          domainLabel(action.domain),
          `${actionLabel(action.action_id, action.recommendation, 'recommendation')} / ${actionLabel(action.action_id, action.reason, 'reason')}`,
          Number(action.expected_saving_pct || action.expected_co2e_ton || 0) > 0 ? 'OK' : 'HOLD'
        )
      )).join('');
    }
    if (economicTwin) {
      economicTwin.innerHTML = [
        row(t('label.digitalTwin'), `${summary.digital_twin?.taxi || '-'} / ${summary.digital_twin?.solar || '-'} / ${summary.digital_twin?.ess || '-'}`, 'OK'),
        row(t('label.expectedReduction'), `${Number(summary.digital_twin?.expected_reduction_tco2e || 0).toFixed(3)} tCO2e`, 'OK'),
        row(t('label.cityValue'), krw.format(Number(summary.city_scale?.city_total_value_krw || 0)), 'OK'),
        row(t('label.payback'), `${Number(summary.carbon_yield?.payback_years || 0).toFixed(2)} y`, 'OK')
      ].join('');
    }
  }
}

async function pageFinance() {
  await loadBaseStatus();
  const summary = await get('/api/v1/carbon-finance/summary');
  text('financeAssetCount', fmt.format(summary.asset_count || 0));
  text('financeTotalCo2e', `${Number(summary.total_co2e || 0).toFixed(3)} tCO2e`);
  text('financeTotalValue', krw.format(Number(summary.total_fair_value_krw || 0)));
  text('financeAverageRating', summary.average_rating || '-');
  text('financeReadiness', statusLabel(summary.finance_readiness || '-'));
  const output = document.getElementById('financeOutput');
  if (output) {
    const first = (summary.assets || [])[0] || {};
    output.innerHTML = [
      row(t('label.asset'), first.asset_id || '-', 'OK'),
      row(t('label.assetRating'), `${first.rating || '-'} / ${Number(first.score || 0).toFixed(1)}`, 'OK'),
      row(t('label.assetRisk'), `${Number(first.risk_score || 0).toFixed(1)} / ${statusLabel(first.risk_status || '-')}`, Number(first.risk_score || 0) <= 20 ? 'OK' : 'HOLD'),
      row(t('label.fairValue'), krw.format(Number(first.fair_value_krw || 0)), 'OK'),
      row(t('label.financeReadiness'), statusLabel(first.finance_readiness || '-'), first.finance_readiness === 'INVESTABLE' ? 'OK' : 'HOLD')
    ].join('');
  }
  const forecast = document.getElementById('financeForecastOutput');
  if (forecast) {
    forecast.innerHTML = [
      row('30D', `${Number(summary.forecast?.['30d']?.expected_co2e || 0).toFixed(3)} tCO2e / ${krw.format(Number(summary.forecast?.['30d']?.expected_value_krw || 0))}`, 'OK'),
      row('90D', `${Number(summary.forecast?.['90d']?.expected_co2e || 0).toFixed(3)} tCO2e / ${krw.format(Number(summary.forecast?.['90d']?.expected_value_krw || 0))}`, 'OK'),
      row(t('label.opportunityScore'), `${Number(summary.opportunity?.opportunity_score || 0).toFixed(1)} / ${summary.opportunity?.scenario || '-'}`, Number(summary.opportunity?.opportunity_score || 0) >= 80 ? 'OK' : 'HOLD'),
      row(t('label.marketplaceReadiness'), statusLabel(summary.marketplace_readiness?.market_status || '-'), 'HOLD')
    ].join('');
  }
}

async function pageEconomic() {
  await loadBaseStatus();
  const summary = await get('/api/v1/economic-decision/summary');
  text('ecoCharge', summary.energy_economics?.optimal_charge_window || '-');
  text('ecoSaving', krw.format(Number(summary.energy_economics?.estimated_daily_saving_krw || 0)));
  text('ecoYield', `${Number(summary.carbon_yield?.carbon_yield_pct || 0).toFixed(1)}%`);
  text('ecoOpportunity', Number(summary.opportunity?.opportunity_score || 0).toFixed(1));
  text('ecoCityRoi', `${Number(summary.city_scale?.city_roi_pct || 0).toFixed(1)}%`);
  const actions = document.getElementById('economicActionOutput');
  if (actions) {
    actions.innerHTML = (summary.recommended_actions || []).map(action => (
      row(
        domainLabel(action.domain),
        `${actionLabel(action.action_id, action.recommendation, 'recommendation')} / ${actionLabel(action.action_id, action.reason, 'reason')}`,
        Number(action.expected_saving_pct || action.expected_co2e_ton || 0) > 0 ? 'OK' : 'HOLD'
      )
    )).join('');
  }
  const twin = document.getElementById('economicTwinOutput');
  if (twin) {
    twin.innerHTML = [
      row(t('label.digitalTwin'), `${summary.digital_twin?.taxi || '-'} / ${summary.digital_twin?.solar || '-'} / ${summary.digital_twin?.ess || '-'}`, 'OK'),
      row(t('label.expectedReduction'), `${Number(summary.digital_twin?.expected_reduction_tco2e || 0).toFixed(3)} tCO2e`, 'OK'),
      row(t('label.cityValue'), krw.format(Number(summary.city_scale?.city_total_value_krw || 0)), 'OK'),
      row(t('label.payback'), `${Number(summary.carbon_yield?.payback_years || 0).toFixed(2)} y`, 'OK')
    ].join('');
  }
}

window.ZenovApp = {
  pageHome,
  pageProjectFactory,
  pageDataCollection,
  pageTrustEvidence,
  pageMrvCenter,
  pageCarbonValue,
  pageRegistry,
  pageVerification,
  pageCustomerZero,
  pageChain,
  pageTrace,
  pageOps,
  pageCustomer2,
  pagePartnerCodes,
  pagePartnerFolder,
  pageReferralCodes,
  pageIntelligence,
  pageFinance,
  pageEconomic,
  pageDigitalTwin,
  pageDealRoom,
  pageMarketplace,
  pageEcosystem,
  pageCompliance,
  pageEducation
};
