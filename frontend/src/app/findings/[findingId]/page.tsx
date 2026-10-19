"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { fetchApi } from "@/lib/api-client"
import { type Finding } from "@/lib/types"
import { SectionCard } from "@/components/flowshield/section-card"
import { ArrowLeft, ShieldAlert, CheckCircle2, Crosshair, FileJson, AlertTriangle } from "lucide-react"

const severityColors: Record<string, string> = {
  critical: "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800",
  high: "bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800",
  medium: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800",
  low: "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800",
  info: "bg-slate-100 text-slate-800 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700"
}

export default function FindingDetailPage() {
  const params = useParams()
  const findingId = params.findingId as string

  const [finding, setFinding] = useState<Finding | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchApi<Finding>(`/findings/${findingId}`)
        setFinding(data)
      } catch (err: any) {
        setError(err.message || "Failed to load finding")
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [findingId])

  if (loading) return <div className="p-8 text-center text-slate-500 animate-pulse">Loading finding details...</div>
  if (error || !finding) return <div className="p-8 text-center text-red-500">Error: {error || "Not found"}</div>

  const ev = finding.evidence

  return (
    <div className="max-w-5xl mx-auto py-8 px-4">
      <div className="mb-6">
        <Link href={`/projects/${finding.project_id}/findings`} className="inline-flex items-center text-sm text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
          <ArrowLeft size={16} className="mr-1" /> Back to Findings
        </Link>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className={`inline-flex items-center px-2.5 py-1 rounded-sm text-xs font-medium border uppercase tracking-wider ${severityColors[finding.severity] || severityColors.info}`}>
              {finding.severity}
            </span>
            <span className="text-sm font-semibold text-slate-500 uppercase tracking-wider">{finding.category.replace("_", " ")}</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            {finding.title}
          </h1>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <SectionCard title="Description">
            <p className="text-sm text-slate-700 dark:text-slate-300 mb-4">{finding.description}</p>
            
            <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">Impact</h4>
            <p className="text-sm text-slate-700 dark:text-slate-300 mb-4">{finding.impact}</p>
            
            <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">Remediation</h4>
            <p className="text-sm text-slate-700 dark:text-slate-300">{finding.remediation}</p>
          </SectionCard>

          {ev && (
            <SectionCard title="Proof of Exploit">
              <div className="p-4 bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-500/20 rounded-sm mb-6 flex items-start gap-3">
                <ShieldAlert className="text-amber-600 dark:text-amber-500 shrink-0 mt-0.5" size={20} />
                <div>
                  <h4 className="text-sm font-semibold text-amber-900 dark:text-amber-400">Verification Logic</h4>
                  <p className="text-sm text-amber-800 dark:text-amber-300/80 mt-1">{ev.proof_text}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-bold bg-slate-200 dark:bg-zinc-700 text-slate-700 dark:text-slate-300 px-2 py-1 rounded-sm">
                      {ev.request_method}
                    </span>
                    <span className="text-sm font-mono text-slate-600 dark:text-slate-400">
                      {ev.request_url}
                    </span>
                  </div>
                  
                  {ev.request_body_redacted && Object.keys(ev.request_body_redacted).length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs text-slate-500 mb-1 font-semibold">Request Body (Redacted)</div>
                      <pre className="p-4 bg-slate-900 text-slate-50 rounded-sm text-xs overflow-x-auto font-mono shadow-inner">
                        {JSON.stringify(ev.request_body_redacted, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>

                <div className="pt-4 border-t border-slate-200 dark:border-white/10">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs font-bold px-2 py-1 rounded-sm ${ev.response_status >= 200 && ev.response_status < 300 ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}>
                      HTTP {ev.response_status}
                    </span>
                  </div>

                  {ev.response_body_redacted && (
                    <div className="mt-2">
                      <div className="text-xs text-slate-500 mb-1 font-semibold">Response Body (Redacted)</div>
                      <pre className="p-4 bg-slate-900 text-slate-50 rounded-sm text-xs overflow-x-auto font-mono shadow-inner max-h-[400px]">
                        {JSON.stringify(ev.response_body_redacted, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            </SectionCard>
          )}
        </div>

        <div className="space-y-6">
          <SectionCard title="Details">
            <div className="space-y-4 text-sm">
              <div>
                <div className="text-xs text-slate-500 mb-1">Status</div>
                <div className="font-medium capitalize">{finding.status.replace("_", " ")}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Confidence</div>
                <div className="font-medium capitalize flex items-center gap-2">
                  {finding.confidence === "confirmed" && <CheckCircle2 size={14} className="text-emerald-500" />}
                  {finding.confidence === "suspicious" && <AlertTriangle size={14} className="text-amber-500" />}
                  {finding.confidence}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Attacker Role</div>
                <div className="font-medium font-mono bg-slate-100 dark:bg-white/5 inline-block px-1.5 py-0.5 rounded-sm">
                  {finding.attacker_role || "none"}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Victim Role</div>
                <div className="font-medium font-mono bg-slate-100 dark:bg-white/5 inline-block px-1.5 py-0.5 rounded-sm">
                  {finding.victim_role || "none"}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-1">Detected At</div>
                <div className="font-medium">{new Date(finding.created_at).toLocaleString()}</div>
              </div>
              <div className="pt-2">
                <Link href={`/scans/${finding.scan_id}`} className="text-indigo-600 dark:text-indigo-400 hover:underline">
                  View Source Scan &rarr;
                </Link>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  )
}
