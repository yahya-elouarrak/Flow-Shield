"use client"

import { PageHeader } from "@/components/flowshield/page-header"
import { EmptyState } from "@/components/flowshield/empty-state"
import { ShieldAlert } from "lucide-react"

export default function FindingsPage() {
  return (
    <div>
      <PageHeader 
        title="Findings" 
        description="All vulnerabilities and logic flaws discovered across your projects."
      />
      <EmptyState 
        title="No findings yet" 
        description="Launch a scan on a project to start detecting vulnerabilities."
        icon={<ShieldAlert size={24} />}
      />
    </div>
  )
}
