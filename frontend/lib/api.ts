const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  // Policies
  generatePolicy: (description: string, compliance_tags: string[]) =>
    req<{ yaml: string; name: string }>("/api/policies/generate", {
      method: "POST",
      body: JSON.stringify({ description, compliance_tags }),
    }),

  savePolicy: (name: string, description: string, yaml_content: string, compliance_tags: string[]) =>
    req("/api/policies/save", {
      method: "POST",
      body: JSON.stringify({ name, description, yaml_content, compliance_tags }),
    }),

  listPolicies: () => req<any[]>("/api/policies"),

  deletePolicy: (id: string) =>
    req(`/api/policies/${id}`, { method: "DELETE" }),

  // Audit
  getLogs: (limit = 20) => req<any[]>(`/api/audit/logs?limit=${limit}`),
  getMetrics: () => req<any>("/api/audit/metrics"),
  getReport: (standard: string) => req<any>(`/api/audit/report?standard=${standard}`),

  // Demo
  listAttacks: () => req<any[]>("/api/demo/attacks"),
  fireAttack: (attack_type: string) =>
    req<any>("/api/demo/attack", {
      method: "POST",
      body: JSON.stringify({ attack_type }),
    }),
}
