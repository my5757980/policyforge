"use client"
import { useEffect, useState, useCallback } from "react"
import { api } from "@/lib/api"
import { Metrics, AuditLog } from "@/lib/types"
import MetricsBar from "@/components/MetricsBar"
import AuditFeed from "@/components/AuditFeed"
import Link from "next/link"
import { Plus, RefreshCw } from "lucide-react"

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    try {
      const [m, l] = await Promise.all([api.getMetrics(), api.getLogs(20)])
      setMetrics(m)
      setLogs(l)
    } catch {
      // backend may not be running yet
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 5000)
    return () => clearInterval(interval)
  }, [refresh])

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Security Dashboard</h1>
          <p className="text-sm text-zinc-500 mt-0.5">Real-time AI agent security monitoring</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={refresh}
            className="flex items-center gap-2 px-3 py-2 text-sm text-zinc-400 hover:text-white bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
          <Link
            href="/policies"
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-black bg-emerald-400 hover:bg-emerald-300 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Policy
          </Link>
        </div>
      </div>

      {/* Metrics */}
      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 bg-zinc-800 animate-pulse rounded-xl" />
          ))}
        </div>
      ) : (
        <MetricsBar metrics={metrics} />
      )}

      {/* Audit Feed */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-white">Live Audit Feed</h2>
          <span className="text-xs text-zinc-500">Auto-refreshes every 5s</span>
        </div>
        {loading ? (
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 bg-zinc-800 animate-pulse rounded" />
            ))}
          </div>
        ) : (
          <AuditFeed logs={logs} />
        )}
      </div>
    </div>
  )
}
