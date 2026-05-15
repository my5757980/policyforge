export interface Policy {
  id: string
  name: string
  description: string
  yaml_content: string
  is_active: boolean
  compliance_tags: string[]
  created_at: string
}

export interface AuditLog {
  id: number
  timestamp: string
  action: "BLOCK" | "ALLOW" | "LOG"
  intent_category: string
  risk_score: number
  matched_rule: string
  prompt_excerpt: string
  attack_type: string
}

export interface Metrics {
  total_policies: number
  active_policies: number
  blocked_today: number
  allowed_today: number
  risk_score: number
}

export interface AttackResult {
  action: "BLOCK" | "ALLOW"
  intent_category: string
  risk_score: number
  matched_rule: string
  message: string
  latency_ms: number
}

export interface AttackType {
  type: string
  description: string
  prompt_preview: string
}

export interface ChecklistItem {
  item: string
  status: boolean
}

export interface ComplianceReport {
  standard: string
  generated_at: string
  summary: { active_policies: number; total_blocked: number; total_events: number }
  policies: { name: string; compliance_tags: string; created_at: string }[]
  checklist: ChecklistItem[]
  audit_trail: AuditLog[]
}
