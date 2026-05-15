"use client"
import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { Policy } from "@/lib/types"
import { Wand2, CheckCircle, Trash2, Loader2, Shield } from "lucide-react"

const COMPLIANCE_OPTIONS = ["HIPAA", "SOC2", "PCI-DSS"]

export default function PoliciesPage() {
  const [description, setDescription] = useState("")
  const [yaml, setYaml] = useState("")
  const [policyName, setPolicyName] = useState("")
  const [tags, setTags] = useState<string[]>([])
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [policies, setPolicies] = useState<Policy[]>([])
  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    api.listPolicies().then(setPolicies).catch(() => {})
  }, [])

  function showToast(msg: string, type: "ok" | "err") {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  async function generate() {
    if (!description.trim()) return
    setGenerating(true)
    setError("")
    try {
      const res = await api.generatePolicy(description, tags)
      setYaml(res.yaml)
      setPolicyName(res.name)
    } catch (e: any) {
      setError(e.message || "Failed to generate policy")
    } finally {
      setGenerating(false)
    }
  }

  async function savePolicy() {
    if (!yaml || !policyName) return
    setSaving(true)
    try {
      await api.savePolicy(policyName, description, yaml, tags)
      const updated = await api.listPolicies()
      setPolicies(updated)
      setYaml("")
      setDescription("")
      setPolicyName("")
      showToast("Policy activated successfully!", "ok")
    } catch (e: any) {
      showToast(e.message || "Failed to save policy", "err")
    } finally {
      setSaving(false)
    }
  }

  async function removePolicy(id: string) {
    try {
      await api.deletePolicy(id)
      setPolicies(p => p.filter(x => x.id !== id))
      showToast("Policy deactivated", "ok")
    } catch {
      showToast("Failed to delete policy", "err")
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg text-sm font-medium shadow-lg ${
          toast.type === "ok" ? "bg-emerald-500 text-white" : "bg-red-500 text-white"
        }`}>
          {toast.msg}
        </div>
      )}

      <div>
        <h1 className="text-2xl font-bold text-white">Policy Editor</h1>
        <p className="text-sm text-zinc-500 mt-0.5">Describe a security policy in plain English — Gemini generates the enforcement rule</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Input */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 space-y-4">
          <h2 className="font-semibold text-white">Natural Language Policy</h2>

          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="e.g. Block any agent that tries to read or transmit patient SSN numbers, medical records, or health information"
            rows={5}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-emerald-500 resize-none"
          />

          {/* Compliance tags */}
          <div>
            <p className="text-xs text-zinc-500 mb-2 font-medium uppercase tracking-wide">Compliance Tags</p>
            <div className="flex gap-2 flex-wrap">
              {COMPLIANCE_OPTIONS.map(tag => (
                <button
                  key={tag}
                  onClick={() => setTags(t => t.includes(tag) ? t.filter(x => x !== tag) : [...t, tag])}
                  className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
                    tags.includes(tag)
                      ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
                      : "bg-zinc-800 text-zinc-400 border-zinc-700 hover:border-zinc-500"
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            onClick={generate}
            disabled={generating || !description.trim()}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 disabled:bg-zinc-700 disabled:text-zinc-500 text-black font-semibold rounded-lg transition-colors text-sm"
          >
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
            {generating ? "Generating with Gemini…" : "Generate Policy"}
          </button>
        </div>

        {/* Right: YAML output */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-white">Generated YAML Rule</h2>
            {yaml && <span className="text-xs text-emerald-400 font-medium">Ready to activate</span>}
          </div>

          {yaml ? (
            <>
              <input
                value={policyName}
                onChange={e => setPolicyName(e.target.value)}
                placeholder="Policy name"
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
              />
              <textarea
                value={yaml}
                onChange={e => setYaml(e.target.value)}
                rows={10}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-xs text-emerald-300 font-mono focus:outline-none focus:border-emerald-500 resize-none"
              />
              <button
                onClick={savePolicy}
                disabled={saving}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 disabled:bg-zinc-700 text-black font-semibold rounded-lg transition-colors text-sm"
              >
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                {saving ? "Activating…" : "Activate Policy"}
              </button>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-zinc-600">
              <Shield className="w-10 h-10 mb-3 opacity-30" />
              <p className="text-sm">Generated YAML will appear here</p>
              <p className="text-xs mt-1">Write a description and click Generate</p>
            </div>
          )}
        </div>
      </div>

      {/* Active Policies Table */}
      {policies.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <h2 className="font-semibold text-white mb-4">Active Policies ({policies.length})</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 text-zinc-500 text-xs uppercase">
                <th className="text-left py-2 pr-4 font-medium">Name</th>
                <th className="text-left py-2 pr-4 font-medium">Compliance</th>
                <th className="text-left py-2 pr-4 font-medium">Created</th>
                <th className="text-left py-2 font-medium">Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {policies.map(p => (
                <tr key={p.id} className="border-b border-zinc-800/50">
                  <td className="py-2.5 pr-4 text-white font-mono text-xs">{p.name}</td>
                  <td className="py-2.5 pr-4">
                    <div className="flex gap-1 flex-wrap">
                      {p.compliance_tags.map(t => (
                        <span key={t} className="text-xs px-1.5 py-0.5 bg-sky-500/15 text-sky-400 rounded">{t}</span>
                      ))}
                    </div>
                  </td>
                  <td className="py-2.5 pr-4 text-zinc-500 text-xs">
                    {new Date(p.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-2.5 pr-4">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded ${p.is_active ? "bg-emerald-500/15 text-emerald-400" : "bg-zinc-700 text-zinc-400"}`}>
                      {p.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="py-2.5">
                    <button onClick={() => removePolicy(p.id)} className="text-zinc-600 hover:text-red-400 transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
