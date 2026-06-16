from collections import defaultdict

from .api_models import AuditEvent, RejectLog, StoredSensorPacket, TrustPacket


audit_events: dict[str, list[AuditEvent]] = defaultdict(list)
reject_logs: list[RejectLog] = []
trust_packets: dict[str, TrustPacket] = {}
sensor_packets: dict[str, StoredSensorPacket] = {}
source_sequences: dict[str, int] = {}
packet_hash_index: set[str] = set()
mrv_results: dict[str, dict] = {}
carbon_value_results: dict[str, dict] = {}
mrv_by_packet_id: dict[str, str] = {}
value_by_mrv_id: dict[str, str] = {}
digital_evidence: dict[str, dict] = {}
evidence_by_packet_id: dict[str, str] = {}
integrity_reports: dict[str, dict] = {}
integrity_report_by_evidence_id: dict[str, str] = {}
evidence_sensor_mappings: dict[str, dict] = {}
taxi_daily_operations: dict[str, dict] = {}
taxi_import_logs: list[dict] = []
green_point_ledger: list[dict] = []
driver_wallets: dict[str, dict] = {}
wallet_transactions: dict[str, dict] = {}
wallet_transactions_by_driver_id: dict[str, list[str]] = defaultdict(list)
import_jobs: dict[str, dict] = {}
import_job_rows: list[dict] = []
failed_import_rows: list[dict] = []
taxi_mrv_results: dict[str, dict] = {}
taxi_mrv_by_packet_id: dict[str, str] = {}
mrv_verification_records: dict[str, dict] = {}
verification_by_packet_id: dict[str, str] = {}
carbon_asset_candidates: dict[str, dict] = {}
carbon_asset_candidate_by_mrv_id: dict[str, str] = {}
mrv_reports: dict[str, dict] = {}
methodology_registry: dict[str, dict] = {}
methodology_snapshots: dict[str, dict] = {}
methodology_change_impacts: dict[str, dict] = {}
portfolio_targets: dict[str, dict] = {}
portfolio_kpi_snapshots: dict[str, dict] = {}
partner_api_keys: dict[str, dict] = {}
partners: dict[str, dict] = {}
partner_data_mappings: dict[str, dict] = {}
partner_integrations: dict[str, dict] = {}
partner_health_logs: list[dict] = []
partner_health: dict[str, dict] = {}
dead_letter_queue: dict[str, dict] = {}
tenants: dict[str, dict] = {}
tenant_users: dict[str, dict] = {}
tenant_subscriptions: dict[str, dict] = {}
billing_accounts: dict[str, dict] = {}
tenant_audit_logs: list[dict] = []
merchant_accounts: dict[str, dict] = {}
commission_rules: dict[str, dict] = {}
settlement_records: dict[str, dict] = {}
settlement_batches: dict[str, dict] = {}
settlement_ledger_entries: list[dict] = []
onboarding_projects: dict[str, dict] = {}
onboarding_checklists: dict[str, dict] = {}
deployment_templates: dict[str, dict] = {}
deployment_runs: dict[str, dict] = {}
customer_health_snapshots: dict[str, dict] = {}
production_readiness_checks: dict[str, dict] = {}
sla_snapshots: dict[str, dict] = {}
operational_runbooks: dict[str, dict] = {}
country_profiles: dict[str, dict] = {}
country_methodology_adapters: dict[str, dict] = {}
localized_report_templates: dict[str, dict] = {}
copilot_query_logs: list[dict] = []
audit_intelligence_explanations: dict[str, dict] = {}
evidence_explanations: dict[str, dict] = {}
asset_ownership_records: dict[str, dict] = {}
asset_custody_records: dict[str, dict] = {}
asset_transfer_records: dict[str, dict] = {}
asset_ownership_audit_logs: list[dict] = []
partner_auth_accounts: dict[str, dict] = {}
referral_auth_accounts: dict[str, dict] = {}
auth_sessions: dict[str, dict] = {}
auth_audit_logs: list[dict] = []
password_reset_tokens: dict[str, dict] = {}
translation_keys: dict[str, dict] = {}
translation_reviews: dict[str, dict] = {}
language_reviewers: dict[str, dict] = {}


def save_audit(event: AuditEvent) -> None:
    audit_events[event.packet_id].append(event)


def save_reject(reject: RejectLog) -> None:
    reject_logs.append(reject)


def save_trust_packet_memory(packet: TrustPacket) -> None:
    trust_packets[packet.packet_id] = packet


