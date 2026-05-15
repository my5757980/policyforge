"use client"
import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { AttackType, AttackResult } from "@/lib/types"
import { Swords, ShieldX, ShieldCheck, Loader2, Zap } from "lucide-react"

const ATTACK_ICONS: Record<string, string> = {
  prompt_injection: "💉",
  pii_exfiltration: "🔓",
  credential_theft: "🗝️",
  jailbreak: "⛓️",
  data_exfiltration: "📤",
}

export default function DemoPage() {
  const [attacks, setAttacks] = useState<AttackType[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [result, setResult] = useState<AttackResult | null>(null)
  const [firing, setFiring] = useState(false)
  const [history, setHistory] = useState<(AttackResult & { type: string })[]>([])

  useEffect(() => {
    api.listAttacks().then(setAttacks).catch(() => {})
  }, [])

  async function fire() {
    if (!selected) return
    setFiring(true)
    setResult(null)
    try {
      const res = await api.fireAttack(selected)
      setResult(res)
      setHistory(h => [{ ...res, type: selected }, ...h].slice(0, 10))
    } catch (e: any) {
      setResult({ action: "ALLOW", intent_category: "error", risk_score: 0, matched_rule: "", message: e.message, latency_ms: 0 })
    } finally {
      setFiring(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Attack Demo</h1>
        <p className="text-sm text-zinc-500 mt-0.5">Fire real adversarial attacks and watch your policies block them in real-time</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Attack Selector */}
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide">Select Attack Type</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {attacks.map(a => (
              <button
                key={a.type}
                onClick={() => { setSelected(a.type); setResult(null) }}
                className={`text-left p-4 rounded-xl border transition-all ${
                  selected === a.type
                    ? "bg-red-500/10 border-red-500/40 ring-1 ring-red-500/30"
                    : "bg-zinc-900 border-zinc-800 hover:border-zinc-600"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">{ATTACK_ICONS[a.type] ?? "⚠️"}</span>
                  <span className="font-medium text-sm text-white capitalize">
                    {a.type.replace(/_/g, " ")}
                  </span>
                </div>
                <p className="text-xs text-zinc-500 leading-relaxed">{a.description}</p>
                <p className="text-xs text-zinc-600 mt-2 font-mono truncate">"{a.prompt_preview}"</p>
              </button>
            ))}
          </div>

          <button
            onClick={fire}
            disabled={!selected || firing}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-500 hover:bg-red-400 disabled:bg-zinc-700 disabled:text-zinc-500 text-white font-bold rounded-xl transition-colors text-sm mt-2"
          >
            {firing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            {firing ? "Firing attack…" : "Fire Attack"}
          </button>
        </div>

        {/* Result Panel */}
        <div className="space-y-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 min-h-64">
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-4">Result</h2>
            {!result && !firing && (
              <div className="flex flex-col items-center justify-center py-10 text-zinc-600">
                <Swords className="w-10 h-10 mb-3 opacity-30" />
                <p className="text-sm">Select an attack and fire</p>
              </div>
            )}
            {firing && (
              <div className="flex flex-col items-center justify-center py-10">
                <Loader2 className="w-8 h-8 text-red-400 animate-spin mb-3" />
                <p className="text-sm text-zinc-400">Sending attack through Lobster Trap…</p>
              </div>
            )}
            {result && !firing && (
              <div className="space-y-4">
                <div className={`flex items-center gap-3 p-4 rounded-xl ${
                  result.action === "BLOCK"
                    ? "bg-red-500/10 border border-red-500/30"
                    : "bg-emerald-500/10 border border-emerald-500/30"
                }`}>
                  {result.action === "BLOCK"
                    ? <ShieldX className="w-8 h-8 text-red-400 flex-shrink-0" />
                    : <ShieldCheck className="w-8 h-8 text-emerald-400 flex-shrink-0" />
                  }
                  <div>
                    <p className={`text-2xl font-black ${result.action === "BLOCK" ? "text-red-400" : "text-emerald-400"}`}>
                      {result.action}
                    </p>
                    <p className="text-xs text-zinc-400 mt-0.5">{result.message}</p>
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Intent</span>
                    <span className="text-white font-mono text-xs">{result.intent_category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Matched Rule</span>
                    <span className="text-emerald-400 font-mono text-xs">{result.matched_rule || "none"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Risk Score</span>
                    <span className={`font-bold ${result.risk_score >= 0.7 ? "text-red-400" : "text-yellow-400"}`}>
                      {(result.risk_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Latency</span>
                    <span className="text-zinc-400">{result.latency_ms}ms</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Attack History */}
          {history.length > 0 && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wide mb-3">Session History</h3>
              <div className="space-y-2">
                {history.map((h, i) => (
                  <div key={i} className="flex items-center justify-between text-xs">
                    <span className="text-zinc-500 capitalize">{h.type.replace(/_/g, " ")}</span>
                    <span className={`font-bold ${h.action === "BLOCK" ? "text-red-400" : "text-emerald-400"}`}>
                      {h.action}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
