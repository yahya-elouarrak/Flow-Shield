import { cn } from "@/lib/utils"

export type StatusType = "running" | "completed" | "failed" | "pending" | "cancelled" | "local" | "lab" | "staging" | "bug_bounty"

export function StatusBadge({ status, className }: { status: StatusType | string, className?: string }) {
  const normalized = status.toLowerCase()
  
  let colorClass = "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700"
  
  if (["completed", "success", "local", "lab"].includes(normalized)) {
    colorClass = "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/30"
  } else if (["failed", "error", "cancelled", "bug_bounty"].includes(normalized)) {
    colorClass = "bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-400 border-rose-200 dark:border-rose-500/30"
  } else if (["running", "in_progress", "staging"].includes(normalized)) {
    colorClass = "bg-cyan-50 text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-400 border-cyan-200 dark:border-cyan-500/30"
  } else if (["pending", "queued"].includes(normalized)) {
    colorClass = "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400 border-amber-200 dark:border-amber-500/30"
  }

  return (
    <span className={cn("px-2 py-0.5 rounded-sm text-[11px] font-semibold border tracking-wide uppercase", colorClass, className)}>
      {status}
    </span>
  )
}
