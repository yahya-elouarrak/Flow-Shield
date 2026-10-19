import { cn } from "@/lib/utils"

export type SeverityType = "critical" | "high" | "medium" | "low" | "info"

export function SeverityBadge({ severity, className }: { severity: SeverityType | string, className?: string }) {
  const normalized = severity.toLowerCase()
  
  let colorClass = "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
  
  if (normalized === "critical") {
    colorClass = "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-500/10 dark:text-rose-400 dark:border-rose-500/30"
  } else if (normalized === "high") {
    colorClass = "bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-500/10 dark:text-orange-400 dark:border-orange-500/30"
  } else if (normalized === "medium") {
    colorClass = "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/30"
  } else if (normalized === "low") {
    colorClass = "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/30"
  } else if (normalized === "info") {
    colorClass = "bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-500/10 dark:text-slate-300 dark:border-slate-500/30"
  }

  return (
    <span className={cn("px-2 py-0.5 rounded-sm border text-[10px] font-bold uppercase tracking-wider", colorClass, className)}>
      {severity}
    </span>
  )
}
