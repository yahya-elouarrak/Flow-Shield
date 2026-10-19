import { ReactNode } from "react"

interface PageHeaderProps {
  title: string
  description?: string
  action?: ReactNode
}

export function PageHeader({ title, description, action }: PageHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-fs-text">{title}</h1>
        {description && <p className="text-sm text-fs-muted mt-1">{description}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
