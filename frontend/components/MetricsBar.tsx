"use client"
import { Metrics } from "@/lib/types"
import { ShieldCheck, ShieldAlert, Activity, AlertTriangle } from "lucide-react"

function riskColor(score: number) {
  if (score < 0.3) return "text-emerald-400"
  if (score < 0.7) return "text-yellow-400"
  return "text-red-400"
}

function riskLabel(score: number) {
  if (score < 0.3) return "LOW"
  if (score < 0.7) return "MEDIUM"
  return "HIGH"
}

export default function MetricsBar({ metrics }: { metrics: Metrics | null }) {
  const cards = [
    {
      label: "Total Policies",
      value: metrics?.total_policies ?? "—",
      icon: ShieldCheck,
      color: "text-sky-400",
      bg: "bg-sky-400/10",
    },
    {
      label: "Active Policies",
      value: metrics?.active_policies ?? "—",
      icon: Activity,
      color: "text-emerald-400",
      bg: "bg-emerald-400/10",
    },
    {
      label: "Blocked Today",
      value: metrics?.blocked_today ?? "—",
      icon: ShieldAlert,
      color: "text-red-400",
      bg: "bg-red-400/10",
    },
    {
      label: "Risk Score",
      value: metrics ? `${riskLabel(metrics.risk_score)} (${(metrics.risk_score * 100).toFixed(0)}%)` : "—",
      icon: AlertTriangle,
      color: metrics ? riskColor(metrics.risk_score) : "text-zinc-400",
      bg: metrics ? (metrics.risk_score < 0.3 ? "bg-emerald-400/10" : metrics.risk_score < 0.7 ? "bg-yellow-400/10" : "bg-red-400/10") : "bg-zinc-800",
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map(({ label, value, icon: Icon, color, bg }) => (
        <div key={label} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center gap-3">
          <div className={`${bg} p-2.5 rounded-lg`}>
            <Icon className={`w-5 h-5 ${color}`} />
          </div>
          <div>
            <p className="text-xs text-zinc-500 font-medium">{label}</p>
            <p className={`text-lg font-bold ${color}`}>{String(value)}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
