"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { fetchApi } from "@/lib/api-client"
import { type EndpointDetail } from "@/lib/types"
import { PageHeader } from "@/components/flowshield/page-header"
import { SectionCard } from "@/components/flowshield/section-card"
import { MethodBadge } from "@/components/flowshield/method-badge"
import { CodeBlock } from "@/components/flowshield/code-block"
import { Lock, Unlock, AlertTriangle } from "lucide-react"

export default function EndpointDetailPage() {
  const params = useParams()
  const projectId = params.id as string
  const endpointId = params.endpointId as string

  const [endpoint, setEndpoint] = useState<EndpointDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchApi<EndpointDetail>(`/projects/${projectId}/openapi/endpoints/${endpointId}`)
      .then(setEndpoint)
      .catch((err) => setError(err.message || "Failed to load endpoint"))
      .finally(() => setLoading(false))
  }, [projectId, endpointId])

  if (loading) return <div className="text-sm text-slate-500">Loading endpoint...</div>
  if (error) return <div className="text-sm text-red-500">{error}</div>
  if (!endpoint) return <div className="text-sm text-slate-500">Endpoint not found.</div>

  return (
    <div>
      <div className="mb-6">
        <Link href={`/projects/${projectId}/endpoints`} className="text-sm text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
          &larr; Back to API Inventory
        </Link>
      </div>

      <PageHeader
        title={endpoint.path}
        description={endpoint.summary || endpoint.operation_id || undefined}
        action={<MethodBadge method={endpoint.method} />}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Overview */}
        <div className="lg:col-span-2 space-y-6">
          <SectionCard title="Overview">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Method</div>
                <MethodBadge method={endpoint.method} />
              </div>
              <div>
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Auth Required</div>
                <div className="flex items-center gap-1.5 text-sm">
                  {endpoint.auth_required
                    ? <><Lock size={14} className="text-amber-500" /> <span className="text-amber-600 dark:text-amber-400 font-medium">Yes</span></>
                    : <><Unlock size={14} className="text-slate-400" /> <span className="text-slate-500">No</span></>
                  }
                </div>
              </div>
              <div>
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Operation ID</div>
                <div className="text-sm font-mono text-slate-900 dark:text-slate-300">{endpoint.operation_id || "—"}</div>
              </div>
              <div>
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Tags</div>
                <div className="flex flex-wrap gap-1">
                  {(endpoint.tags || []).length > 0 ? endpoint.tags.map((tag) => (
                    <span key={tag} className="px-1.5 py-0.5 rounded-sm text-xs bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-white/10">{tag}</span>
                  )) : <span className="text-sm text-slate-400">—</span>}
                </div>
              </div>
            </div>
            {endpoint.description && (
              <div className="mt-6 pt-6 border-t border-slate-200 dark:border-white/10">
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">Description</div>
                <p className="text-sm text-slate-700 dark:text-slate-300">{endpoint.description}</p>
              </div>
            )}
          </SectionCard>

          {/* Parameters */}
          {endpoint.parameters_json && endpoint.parameters_json.length > 0 && (
            <SectionCard title="Parameters">
              <div className="overflow-x-auto -mx-6 -mb-6">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-white/10 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      <th className="px-6 py-3">Name</th>
                      <th className="px-6 py-3">In</th>
                      <th className="px-6 py-3">Required</th>
                      <th className="px-6 py-3">Type</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                    {endpoint.parameters_json.map((p: any, i: number) => (
                      <tr key={i} className="hover:bg-slate-50 dark:hover:bg-white/[0.02]">
                        <td className="px-6 py-3 font-mono text-slate-900 dark:text-slate-200">{p.name}</td>
                        <td className="px-6 py-3 text-slate-500">{p.in}</td>
                        <td className="px-6 py-3 text-slate-500">{p.required ? "Yes" : "No"}</td>
                        <td className="px-6 py-3 text-slate-500 font-mono">{p.schema?.type || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </SectionCard>
          )}

          {/* Request Schema */}
          {endpoint.request_schema_json && (
            <SectionCard title="Request Body Schema">
              <CodeBlock code={endpoint.request_schema_json} language="json" />
            </SectionCard>
          )}

          {/* Response Schema */}
          {endpoint.response_schema_json && (
            <SectionCard title="Response Schema">
              <CodeBlock code={endpoint.response_schema_json} language="json" />
            </SectionCard>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Sensitive Score */}
          <SectionCard title="Sensitive Score">
            <div className="text-center">
              <div className={`text-4xl font-bold ${endpoint.sensitive_score >= 50 ? "text-rose-600 dark:text-rose-400" : endpoint.sensitive_score >= 25 ? "text-amber-600 dark:text-amber-400" : "text-emerald-600 dark:text-emerald-400"}`}>
                {endpoint.sensitive_score}
              </div>
              <div className="text-xs text-slate-500 mt-1">out of 100</div>

              <div className="w-full h-2 rounded-sm bg-slate-100 dark:bg-white/10 mt-4 overflow-hidden">
                <div
                  className={`h-full rounded-sm ${endpoint.sensitive_score >= 50 ? "bg-rose-500" : endpoint.sensitive_score >= 25 ? "bg-amber-500" : "bg-emerald-500"}`}
                  style={{ width: `${Math.min(endpoint.sensitive_score, 100)}%` }}
                />
              </div>
            </div>

            {endpoint.sensitive_reasons && endpoint.sensitive_reasons.length > 0 && (
              <div className="mt-6 pt-4 border-t border-slate-200 dark:border-white/10 space-y-2">
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">Reasons</div>
                {endpoint.sensitive_reasons.map((reason, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-400">
                    <AlertTriangle size={12} className="text-amber-500 mt-0.5 shrink-0" />
                    {reason}
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          {/* Quick Info */}
          <SectionCard title="Quick Info">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Path Params</span>
                <span className="font-mono text-slate-900 dark:text-slate-300">{endpoint.path_params?.join(", ") || "—"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Query Params</span>
                <span className="font-mono text-slate-900 dark:text-slate-300">{endpoint.query_params?.join(", ") || "—"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Body Fields</span>
                <span className="font-mono text-slate-900 dark:text-slate-300">{endpoint.body_fields?.join(", ") || "—"}</span>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  )
}
