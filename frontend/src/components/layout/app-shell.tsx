"use client"

import { ReactNode } from "react"
import { Sidebar } from "./sidebar"
import { Topbar } from "./topbar"
import { usePathname } from "next/navigation"

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  
  // Don't wrap the landing page in the dashboard shell
  if (pathname === "/") {
    return <>{children}</>
  }

  return (
    <div className="flex h-screen overflow-hidden bg-transparent">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-6xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
