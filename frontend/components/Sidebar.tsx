"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Shield, LayoutDashboard, FileCode2, Swords, FileBarChart2 } from "lucide-react"

const links = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/policies", label: "Policy Editor", icon: FileCode2 },
  { href: "/demo", label: "Attack Demo", icon: Swords },
  { href: "/report", label: "Compliance Report", icon: FileBarChart2 },
]

export default function Sidebar() {
  const path = usePathname()
  return (
    <aside className="w-60 min-h-screen bg-zinc-900 border-r border-zinc-800 flex flex-col">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-zinc-800">
        <Shield className="text-emerald-400 w-6 h-6" />
        <span className="font-bold text-white text-lg tracking-tight">PolicyForge</span>
      </div>
      <nav className="flex-1 py-4 px-3 space-y-1">
        {links.map(({ href, label, icon: Icon }) => {
          const active = path === href
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "text-zinc-400 hover:text-white hover:bg-zinc-800"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          )
        })}
      </nav>
      <div className="px-5 py-4 border-t border-zinc-800">
        <p className="text-xs text-zinc-600">TechEx Hackathon 2026</p>
        <p className="text-xs text-zinc-500">Track 1 — Agent Security</p>
      </div>
    </aside>
  )
}
