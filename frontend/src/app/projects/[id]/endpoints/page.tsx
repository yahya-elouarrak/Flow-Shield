"use client"

import { useEffect, useState, useRef } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { fetchApi } from "@/lib/api-client"
import { type Endpoint, type UploadedSpec } from "@/lib/types"
import { SectionCard } from "@/components/flowshield/section-card"
import { EmptyState } from "@/components/flowshield/empty-state"
import { MethodBadge } from "@/components/flowshield/method-badge"
import { Network, Upload, Link as LinkIcon, Loader2, CheckCircle2, XCircle, Lock, Unlock, Trash2 } from "lucide-react"

export default function EndpointsPage() {
  const params = useParams()
  const projectId = params.id as string

  const [endpoints, setEndpoints] = useState<Endpoint[]>([])
  const [loading, setLoading] = useState(true)
  const [importMode, setImportMode] = useState<"url" | "file">("url")
  const [importUrl, setImportUrl] = useState("")
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<{ ok: boolean; message: string } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const fetchEndpoints = async () => {
    try {
      const data = await fetchApi<Endpoint[]>(`/projects/${projectId}/openapi/endpoints`)
      setEndpoints(data)
    } catch {
      setEndpoints([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEndpoints()
  }, [projectId])

  const handleImportUrl = async () => {
    if (!importUrl.trim()) return
    setImporting(true)
    setImportResult(null)

    try {
      await fetchApi<UploadedSpec>(`/projects/${projectId}/openapi/import-url`, {
        method: "POST",
        body: JSON.stringify({ url: importUrl }),
      })
      setImportResult({ ok: true, message: "Spec imported successfully." })
      setImportUrl("")
      setLoading(true)
      await fetchEndpoints()
    } catch (err: any) {
      setImportResult({ ok: false, message: err.message || "Import failed." })
    } finally {
      setImporting(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    setImportResult(null)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const resp = await fetch(`${API_BASE}/projects/${projectId}/openapi/upload`, {
        method: "POST",
        body: formData,
      })
      if (!resp.ok) {
        const errText = await resp.text()
        let msg = "Upload failed."
        try { msg = JSON.parse(errText).detail || msg } catch {}
        throw new Error(msg)
      }
      setImportResult({ ok: true, message: `File "${file.name}" imported successfully.` })
      setLoading(true)
      await fetchEndpoints()
    } catch (err: any) {
      setImportResult({ ok: false, message: err.message || "Upload failed." })
    } finally {
      setImporting(false)
      if (fileInputRef.current) fileInputRef.current.value = ""
    }
  }

  const handleDeleteAll = async () => {
    if (!confirm("Delete all imported endpoints for this project?")) return
    try {
      await fetchApi(`/projects/${projectId}/openapi/endpoints`, { method: "DELETE" })
      setEndpoints([])
      setImportResult({ ok: true, message: "All endpoints removed." })
    } catch (err: any) {
      setImportResult({ ok: false, message: err.message || "Delete failed." })
    }
  }

  return (
    <div>
      

      

      {/* Import Panel */}
      <SectionCard title="Import OpenAPI Specification" className="mb-8">
        <div className="space-y-4">
          {/* Tab Selector */}
          <div className="flex rounded-sm border border-slate-200 dark:border-white/10 w-fit">
            <button
              onClick={() => setImportMode("url")}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${importMode === "url" ? "bg-indigo-600 text-white" : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5"}`}
            >
              <LinkIcon size={14} /> From URL
            </button>
            <button
              onClick={() => setImportMode("file")}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors ${importMode === "file" ? "bg-indigo-600 text-white" : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5"}`}
            >
              <Upload size={14} /> Upload File
            </button>
          </div>

          {/* URL Import */}
          {importMode === "url" && (
            <div className="flex gap-3">
              <input
                type="text"
                value={importUrl}
                onChange={(e) => setImportUrl(e.target.value)}
                placeholder="e.g. http://vulnerable-saas:9000/openapi.json"
                className="flex-1 rounded-sm border border-slate-300 dark:border-white/10 bg-white dark:bg-zinc-900 px-4 py-2 text-sm font-mono text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                onKeyDown={(e) => e.key === "Enter" && handleImportUrl()}
              />
              <button
                onClick={handleImportUrl}
                disabled={importing || !importUrl.trim()}
                className="rounded-sm bg-indigo-600 px-6 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50 flex items-center gap-2"
              >
                {importing ? <Loader2 size={16} className="animate-spin" /> : null}
                Import
              </button>
            </div>
          )}

          {/* File Upload */}
          {importMode === "file" && (
            <div className="flex items-center gap-4">
              <input
                ref={fileInputRef}
                type="file"
                accept=".json,.yaml,.yml"
                onChange={handleFileUpload}
                className="block text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-sm file:border file:border-slate-200 dark:file:border-white/10 file:text-sm file:font-semibold file:bg-white dark:file:bg-zinc-900 file:text-slate-700 dark:file:text-slate-300 hover:file:bg-slate-50 dark:hover:file:bg-white/5 file:cursor-pointer file:transition-colors"
              />
              {importing && <Loader2 size={16} className="animate-spin text-indigo-500" />}
            </div>
          )}

          {/* Result feedback */}
          {importResult && (
            <div className={`flex items-center gap-2 rounded-sm p-3 text-sm border ${importResult.ok ? "bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400"}`}>
              {importResult.ok ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
              {importResult.message}
            </div>
          )}
        </div>
      </SectionCard>

      {/* Endpoint Inventory */}
      {loading ? (
        <div className="text-sm text-slate-500">Loading endpoints...</div>
      ) : endpoints.length === 0 ? (
        <EmptyState
          title="No endpoints discovered"
          description="Import an OpenAPI specification above to populate the inventory."
          icon={<Network size={24} />}
        />
      ) : (
        <SectionCard
          title={`Discovered Endpoints (${endpoints.length})`}
          action={
            <button onClick={handleDeleteAll} className="flex items-center gap-1.5 text-sm text-red-600 dark:text-red-400 hover:underline">
              <Trash2 size={14} /> Clear All
            </button>
          }
        >
          <div className="overflow-x-auto -mx-6 -mb-6">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-white/10 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  <th className="px-6 py-3 w-20">Method</th>
                  <th className="px-6 py-3">Path</th>
                  <th className="px-6 py-3 w-16 text-center">Auth</th>
                  <th className="px-6 py-3">Tags</th>
                  <th className="px-6 py-3 w-20 text-center">Params</th>
                  <th className="px-6 py-3 w-20 text-center">Body</th>
                  <th className="px-6 py-3 w-24 text-center">Sensitive</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                {endpoints.map((ep) => (
                  <tr key={ep.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-3">
                      <MethodBadge method={ep.method} />
                    </td>
                    <td className="px-6 py-3">
                      <Link
                        href={`/projects/${projectId}/endpoints/${ep.id}`}
                        className="font-mono text-slate-900 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                      >
                        {ep.path}
                      </Link>
                      {ep.summary && (
                        <div className="text-xs text-slate-400 dark:text-slate-500 mt-0.5 truncate max-w-xs">{ep.summary}</div>
                      )}
                    </td>
                    <td className="px-6 py-3 text-center">
                      {ep.auth_required
                        ? <Lock size={14} className="inline text-amber-500" />
                        : <Unlock size={14} className="inline text-slate-300 dark:text-slate-600" />
                      }
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex flex-wrap gap-1">
                        {(ep.tags || []).slice(0, 3).map((tag) => (
                          <span key={tag} className="px-1.5 py-0.5 rounded-sm text-xs bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-white/10">{tag}</span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-3 text-center text-slate-600 dark:text-slate-400">
                      {(ep.path_params?.length || 0) + (ep.query_params?.length || 0)}
                    </td>
                    <td className="px-6 py-3 text-center text-slate-600 dark:text-slate-400">
                      {ep.body_fields?.length || 0}
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-12 h-1.5 rounded-sm bg-slate-100 dark:bg-white/10 overflow-hidden">
                          <div
                            className={`h-full rounded-sm transition-all ${ep.sensitive_score >= 50 ? "bg-rose-500" : ep.sensitive_score >= 25 ? "bg-amber-500" : "bg-emerald-500"}`}
                            style={{ width: `${Math.min(ep.sensitive_score, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono text-slate-500">{ep.sensitive_score}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      )}
    </div>
  )
}
