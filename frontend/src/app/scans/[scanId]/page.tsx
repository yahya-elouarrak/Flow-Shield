"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { fetchApi } from "@/lib/api-client"
import { type ScanJob, type ScanEvent } from "@/lib/types"
import { PageHeader } from "@/components/flowshield/page-header"
import { SectionCard } from "@/components/flowshield/section-card"
import { StatusBadge } from "@/components/flowshield/status-badge"
import { 
  Play, Square, CheckCircle2, XCircle, AlertTriangle, 
  Loader2, Info, ArrowLeft, RefreshCw
} from "lucide-react"

// Color mapping for phases
const phaseColors: Record<string, string> = {
  created: "bg-slate-500",
  loading: "bg-blue-500",
  authenticating: "bg-indigo-500",
  validating: "bg-violet-500",
  planning: "bg-fuchsia-500",
  executing: "bg-amber-500",
  verifying: "bg-orange-500",
  reporting: "bg-emerald-500"
}

export default function ScanMonitorPage() {
  const params = useParams()
  const router = useRouter()
  const scanId = params.scanId as string

  const [scan, setScan] = useState<ScanJob | null>(null)
  const [events, setEvents] = useState<ScanEvent[]>([])
  const [error, setError] = useState<string | null>(null)
  const [cancelling, setCancelling] = useState(false)

  const isFinished = scan?.status === "completed" || scan?.status === "failed" || scan?.status === "cancelled"

  useEffect(() => {
    let interval: NodeJS.Timeout

    const poll = async () => {
      try {
        const [s, e] = await Promise.all([
          fetchApi<ScanJob>(`/scans/${scanId}`),
          fetchApi<ScanEvent[]>(`/scans/${scanId}/events`)
        ])
        setScan(s)
        setEvents(e)
        
        if (s.status === "completed" || s.status === "failed" || s.status === "cancelled") {
          clearInterval(interval)
        }
      } catch (err: any) {
        setError(err.message || "Failed to load scan data")
      }
    }

    // Initial load
    poll()

    // Poll every 2 seconds if not finished
    if (!isFinished) {
      interval = setInterval(poll, 2000)
    }

    return () => clearInterval(interval)
  }, [scanId, isFinished])

  const cancelScan = async () => {
    setCancelling(true)
    try {
      await fetchApi(`/scans/${scanId}/cancel`, { method: "POST" })
      // Next poll will pick up the cancelled state
    } catch (err: any) {
      alert("Failed to cancel: " + err.message)
      setCancelling(false)
    }
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <AlertTriangle size={48} className="mx-auto text-red-500 mb-4" />
        <h2 className="text-xl font-semibold mb-2">Error Loading Scan</h2>
        <p className="text-slate-500">{error}</p>
        <button onClick={() => router.back()} className="mt-6 px-4 py-2 bg-slate-100 dark:bg-zinc-800 rounded-sm text-sm font-medium">Go Back</button>
      </div>
    )
  }

  if (!scan) {
    return (
      <div className="flex items-center justify-center p-20 text-slate-500">
        <Loader2 size={24} className="animate-spin mr-2" /> Loading scan details...
      </div>
    )
  }

  const progressWidth = `${scan.progress}%`
  const currentPhaseColor = phaseColors[scan.phase] || "bg-indigo-500"

  return (
    <div className="max-w-5xl mx-auto py-8">
      <div className="mb-6">
        <Link href={`/projects/${scan.project_id}`} className="inline-flex items-center text-sm text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
          <ArrowLeft size={16} className="mr-1" /> Back to Project
        </Link>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-3">
            Scan Execution
            <StatusBadge status={scan.status} />
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 font-mono">{scan.id}</p>
        </div>
        {!isFinished && (
          <button 
            onClick={cancelScan} 
            disabled={cancelling}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400 border border-red-200 dark:border-red-500/20 text-sm font-semibold rounded-sm hover:bg-red-100 dark:hover:bg-red-500/20 transition-colors disabled:opacity-50"
          >
            {cancelling ? <Loader2 size={16} className="animate-spin" /> : <Square size={16} />}
            Cancel Scan
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main execution view */}
        <div className="lg:col-span-2 space-y-6">
          <SectionCard title="Live Progress">
            <div className="mb-2 flex justify-between text-sm">
              <span className="font-medium text-slate-900 dark:text-white uppercase tracking-wider text-xs flex items-center gap-2">
                {!isFinished && <RefreshCw size={12} className="animate-spin text-indigo-500" />}
                Phase: {scan.phase}
              </span>
              <span className="font-medium text-slate-700 dark:text-slate-300">{scan.progress}%</span>
            </div>
            <div className="h-4 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden border border-slate-200 dark:border-white/10">
              <div 
                className={`h-full ${currentPhaseColor} transition-all duration-500 ease-out`}
                style={{ width: progressWidth }}
              />
            </div>
            
            {scan.error_message && (
              <div className="mt-4 p-4 rounded-sm bg-red-50 text-red-600 border border-red-200 dark:bg-red-900/10 dark:border-red-500/20 text-sm">
                <div className="font-semibold mb-1">Scan Failed</div>
                <div className="font-mono text-xs break-all">{scan.error_message}</div>
              </div>
            )}
          </SectionCard>

          <SectionCard title="Event Log">
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar flex flex-col-reverse">
              {events.length === 0 ? (
                <div className="text-center text-sm text-slate-500 py-8">Waiting for events...</div>
              ) : (
                events.map((event, idx) => (
                  <div key={event.id} className={`text-sm flex gap-3 ${idx === 0 && !isFinished ? "opacity-100" : "opacity-70"} hover:opacity-100 transition-opacity`}>
                    <div className="text-slate-400 font-mono text-xs shrink-0 mt-0.5">
                      {new Date(event.created_at).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' })}
                    </div>
                    <div className="shrink-0 mt-0.5">
                      {event.level === "info" && <Info size={16} className="text-blue-500" />}
                      {event.level === "warning" && <AlertTriangle size={16} className="text-amber-500" />}
                      {event.level === "error" && <XCircle size={16} className="text-red-500" />}
                    </div>
                    <div>
                      <span className="font-mono text-xs uppercase text-slate-500 mr-2">[{event.phase}]</span>
                      <span className={event.level === "error" ? "text-red-600 dark:text-red-400 font-medium" : "text-slate-700 dark:text-slate-300"}>
                        {event.message}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </SectionCard>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <SectionCard title="Details">
            <div className="space-y-4 text-sm">
              <div>
                <div className="text-xs text-slate-500 mb-1">Status</div>
                <div className="font-medium capitalize flex items-center gap-2">
                  {scan.status === "running" && <Play size={14} className="text-indigo-500" />}
                  {scan.status === "completed" && <CheckCircle2 size={14} className="text-emerald-500" />}
                  {scan.status === "failed" && <XCircle size={14} className="text-red-500" />}
                  {scan.status === "cancelled" && <Square size={14} className="text-slate-500" />}
                  {scan.status}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">AI Enabled</div>
                <div className="font-medium">{scan.ai_enabled ? "Yes" : "No"}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Safety Profile</div>
                <div className="font-medium capitalize">{scan.safety_profile}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Started At</div>
                <div className="font-medium">{scan.started_at ? new Date(scan.started_at).toLocaleString() : "—"}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Completed At</div>
                <div className="font-medium">{scan.completed_at ? new Date(scan.completed_at).toLocaleString() : "—"}</div>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  )
}
