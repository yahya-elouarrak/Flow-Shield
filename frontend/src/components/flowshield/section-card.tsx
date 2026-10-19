import { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface SectionCardProps {
  title?: string
  description?: string
  children: ReactNode
  className?: string
  action?: ReactNode
}

export function SectionCard({ title, description, children, className, action }: SectionCardProps) {
  return (
    <div className={cn("rounded-sm border border-fs-border bg-fs-surface overflow-hidden", className)}>
      {(title || description || action) && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-fs-border px-5 py-3">
          <div>
            {title && <h3 className="text-base font-semibold text-fs-text">{title}</h3>}
            {description && <p className="text-sm text-fs-muted mt-1">{description}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
    </div>
  )
}
