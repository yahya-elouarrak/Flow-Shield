"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { fetchApi } from "@/lib/api-client"
import { type Project, type TargetConfig } from "@/lib/types"
import { PageHeader } from "@/components/flowshield/page-header"
import { SectionCard } from "@/components/flowshield/section-card"
import { StatusBadge } from "@/components/flowshield/status-badge"
import { ShieldAlert, Globe, Crosshair, Network, FileCode2, FileText } from "lucide-react"

export default function ProjectDetailPage() {
  const params = useParams()
  const id = params.id as string
  
  const [project, setProject] = useState<Project | null>(null)
  const [config, setConfig] = useState<TargetConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const projData = await fetchApi<Project>(`/projects/${id}`)
        setProject(projData)
        
        try {
          const confData = await fetchApi<TargetConfig>(`/projects/${id}/target-config`)
          setConfig(confData)
        } catch (e) {
          // It's possible target config is missing, which is handled gracefully
        }
      } catch (err: any) {
        setError(err.message || "Failed to load project")
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  if (loading) return <div className="text-sm text-slate-500">Loading project details...</div>
  if (error) return <div className="text-sm text-red-500">{error}</div>
  if (!project) return <div className="text-sm text-slate-500">Project not found.</div>

  return (
    <div>
      <div className="mb-6">
        <Link href="/projects" className="text-sm text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
          &larr; Back to Projects
        </Link>
      </div>

      <PageHeader 
        title={project.name}
        description={project.description || "No description provided."}
        action={<StatusBadge status={project.environment_type} />}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Link href={`/projects/${id}/endpoints`} className="group">
          <SectionCard className="h-full hover:border-indigo-500/50 transition-colors cursor-pointer">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-sm bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                <Network size={20} />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">API Inventory</h3>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">Manage OpenAPI specs and discovered endpoints.</p>
          </SectionCard>
        </Link>
        
        <Link href={`/projects/${id}/scan`} className="group">
          <SectionCard className="h-full hover:border-emerald-500/50 transition-colors cursor-pointer">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-sm bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                <Crosshair size={20} />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">New Scan</h3>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">Launch AI-assisted BOLA and logic tests.</p>
          </SectionCard>
        </Link>
        
        <Link href={`/projects/${id}/findings`} className="group">
          <SectionCard className="h-full hover:border-red-500/50 transition-colors cursor-pointer">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-sm bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400">
                <ShieldAlert size={20} />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors">Findings</h3>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">View verified security vulnerabilities.</p>
          </SectionCard>
        </Link>

        <Link href={`/projects/${id}/reports`} className="group">
          <SectionCard className="h-full hover:border-slate-400 transition-colors cursor-pointer">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-sm bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400">
                <FileText size={20} />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-slate-600 transition-colors">Reports</h3>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">Export PDF, HTML, and JSON findings.</p>
          </SectionCard>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <SectionCard 
            title="Target Configuration" 
            action={<Link href={`/projects/${id}/configuration`} className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">Edit</Link>}
          >
            {config ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 flex items-center gap-2">
                      <Globe size={14} /> Base URL
                    </div>
                    <div className="text-sm font-mono text-slate-900 dark:text-slate-300">{project.base_url}</div>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Allowed Hosts</div>
                    <div className="text-sm font-mono text-slate-900 dark:text-slate-300">
                      {config.allowed_hosts.join(", ") || "None"}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Rate Limit</div>
                    <div className="text-sm text-slate-900 dark:text-slate-300">
                      {config.max_requests_per_second} req/sec (Max: {config.max_total_requests})
                    </div>
                  </div>
                </div>

                <div className="border-t border-slate-200 dark:border-white/10 pt-6">
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">Safety Boundaries</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className={`p-4 rounded-sm border ${config.allow_destructive_tests ? 'bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30' : 'bg-slate-50 dark:bg-zinc-900/50 border-slate-200 dark:border-white/10'}`}>
                      <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Destructive Tests</div>
                      <div className={`font-semibold text-sm ${config.allow_destructive_tests ? 'text-red-700 dark:text-red-400' : 'text-slate-900 dark:text-slate-300'}`}>
                        {config.allow_destructive_tests ? "ALLOWED" : "BLOCKED"}
                      </div>
                    </div>
                    <div className={`p-4 rounded-sm border ${config.allow_delete_requests ? 'bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30' : 'bg-slate-50 dark:bg-zinc-900/50 border-slate-200 dark:border-white/10'}`}>
                      <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">DELETE Requests</div>
                      <div className={`font-semibold text-sm ${config.allow_delete_requests ? 'text-red-700 dark:text-red-400' : 'text-slate-900 dark:text-slate-300'}`}>
                        {config.allow_delete_requests ? "ALLOWED" : "BLOCKED"}
                      </div>
                    </div>
                    <div className={`p-4 rounded-sm border ${config.allow_payment_tests ? 'bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30' : 'bg-slate-50 dark:bg-zinc-900/50 border-slate-200 dark:border-white/10'}`}>
                      <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Payment Flows</div>
                      <div className={`font-semibold text-sm ${config.allow_payment_tests ? 'text-red-700 dark:text-red-400' : 'text-slate-900 dark:text-slate-300'}`}>
                        {config.allow_payment_tests ? "ALLOWED" : "BLOCKED"}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500">No configuration found.</p>
            )}
          </SectionCard>
        </div>
        
        <div className="space-y-6">
          <SectionCard title="Recent Activity">
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <ShieldAlert size={24} className="text-slate-300 dark:text-slate-600 mb-2" />
              <p className="text-sm text-slate-500">No scans run yet.</p>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  )
}
