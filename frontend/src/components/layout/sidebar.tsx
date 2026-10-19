"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { FlowShieldLogo } from "../flowshield/logo"
import { cn } from "@/lib/utils"
import { LayoutDashboard, FolderKanban, FileText, Settings, ShieldAlert, Activity } from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Projects", href: "/projects", icon: FolderKanban },
  { name: "Findings", href: "/findings", icon: ShieldAlert },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Settings", href: "/settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col border-r border-fs-border bg-fs-surface dark:bg-fs-bg-secondary">
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-fs-border">
        <Link href="/" className="flex items-center gap-2 transition-transform hover:scale-105">
          <FlowShieldLogo />
        </Link>
      </div>
      
      <div className="flex flex-1 flex-col overflow-y-auto pt-6 px-4">
        <nav className="flex-1 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href)
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  isActive
                    ? "bg-fs-accent-cyan/10 text-fs-accent-cyan font-medium border-l-2 border-fs-accent-cyan rounded-r-md -ml-3 pl-5"
                    : "text-fs-muted hover:bg-fs-surface-elevated hover:text-fs-text rounded-md",
                  "group flex items-center px-3 py-2 text-sm transition-all"
                )}
              >
                <item.icon
                  className={cn(
                    isActive ? "text-fs-accent-cyan" : "text-fs-muted group-hover:text-fs-text",
                    "mr-3 h-5 w-5 shrink-0 transition-colors"
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>
      
      <div className="p-4 border-t border-fs-border">
        <div className="flex items-center gap-3 px-3 py-2 rounded-sm bg-fs-surface-elevated border border-fs-border">
          <div className="h-2 w-2 rounded-full bg-fs-accent-cyan animate-pulse" />
          <div className="text-xs font-medium text-fs-text">Scanner Ready</div>
        </div>
      </div>
    </div>
  )
}
