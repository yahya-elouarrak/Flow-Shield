"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { fetchApi } from "@/lib/api-client"
import { type Finding } from "@/lib/types"
import { ShieldAlert, AlertCircle, AlertTriangle, Info, CheckCircle2, Search } from "lucide-react"

const severityColors = {
  critical: "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800",
  high: "bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800",
  medium: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800",
  low: "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800",
  info: "bg-slate-100 text-slate-800 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700"
}

const severityIcons = {
  critical: <AlertCircle size={14} />,
  high: <AlertTriangle size={14} />,
  medium: <AlertTriangle size={14} />,
  low: <Info size={14} />,
  info: <Info size={14} />
}

export default function FindingsPage() {
  const params = useParams()
  const projectId = params.id as string

  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchApi<Finding[]>(`/projects/${projectId}/findings`)
        setFindings(data)
      } catch (err: any) {
        setError(err.message || "Failed to load findings")
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [projectId])

  if (loading) return <div className="p-8 text-center text-slate-500 animate-pulse">Loading findings...</div>
  if (error) return <div className="p-8 text-center text-red-500">Error: {error}</div>

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        
        <div className="flex items-center text-sm text-slate-500">
          <ShieldAlert size={16} className="mr-2 text-indigo-500" />
          {findings.length} findings detected
        </div>
      </div>

      {findings.length === 0 ? (
        <div className="text-center p-12 border border-slate-200 dark:border-white/10 rounded-sm bg-slate-50/50 dark:bg-zinc-900/50">
          <CheckCircle2 size={48} className="mx-auto text-emerald-500 mb-4 opacity-50" />
          <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No findings yet</h3>
          <p className="text-slate-500">Launch a scan to discover security vulnerabilities in your API.</p>
          <Link href={`/projects/${projectId}/scan`} className="mt-6 inline-block px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-sm">
            Launch Scan
          </Link>
        </div>
      ) : (
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-white/10 rounded-sm overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 dark:bg-zinc-800/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-semibold">
                <tr>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3">Vulnerability</th>
                  <th className="px-4 py-3">Endpoint</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                {findings.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50 dark:hover:bg-zinc-800/50 transition-colors group">
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-xs font-medium border ${severityColors[f.severity]}`}>
                        {severityIcons[f.severity]}
                        <span className="capitalize">{f.severity}</span>
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-900 dark:text-white max-w-xs truncate" title={f.title}>
                      {f.title}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono font-bold bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded-sm">
                          {f.endpoint_method}
                        </span>
                        <span className="font-mono text-slate-600 dark:text-slate-400 truncate max-w-[200px]" title={f.endpoint_path}>
                          {f.endpoint_path}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`capitalize ${f.confidence === 'confirmed' ? 'text-emerald-600 dark:text-emerald-400 font-semibold' : 'text-amber-600 dark:text-amber-400'}`}>
                        {f.confidence}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="capitalize text-slate-500">{f.status.replace("_", " ")}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link 
                        href={`/findings/${f.id}`}
                        className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium"
                      >
                        <Search size={14} />
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
