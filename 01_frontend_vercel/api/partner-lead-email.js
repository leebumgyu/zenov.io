const DEFAULT_RECIPIENTS = ['contact@zenov.io', 'zenovou@gmail.com'];

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

function row(label, value) {
  return `<tr><td style="padding:8px 10px;border-bottom:1px solid #e7edf3;color:#64748b;width:190px;">${label}</td><td style="padding:8px 10px;border-bottom:1px solid #e7edf3;color:#111827;font-weight:600;">${value || '-'}</td></tr>`;
}

function buildEmailHtml(partner) {
  const mobility = partner.mobility || {};
  const energy = partner.energy || {};
  const cost = partner.cost_structure || {};
  const opportunity = partner.opportunity || {};
  const goals = partner.business_goals || {};
  const data = partner.data_status || {};
  const analysis = partner.partner_analysis || partner.sales_automation || {};

  return `
    <div style="font-family:Arial, sans-serif;background:#f8fafc;padding:24px;">
      <div style="max-width:720px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
        <div style="background:#07111f;color:#ffffff;padding:22px 24px;">
          <div style="font-size:12px;letter-spacing:1.5px;color:#67e8f9;">ZENOV SMART ESG DIAGNOSIS</div>
          <h1 style="margin:8px 0 0;font-size:22px;">새 파트너 가입 및 분석 요청</h1>
        </div>
        <div style="padding:22px 24px;">
          <h2 style="font-size:16px;margin:0 0 10px;">회사 정보</h2>
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
            ${row('저장 시각', clean(partner.updated_at || partner.created_at || new Date().toISOString()))}
          </table>

          <p style="margin-top:24px;color:#64748b;font-size:12px;line-height:1.6;">
            이 메일은 Zenov 파트너 가입 및 분석 화면에서 자동 발송되었습니다.
          </p>
        </div>
      </div>
    </div>
  `;
}

function buildText(partner) {
  const mobility = partner.mobility || {};
  const energy = partner.energy || {};
  const opportunity = partner.opportunity || {};
  return [
    '[ZENOV] 새 파트너 가입 및 분석 요청',
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

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return json(res, 405, { ok: false, error: 'METHOD_NOT_ALLOWED' });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    return json(res, 503, {
      ok: false,
      error: 'EMAIL_PROVIDER_NOT_CONFIGURED',
      message: 'Set RESEND_API_KEY in Vercel environment variables.'
    });
  }

  let body = {};
  try {
    body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  } catch {
    return json(res, 400, { ok: false, error: 'INVALID_JSON' });
  }

  const partner = body.partner || body;
  const companyName = clean(partner.company_name) || clean(partner.partner_id) || 'New Partner';
  const recipients = clean(process.env.ZENOV_LEAD_EMAILS)
    ? clean(process.env.ZENOV_LEAD_EMAILS).split(',').map((item) => item.trim()).filter(Boolean)
    : DEFAULT_RECIPIENTS;

  const emailPayload = {
    from: process.env.ZENOV_EMAIL_FROM || 'Zenov Platform <onboarding@resend.dev>',
    to: recipients,
    subject: `[ZENOV] 새 파트너 가입 및 분석 요청 - ${companyName}`,
    html: buildEmailHtml(partner),
    text: buildText(partner)
  };

  try {
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
      return json(res, response.status, { ok: false, error: 'EMAIL_SEND_FAILED', detail: result });
    }
    return json(res, 200, { ok: true, recipients, id: result.id || null });
  } catch (error) {
    return json(res, 500, { ok: false, error: 'EMAIL_SEND_FAILED', message: error.message });
  }
};
