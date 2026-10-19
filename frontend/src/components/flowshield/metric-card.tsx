import { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface MetricCardProps {
  title: string
  value: string | number
  icon?: ReactNode
  trend?: string
  trendUp?: boolean
  className?: string
}

export function MetricCard({ title, value, icon, trend, trendUp, className }: MetricCardProps) {
  return (
    <div className={cn("rounded-sm border border-fs-border bg-fs-surface p-5", className)}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs uppercase tracking-wider font-semibold text-fs-muted">{title}</h3>
        {icon && <div className="text-fs-accent-cyan">{icon}</div>}
      </div>
      <div className="flex items-baseline gap-2">
        <div className="text-2xl font-bold tracking-tight text-fs-text">{value}</div>
        {trend && (
          <span className={cn(
            "text-xs font-medium px-2 py-0.5 rounded-sm",
            trendUp ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400" 
                    : "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400"
          )}>
            {trend}
          </span>
        )}
      </div>
    </div>
  )
}
