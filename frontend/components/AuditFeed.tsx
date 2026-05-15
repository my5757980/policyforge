"use client"
import { AuditLog } from "@/lib/types"

function ActionBadge({ action }: { action: string }) {
  const styles: Record<string, string> = {
    BLOCK: "bg-red-500/15 text-red-400 border border-red-500/30",
    ALLOW: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
    LOG: "bg-zinc-700 text-zinc-400 border border-zinc-600",
  }
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded ${styles[action] ?? styles.LOG}`}>
      {action}
    </span>
  )
}

export default function AuditFeed({ logs }: { logs: AuditLog[] }) {
  if (!logs.length) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-zinc-600">
        <p className="text-sm">No audit events yet.</p>
        <p className="text-xs mt-1">Fire an attack from the Demo panel to see events here.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-800 text-zinc-500 text-xs uppercase">
            <th className="text-left py-2 pr-4 font-medium">Time</th>
            <th className="text-left py-2 pr-4 font-medium">Action</th>
            <th className="text-left py-2 pr-4 font-medium">Intent</th>
            <th className="text-left py-2 pr-4 font-medium">Matched Rule</th>
            <th className="text-left py-2 font-medium">Risk</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
              <td className="py-2.5 pr-4 text-zinc-500 whitespace-nowrap">
                {new Date(log.timestamp).toLocaleTimeString()}
              </td>
              <td className="py-2.5 pr-4">
                <ActionBadge action={log.action} />
              </td>
              <td className="py-2.5 pr-4 text-zinc-300 font-mono text-xs">{log.intent_category || "—"}</td>
              <td className="py-2.5 pr-4 text-zinc-400 font-mono text-xs">{log.matched_rule || "—"}</td>
              <td className="py-2.5">
                <span className={`font-bold text-xs ${log.risk_score >= 0.7 ? "text-red-400" : log.risk_score >= 0.4 ? "text-yellow-400" : "text-emerald-400"}`}>
                  {(log.risk_score * 100).toFixed(0)}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
