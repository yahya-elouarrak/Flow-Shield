"use client"

import { EmptyState } from "@/components/flowshield/empty-state"
import { FileCode2 } from "lucide-react"

export default function WorkflowsPage() {
  return (
    <div>
      
      <EmptyState 
        title="No workflows defined" 
        description="Create workflows to test complex logic like checkout processes or multi-step approvals."
        icon={<FileCode2 size={24} />}
      />
    </div>
  )
}