def save_packet(packet: TrustPacket, stored_packet: StoredSensorPacket) -> None:
    save_trust_packet_memory(packet)
    sensor_packets[packet.packet_id] = stored_packet
    packet_hash_index.add(packet.payload_hash)
    source_sequences[packet.source_id] = max(
        packet.sequence_no,
        source_sequences.get(packet.source_id, -1),
    )


def save_mrv_memory(mrv_result: dict) -> None:
    mrv_results[mrv_result["mrv_id"]] = mrv_result
    mrv_by_packet_id[mrv_result["packet_id"]] = mrv_result["mrv_id"]


def save_carbon_value_memory(value_result: dict) -> None:
    carbon_value_results[value_result["value_id"]] = value_result
    value_by_mrv_id[value_result["mrv_id"]] = value_result["value_id"]


def save_evidence_memory(bundle: dict) -> None:
    evidence = bundle["evidence"]
    integrity_report = bundle["integrity_report"]
    sensor_mapping = bundle["sensor_mapping"]
    digital_evidence[evidence["evidence_id"]] = evidence
    evidence_by_packet_id[evidence["packet_id"]] = evidence["evidence_id"]
    integrity_reports[integrity_report["integrity_report_id"]] = integrity_report
    integrity_report_by_evidence_id[evidence["evidence_id"]] = integrity_report["integrity_report_id"]
    evidence_sensor_mappings[sensor_mapping["mapping_id"]] = sensor_mapping


def save_taxi_operation_memory(operation: dict) -> None:
    taxi_daily_operations[operation["operation_id"]] = operation


def save_taxi_import_log_memory(log: dict) -> None:
    taxi_import_logs.append(log)


def save_green_point_memory(entry: dict) -> None:
    green_point_ledger.append(entry)


def save_wallet_memory(wallet: dict) -> None:
    driver_wallets[wallet["driver_id"]] = wallet


def save_wallet_transaction_memory(transaction: dict) -> None:
    wallet_transactions[transaction["transaction_id"]] = transaction
    wallet_transactions_by_driver_id[transaction["driver_id"]].append(transaction["transaction_id"])


def save_import_job_memory(job: dict) -> None:
    import_jobs[job["import_job_id"]] = job


def save_import_job_row_memory(row: dict) -> None:
    import_job_rows.append(row)


def save_failed_import_row_memory(row: dict) -> None:
    failed_import_rows.append(row)


def save_taxi_mrv_memory(result: dict) -> None:
    taxi_mrv_results[result["mrv_id"]] = result
    taxi_mrv_by_packet_id[result["packet_id"]] = result["mrv_id"]


def save_verification_memory(record: dict) -> None:
    mrv_verification_records[record["verification_id"]] = record
    verification_by_packet_id[record["packet_id"]] = record["verification_id"]


def save_carbon_asset_candidate_memory(candidate: dict) -> None:
    carbon_asset_candidates[candidate["candidate_id"]] = candidate
    carbon_asset_candidate_by_mrv_id[candidate["mrv_id"]] = candidate["candidate_id"]


def save_mrv_report_memory(report: dict) -> None:
    mrv_reports[report["report_id"]] = report


def save_methodology_memory(methodology: dict) -> None:
    methodology_registry[f"{methodology['methodology_id']}:{methodology['version']}"] = methodology


def save_methodology_snapshot_memory(snapshot: dict) -> None:
    methodology_snapshots[snapshot["snapshot_id"]] = snapshot


def save_methodology_impact_memory(impact: dict) -> None:
    methodology_change_impacts[impact["impact_id"]] = impact


def save_portfolio_target_memory(target: dict) -> None:
    portfolio_targets[target["portfolio_id"]] = target


def save_portfolio_kpi_snapshot_memory(snapshot: dict) -> None:
    portfolio_kpi_snapshots[snapshot["snapshot_id"]] = snapshot


def save_partner_health_memory(health: dict) -> None:
    partner_health[health["partner_id"]] = health


def save_partner_memory(partner: dict) -> None:
    partners[partner["partner_id"]] = partner


def save_partner_api_key_memory(api_key: dict) -> None:
    partner_api_keys[api_key["api_key_id"]] = api_key


def save_partner_mapping_memory(mapping: dict) -> None:
    partner_data_mappings[mapping["mapping_id"]] = mapping


def save_partner_integration_memory(integration: dict) -> None:
    partner_integrations[integration["integration_id"]] = integration


