"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { fetchApi } from "@/lib/api-client"
import { type ScanJob, type ScanCreateRequest } from "@/lib/types"
import { SectionCard } from "@/components/flowshield/section-card"
import { AlertTriangle, ShieldAlert, Zap, Loader2, XCircle, Info } from "lucide-react"

export default function LaunchScanPage() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.id as string

  const [roeConfirmed, setRoeConfirmed] = useState(false)
  const [aiEnabled, setAiEnabled] = useState(true)
  const [enableBola, setEnableBola] = useState(true)
  const [enableBfla, setEnableBfla] = useState(true)
  const [enableMa, setEnableMa] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [readiness, setReadiness] = useState<any>(null)
  const [readinessLoading, setReadinessLoading] = useState(true)

  useEffect(() => {
    async function checkReadiness() {
      try {
        const rd = await fetchApi<any>(`/projects/${projectId}/readiness`)
        setReadiness(rd)
      } catch (err) {
        console.error("Failed to fetch readiness", err)
      } finally {
        setReadinessLoading(false)
      }
    }
    checkReadiness()
  }, [projectId])

  const launchScan = async () => {
    if (!roeConfirmed || (readiness && !readiness.ready)) return
    setLoading(true)
    setError(null)
    
    try {
      const req: ScanCreateRequest = {
        ai_enabled: aiEnabled,
        safety_profile: "standard",
        options_json: {
          enable_bola: enableBola,
          enable_bfla: enableBfla,
          enable_mass_assignment: enableMa
        },
        roe_confirmed: roeConfirmed
      }
      
      const scan = await fetchApi<ScanJob>(`/projects/${projectId}/scans`, {
        method: "POST",
        body: JSON.stringify(req)
      })
      
      router.push(`/scans/${scan.id}`)
    } catch (err: any) {
      setError(err.message || "Failed to launch scan")
      setLoading(false)
    }
  }

  const isReady = readiness?.ready ?? true; // if readiness fails to load, let them try

  return (
    <div className="space-y-6 max-w-3xl">
      {error && (
        <div className="p-4 rounded-sm bg-red-50 text-red-600 border border-red-200 dark:bg-red-900/10 dark:border-red-500/20 flex items-start gap-3">
          <AlertTriangle size={18} className="mt-0.5 shrink-0" />
          <div className="text-sm">{error}</div>
        </div>
      )}

      {readinessLoading ? (
        <div className="p-4 rounded-sm bg-slate-50 border border-slate-200 text-slate-500 flex items-center gap-3">
          <Loader2 className="animate-spin" size={18} /> Checking project readiness...
        </div>
      ) : !isReady ? (
        <div className="p-5 rounded-sm bg-red-50 border border-red-200 dark:bg-red-900/10 dark:border-red-500/20">
          <div className="flex items-start gap-3">
            <XCircle className="text-red-600 dark:text-red-400 shrink-0 mt-0.5" size={20} />
            <div>
              <h3 className="text-sm font-semibold text-red-800 dark:text-red-400">Scan Blocked: Project Not Ready</h3>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1 mb-3">
                Your project is missing required configuration to run a scan. Please fix the following issues:
              </p>
              <ul className="list-disc pl-5 text-sm text-red-700 dark:text-red-300 space-y-1 mb-4">
                {readiness.checks.filter((c: any) => c.status === "fail").map((c: any) => (
                  <li key={c.key}>{c.label}: {c.message}</li>
                ))}
              </ul>
              <Link href={`/projects/${projectId}/configuration`} className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-sm hover:bg-red-500 transition-colors">
                Go to Configuration
              </Link>
            </div>
          </div>
        </div>
      ) : null}

      <SectionCard title="Scan Configuration">
        <div className="space-y-6">
          <div className="flex items-start gap-4 p-4 rounded-sm border border-slate-200 dark:border-white/10">
            <div className="flex-1">
              <h4 className="text-sm font-medium text-slate-900 dark:text-white">Active Detection Engines</h4>
              <p className="text-sm text-slate-500 mt-1 mb-4">Select which vulnerability classes to test for during this scan.</p>
              
              <div className="space-y-3">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" checked={enableBola} onChange={e => setEnableBola(e.target.checked)} className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">BOLA (Broken Object Level Authorization)</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" checked={enableBfla} onChange={e => setEnableBfla(e.target.checked)} className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">BFLA (Broken Function Level Authorization)</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" checked={enableMa} onChange={e => setEnableMa(e.target.checked)} className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Mass Assignment</span>
                </label>
              </div>
            </div>
          </div>
          
          <div className="flex items-start gap-4 p-4 rounded-sm border border-slate-200 dark:border-white/10">
            <div className="flex items-center justify-center w-10 h-10 rounded-sm bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 shrink-0">
              <Zap size={20} />
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-slate-900 dark:text-white">AI-Assisted Reasoning</h4>
              <p className="text-sm text-slate-500 mt-1">Use local LLM to infer object relationships and predict likely authorization flaws. Significantly improves coverage but takes longer.</p>
            </div>
            <div className="pt-2 shrink-0">
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" checked={aiEnabled} onChange={e => setAiEnabled(e.target.checked)} />
                <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-zinc-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>

          <div className="flex items-start gap-4 p-4 rounded-sm border border-amber-200 bg-amber-50 dark:bg-amber-900/10 dark:border-amber-500/20">
            <div className="text-amber-600 dark:text-amber-500 mt-0.5 shrink-0">
              <ShieldAlert size={20} />
            </div>
            <div>
              <h4 className="text-sm font-medium text-amber-800 dark:text-amber-400">Rules of Engagement</h4>
              <p className="text-sm text-amber-700/80 dark:text-amber-500/80 mt-1 mb-3">
                FlowShield will actively send mutated HTTP requests to the target API. It will attempt to bypass authorization checks, modify resources, and leak data across accounts.
              </p>
              <label className="flex items-start gap-3 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={roeConfirmed} 
                  onChange={e => setRoeConfirmed(e.target.checked)}
                  className="mt-0.5 rounded border-amber-300 text-amber-600 focus:ring-amber-500 w-4 h-4 bg-white dark:bg-zinc-900"
                />
                <span className="text-sm font-medium text-amber-900 dark:text-amber-300">
                  I am authorized to test this target and accept the consequences.
                </span>
              </label>
            </div>
          </div>
        </div>
      </SectionCard>

      <div className="flex justify-end gap-3 pt-4">
        <button 
          onClick={launchScan} 
          disabled={!roeConfirmed || loading || !isReady}
          className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-sm hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && <Loader2 size={16} className="animate-spin" />}
          {loading ? "Starting..." : "Launch Scan"}
        </button>
      </div>
    </div>
  )
}
