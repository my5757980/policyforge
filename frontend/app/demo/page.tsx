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

const ACTION_STYLE: Record<string, { box: string; text: string }> = {
  BLOCK: { box: "bg-red-500/10 border border-red-500/30", text: "text-red-400" },
  ALLOW: { box: "bg-emerald-500/10 border border-emerald-500/30", text: "text-emerald-400" },
  LOG: { box: "bg-yellow-500/10 border border-yellow-500/30", text: "text-yellow-400" },
  ERROR: { box: "bg-zinc-800/60 border border-zinc-700", text: "text-zinc-300" },
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
      setResult({ action: "ERROR", intent_category: "", risk_score: null, matched_rule: "", message: `Could not check the attack: ${e.message}`, latency_ms: 0 })
    } finally {
      setFiring(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Attack Demo</h1>
        <p className="text-sm text-zinc-500 mt-0.5">Fire adversarial prompts at your active policies and see what each one really does</p>
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
                <p className="text-sm text-zinc-400">Checking the attack against your active policies…</p>
              </div>
            )}
            {result && !firing && (
              <div className="space-y-4">
                <div className={`flex items-center gap-3 p-4 rounded-xl ${ACTION_STYLE[result.action]?.box ?? ACTION_STYLE.ERROR.box}`}>
                  {result.action === "BLOCK" || result.action === "ERROR"
                    ? <ShieldX className={`w-8 h-8 flex-shrink-0 ${ACTION_STYLE[result.action].text}`} />
                    : <ShieldCheck className={`w-8 h-8 flex-shrink-0 ${ACTION_STYLE[result.action]?.text ?? ""}`} />
                  }
                  <div>
                    <p className={`text-2xl font-black ${ACTION_STYLE[result.action]?.text ?? ""}`}>
                      {result.action}
                    </p>
                    <p className="text-xs text-zinc-400 mt-0.5">{result.message}</p>
                  </div>
                </div>

                {result.action !== "ERROR" && (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between gap-3">
                      <span className="text-zinc-500">Checked by</span>
                      <span className="text-zinc-300 text-xs text-right">
                        PolicyForge: keywords + PII{result.not_checked?.includes("intent") ? " (intent not checked)" : ""}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-zinc-500">Policy</span>
                      <span className="text-white font-mono text-xs">{result.matched_policy || "—"}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-zinc-500">Matched Rule</span>
                      <span className="text-emerald-400 font-mono text-xs">{result.matched_rule || "none"}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-zinc-500">Matched on</span>
                      <span className="text-zinc-300 font-mono text-xs text-right">
                        {result.matched_on?.length ? result.matched_on.join(", ") : "—"}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-zinc-500">Check time</span>
                      <span className="text-zinc-400">{result.latency_ms}ms</span>
                    </div>
                  </div>
                )}
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
                    <span className={`font-bold ${ACTION_STYLE[h.action]?.text ?? ""}`}>
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
