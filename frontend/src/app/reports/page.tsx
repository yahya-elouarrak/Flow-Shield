"use client"

import { PageHeader } from "@/components/flowshield/page-header"
import { EmptyState } from "@/components/flowshield/empty-state"
import { FileText } from "lucide-react"

export default function ReportsPage() {
  return (
    <div>
      <PageHeader 
        title="Reports" 
        description="Generate and download professional security reports."
      />
      <EmptyState 
        title="No reports generated" 
        description="Run scans and generate reports to share with your team."
        icon={<FileText size={24} />}
      />
    </div>
  )
}
