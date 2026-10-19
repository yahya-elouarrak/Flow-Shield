import { ReactNode } from "react"
import { cn } from "@/lib/utils"
import { ShieldAlert } from "lucide-react"

interface EmptyStateProps {
  title: string
  description: string
  action?: ReactNode
  icon?: ReactNode
  className?: string
}

export function EmptyState({ title, description, action, icon, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-10 text-center border border-dashed border-fs-border rounded-sm bg-fs-bg-secondary", className)}>
      <div className="h-10 w-10 rounded-sm flex items-center justify-center text-fs-muted mb-4">
        {icon || <ShieldAlert size={24} />}
      </div>
      <h3 className="text-base font-semibold text-fs-text">{title}</h3>
      <p className="mt-2 text-sm text-fs-muted max-w-sm mb-6">{description}</p>
      {action && <div>{action}</div>}
    </div>
  )
}
