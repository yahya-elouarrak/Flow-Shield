"use client"

import { useTheme } from "next-themes"
import Image from "next/image"
import { Moon, Sun, Monitor } from "lucide-react"
import { useEffect, useState } from "react"

export function Topbar() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="flex h-16 shrink-0 items-center justify-between border-b border-fs-border bg-fs-surface px-6">
      <div className="flex items-center gap-4">
        {/* Breadcrumb or Context Placeholder */}
        <div className="text-sm font-medium text-fs-muted">
          Workspaces
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        {mounted && (
          <div className="flex rounded-sm border border-fs-border bg-fs-bg-secondary p-0.5">
            <button
              onClick={() => setTheme("light")}
              className={`rounded-sm p-1.5 transition-colors ${theme === "light" ? "bg-fs-surface-elevated text-fs-text shadow-sm" : "text-fs-muted hover:text-fs-text"}`}
            >
              <Sun size={16} />
            </button>
            <button
              onClick={() => setTheme("dark")}
              className={`rounded-sm p-1.5 transition-colors ${theme === "dark" ? "bg-fs-surface-elevated text-fs-text shadow-sm" : "text-fs-muted hover:text-fs-text"}`}
            >
              <Moon size={16} />
            </button>
            <button
              onClick={() => setTheme("system")}
              className={`rounded-sm p-1.5 transition-colors ${theme === "system" ? "bg-fs-surface-elevated text-fs-text shadow-sm" : "text-fs-muted hover:text-fs-text"}`}
            >
              <Monitor size={16} />
            </button>
          </div>
        )}
        
        <div className="h-8 w-8 rounded-sm bg-fs-bg-secondary flex items-center justify-center border border-fs-border p-1">
          <Image src="/images/logo_mark_transparent.png" alt="Profile" width={24} height={24} className="object-contain" />
        </div>
      </div>
    </div>
  )
}