def save_partner_health_log_memory(log: dict) -> None:
    partner_health_logs.append(log)


def save_dead_letter_memory(item: dict) -> None:
    dead_letter_queue[item["dlq_id"]] = item


def save_tenant_memory(tenant: dict) -> None:
    tenants[tenant["tenant_id"]] = tenant


def save_tenant_user_memory(user: dict) -> None:
    tenant_users[user["user_id"]] = user


def save_tenant_subscription_memory(subscription: dict) -> None:
    tenant_subscriptions[subscription["subscription_id"]] = subscription


def save_billing_account_memory(account: dict) -> None:
    billing_accounts[account["billing_account_id"]] = account


def save_tenant_audit_log_memory(log: dict) -> None:
    tenant_audit_logs.append(log)


def save_merchant_account_memory(account: dict) -> None:
    merchant_accounts[account["merchant_account_id"]] = account


def save_commission_rule_memory(rule: dict) -> None:
    commission_rules[rule["rule_id"]] = rule


def save_settlement_record_memory(record: dict) -> None:
    settlement_records[record["settlement_id"]] = record


def save_settlement_batch_memory(batch: dict) -> None:
    settlement_batches[batch["batch_id"]] = batch


def save_settlement_ledger_entry_memory(entry: dict) -> None:
    settlement_ledger_entries.append(entry)


def save_onboarding_project_memory(project: dict) -> None:
    onboarding_projects[project["onboarding_id"]] = project


def save_onboarding_checklist_memory(checklist: dict) -> None:
    onboarding_checklists[checklist["checklist_id"]] = checklist


def save_deployment_template_memory(template: dict) -> None:
    deployment_templates[template["template_id"]] = template


def save_deployment_run_memory(run: dict) -> None:
    deployment_runs[run["deployment_run_id"]] = run


def save_customer_health_snapshot_memory(snapshot: dict) -> None:
    customer_health_snapshots[snapshot["health_snapshot_id"]] = snapshot


def save_production_readiness_check_memory(check: dict) -> None:
    production_readiness_checks[check["check_id"]] = check


def save_sla_snapshot_memory(snapshot: dict) -> None:
    sla_snapshots[snapshot["sla_snapshot_id"]] = snapshot


def save_operational_runbook_memory(runbook: dict) -> None:
    operational_runbooks[runbook["runbook_id"]] = runbook


def save_country_profile_memory(profile: dict) -> None:
    country_profiles[profile["country_code"]] = profile


def save_country_methodology_adapter_memory(adapter: dict) -> None:
    country_methodology_adapters[adapter["adapter_id"]] = adapter


def save_localized_report_template_memory(template: dict) -> None:
    localized_report_templates[template["template_id"]] = template


def save_copilot_query_log_memory(log: dict) -> None:
    copilot_query_logs.append(log)


def save_audit_intelligence_explanation_memory(explanation: dict) -> None:
    audit_intelligence_explanations[explanation["explanation_id"]] = explanation


def save_evidence_explanation_memory(explanation: dict) -> None:
    evidence_explanations[explanation["explanation_id"]] = explanation


def save_asset_ownership_memory(record: dict) -> None:
    asset_ownership_records[record["asset_id"]] = record


def save_asset_custody_memory(record: dict) -> None:
    asset_custody_records[record["asset_id"]] = record


def save_asset_transfer_memory(record: dict) -> None:
    asset_transfer_records[record["transfer_id"]] = record


def save_asset_ownership_audit_memory(log: dict) -> None:
    asset_ownership_audit_logs.append(log)


def save_partner_auth_account_memory(account: dict) -> None:
    partner_auth_accounts[account["partner_code"]] = account


def save_referral_auth_account_memory(account: dict) -> None:
    referral_auth_accounts[account["referral_code"]] = account


def save_auth_session_memory(session: dict) -> None:
    auth_sessions[session["access_token"]] = session


def save_auth_audit_log_memory(log: dict) -> None:
    auth_audit_logs.append(log)


def save_password_reset_token_memory(token: dict) -> None:
    password_reset_tokens[token["reset_token"]] = token


def save_translation_key_memory(key: dict) -> None:
    translation_keys[key["translation_key_id"]] = key


def save_translation_review_memory(review: dict) -> None:
    translation_reviews[review["review_id"]] = review


def save_language_reviewer_memory(reviewer: dict) -> None:
    language_reviewers[reviewer["reviewer_id"]] = reviewer
