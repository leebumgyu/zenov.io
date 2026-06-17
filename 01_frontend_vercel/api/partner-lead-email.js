const { neon } = require('@neondatabase/serverless');

const DEFAULT_RECIPIENTS = [
  'ganztaic@gmail.com',
  'contact@zenov.io',
  'zenovou@gmail.com'
];

function json(res, statusCode, payload) {
  res.statusCode = statusCode;
  res.setHeader('content-type', 'application/json; charset=utf-8');
  res.end(JSON.stringify(payload));
}

function clean(value) {
  return String(value ?? '').trim();
}

function number(value) {
  const parsed = Number(value || 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatKrw(value) {
  return `${number(value).toLocaleString('ko-KR')} KRW`;
}

function newLeadId() {
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14);
  const random = Math.random().toString(36).slice(2, 8).toUpperCase();
  return `LEAD-${stamp}-${random}`;
}

function row(label, value) {
  return `<tr><td style="padding:8px 10px;border-bottom:1px solid #e7edf3;color:#64748b;width:190px;">${label}</td><td style="padding:8px 10px;border-bottom:1px solid #e7edf3;color:#111827;font-weight:600;">${value || '-'}</td></tr>`;
}

function normalizePartner(payload) {
  const partner = payload.partner || payload;
  return {
    ...partner,
    partner_id: clean(partner.partner_id || partner.partner_code),
    company_name: clean(partner.company_name),
    ceo_name: clean(partner.ceo_name),
    contact_name: clean(partner.contact_name),
    contact_phone: clean(partner.contact_phone),
    contact_email: clean(partner.contact_email),
    region: clean(partner.region),
    business_type: clean(partner.business_type),
    status: clean(partner.status) || 'NEW',
    updated_at: clean(partner.updated_at) || new Date().toISOString()
  };
}

function getSql() {
  const databaseUrl = clean(process.env.DATABASE_URL);
  if (!databaseUrl) {
    throw new Error('DATABASE_URL_NOT_CONFIGURED');
  }
  return neon(databaseUrl);
}

async function ensurePartnerLeadsTable(sql) {
  await sql`
    CREATE TABLE IF NOT EXISTS partner_leads (
      id TEXT PRIMARY KEY,
      partner_id TEXT,
      company_name TEXT,
      ceo_name TEXT,
      contact_name TEXT,
      contact_phone TEXT,
      contact_email TEXT,
      region TEXT,
      business_type TEXT,
      status TEXT,
      raw_payload JSONB NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  `;
  await sql`CREATE INDEX IF NOT EXISTS idx_partner_leads_created_at ON partner_leads (created_at DESC)`;
  await sql`CREATE INDEX IF NOT EXISTS idx_partner_leads_partner_id ON partner_leads (partner_id)`;
}

async function savePartnerLead(partner, rawPayload) {
  const sql = getSql();
  const leadId = newLeadId();
  await ensurePartnerLeadsTable(sql);
  await sql`
    INSERT INTO partner_leads (
      id,
      partner_id,
      company_name,
      ceo_name,
      contact_name,
      contact_phone,
      contact_email,
      region,
      business_type,
      status,
      raw_payload
    )
    VALUES (
      ${leadId},
      ${partner.partner_id},
      ${partner.company_name},
      ${partner.ceo_name},
      ${partner.contact_name},
      ${partner.contact_phone},
      ${partner.contact_email},
      ${partner.region},
      ${partner.business_type},
      ${partner.status},
      CAST(${JSON.stringify(rawPayload)} AS jsonb)
    )
  `;
  return leadId;
}

function buildEmailHtml(partner, leadId) {
  const mobility = partner.mobility || {};
  const energy = partner.energy || {};
  const cost = partner.cost_structure || {};
  const opportunity = partner.opportunity || {};
  const goals = partner.business_goals || {};
  const data = partner.data_status || {};

  return `
    <div style="font-family:Arial, sans-serif;background:#f8fafc;padding:24px;">
      <div style="max-width:720px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
        <div style="background:#07111f;color:#ffffff;padding:22px 24px;">
          <div style="font-size:12px;letter-spacing:1.5px;color:#67e8f9;">ZENOV SMART ESG DIAGNOSIS</div>
          <h1 style="margin:8px 0 0;font-size:22px;">새 파트너 가입 및 분석 요청</h1>
        </div>
        <div style="padding:22px 24px;">
          <h2 style="font-size:16px;margin:0 0 10px;">DB 저장 정보</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            ${row('Lead ID', clean(leadId))}
            ${row('저장 테이블', 'partner_leads')}
            ${row('저장 시각', clean(partner.updated_at || new Date().toISOString()))}
          </table>

          <h2 style="font-size:16px;margin:24px 0 10px;">회사 정보</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            ${row('파트너 코드', clean(partner.partner_id))}
            ${row('회사명', clean(partner.company_name))}
            ${row('대표자', clean(partner.ceo_name))}
            ${row('담당자', clean(partner.contact_name))}
            ${row('연락처', clean(partner.contact_phone))}
            ${row('이메일', clean(partner.contact_email))}
            ${row('지역', clean(partner.region))}
            ${row('사업유형', clean(partner.business_type))}
          </table>

          <h2 style="font-size:16px;margin:24px 0 10px;">운영 현황</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            ${row('보유 택시 수', number(mobility.taxi_count))}
            ${row('전기택시 수', number(mobility.ev_taxi_count))}
            ${row('보유 버스 수', number(mobility.bus_count))}
            ${row('전기버스 수', number(mobility.ev_bus_count))}
            ${row('태양광 설치 여부', clean(energy.solar_installed))}
            ${row('태양광 용량', `${number(energy.solar_capacity_kw)} kW`)}
            ${row('EV 충전기 상태', clean(energy.ev_charger_status))}
            ${row('EV 충전기 수', number(energy.charger_count))}
            ${row('완속 충전기', number(energy.slow_charger_count))}
            ${row('급속 충전기', number(energy.fast_charger_count))}
          </table>

          <h2 style="font-size:16px;margin:24px 0 10px;">비용 / 데이터 / 목표</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            ${row('차량 1대당 월 연료비 평균', formatKrw(cost.monthly_fuel_cost))}
            ${row('회사 월 전기 사용량', `${number(cost.company_monthly_electricity_usage).toLocaleString('ko-KR')} kWh`)}
            ${row('월 전기요금', formatKrw(cost.monthly_electricity_cost))}
            ${row('가장 부담되는 비용', clean(cost.biggest_cost_burden))}
            ${row('GPS 데이터', clean(data.gps_data_available))}
            ${row('충전 데이터', clean(data.charging_data_available))}
            ${row('전력 데이터', clean(data.power_data_available))}
            ${row('API 제공 가능', clean(data.api_available))}
            ${row('1년 목표', clean(goals.one_year_goal))}
            ${row('3년 목표', clean(goals.three_year_goal))}
            ${row('5년 목표', clean(goals.five_year_goal))}
          </table>

          <h2 style="font-size:16px;margin:24px 0 10px;">Zenov 자동 분석</h2>
          <table style="width:100%;border-collapse:collapse;font-size:14px;">
            ${row('추천 프로젝트', clean(opportunity.expected_project))}
            ${row('예상 CO2e', `${number(opportunity.estimated_co2e_ton)} tCO2e`)}
            ${row('예상 Carbon Value', formatKrw(opportunity.estimated_carbon_value_krw))}
            ${row('다음 액션', clean(opportunity.next_action))}
            ${row('분석 상태', clean(partner.status))}
          </table>

          <p style="margin-top:24px;color:#64748b;font-size:12px;line-height:1.6;">
            이 메일은 Zenov 파트너 가입 및 분석 화면에서 DB 저장 후 자동 발송되었습니다.
          </p>
        </div>
      </div>
    </div>
  `;
}

function buildText(partner, leadId) {
  const mobility = partner.mobility || {};
  const energy = partner.energy || {};
  const opportunity = partner.opportunity || {};
  return [
    '[ZENOV] 새 파트너 가입 및 분석 요청',
    '',
    `Lead ID: ${clean(leadId)}`,
    `저장 테이블: partner_leads`,
    '',
    `파트너 코드: ${clean(partner.partner_id)}`,
    `회사명: ${clean(partner.company_name)}`,
    `대표자: ${clean(partner.ceo_name)}`,
    `담당자: ${clean(partner.contact_name)}`,
    `연락처: ${clean(partner.contact_phone)}`,
    `이메일: ${clean(partner.contact_email)}`,
    `지역: ${clean(partner.region)}`,
    `사업유형: ${clean(partner.business_type)}`,
    '',
    `보유 택시 수: ${number(mobility.taxi_count)}`,
    `전기택시 수: ${number(mobility.ev_taxi_count)}`,
    `태양광: ${clean(energy.solar_installed)} / ${number(energy.solar_capacity_kw)} kW`,
    `EV 충전기: ${clean(energy.ev_charger_status)} / ${number(energy.charger_count)}기`,
    '',
    `추천 프로젝트: ${clean(opportunity.expected_project)}`,
    `예상 CO2e: ${number(opportunity.estimated_co2e_ton)} tCO2e`,
    `예상 Carbon Value: ${formatKrw(opportunity.estimated_carbon_value_krw)}`,
    `다음 액션: ${clean(opportunity.next_action)}`
  ].join('\n');
}

function emailRecipients() {
  const configured = clean(process.env.ZENOV_LEAD_EMAILS);
  return configured
    ? configured.split(',').map((item) => item.trim()).filter(Boolean)
    : DEFAULT_RECIPIENTS;
}

async function sendEmail(partner, leadId) {
  const apiKey = clean(process.env.RESEND_API_KEY);
  if (!apiKey) {
    throw new Error('EMAIL_PROVIDER_NOT_CONFIGURED');
  }

  const companyName = clean(partner.company_name) || clean(partner.partner_id) || 'New Partner';
  const emailPayload = {
    from: clean(process.env.ZENOV_EMAIL_FROM) || 'Zenov Platform <onboarding@resend.dev>',
    to: emailRecipients(),
    subject: `[ZENOV] 새 파트너 가입 및 분석 요청 - ${companyName}`,
    html: buildEmailHtml(partner, leadId),
    text: buildText(partner, leadId)
  };

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      authorization: `Bearer ${apiKey}`,
      'content-type': 'application/json'
    },
    body: JSON.stringify(emailPayload)
  });

  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error('EMAIL_SEND_FAILED');
    error.detail = result;
    error.statusCode = response.status;
    throw error;
  }

  return { recipients: emailPayload.to, id: result.id || null };
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return json(res, 405, { ok: false, error: 'METHOD_NOT_ALLOWED' });
  }

  let body = {};
  try {
    body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  } catch {
    return json(res, 400, { ok: false, saved: false, error: 'INVALID_JSON' });
  }

  const partner = normalizePartner(body);
  let leadId = null;

  try {
    leadId = await savePartnerLead(partner, body);
  } catch (error) {
    return json(res, 500, {
      ok: false,
      saved: false,
      error: 'DB_SAVE_FAILED',
      detail: clean(error.message)
    });
  }

  try {
    const email = await sendEmail(partner, leadId);
    return json(res, 200, {
      ok: true,
      saved: true,
      email_sent: true,
      lead_id: leadId,
      email
    });
  } catch (error) {
    return json(res, 502, {
      ok: false,
      saved: true,
      email_sent: false,
      error: 'EMAIL_SEND_FAILED',
      lead_id: leadId,
      detail: error.detail || clean(error.message)
    });
  }
};
