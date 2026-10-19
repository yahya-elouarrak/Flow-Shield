"use client"

import { PageHeader } from "@/components/flowshield/page-header"
import { MetricCard } from "@/components/flowshield/metric-card"
import { SectionCard } from "@/components/flowshield/section-card"
import { ShieldAlert, FolderKanban, Activity, Bug } from "lucide-react"
import { EmptyState } from "@/components/flowshield/empty-state"
import Link from "next/link"
import { useEffect, useState } from "react"
import { fetchApi } from "@/lib/api-client"

interface ProjectSummary {
  id: string;
  name: string;
  created_at: string;
  description?: string;
}

interface FindingSummary {
  id: string;
  project_id: string;
  title: string;
  severity: string;
  category: string;
  created_at: string;
}

interface DashboardStats {
  total_projects: number;
  active_scans: number;
  high_severity_findings: number;
  total_findings: number;
  recent_projects: ProjectSummary[];
  recent_findings: FindingSummary[];
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchApi<DashboardStats>("/dashboard/stats");
        setStats(data);
      } catch (error) {
        console.error("Failed to load dashboard stats", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadStats();
  }, []);

  return (
    <div>
      <PageHeader 
        title="Dashboard" 
        description="Overview of your API security posture and active test environments."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard title="Total Projects" value={isLoading ? "..." : stats?.total_projects ?? 0} icon={<FolderKanban size={20} />} />
        <MetricCard title="Active Scans" value={isLoading ? "..." : stats?.active_scans ?? 0} icon={<Activity size={20} />} />
        <MetricCard title="High Severity Findings" value={isLoading ? "..." : stats?.high_severity_findings ?? 0} icon={<ShieldAlert size={20} className="text-red-500" />} />
        <MetricCard title="Total Findings" value={isLoading ? "..." : stats?.total_findings ?? 0} icon={<Bug size={20} />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <SectionCard title="Recent Projects" action={<Link href="/projects" className="text-sm font-medium text-fs-accent-cyan hover:opacity-80">View All</Link>}>
          {isLoading ? (
            <div className="flex justify-center items-center h-48 text-zinc-500 text-sm">Loading projects...</div>
          ) : stats?.recent_projects && stats.recent_projects.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_projects.map((project) => (
                <div key={project.id} className="p-4 rounded border border-zinc-800 bg-zinc-900/50 flex justify-between items-center">
                  <div>
                    <h3 className="font-medium text-white">{project.name}</h3>
                    <p className="text-xs text-zinc-400 mt-1">Created {new Date(project.created_at).toLocaleDateString()}</p>
                  </div>
                  <Link href={`/projects/${project.id}`} className="text-xs font-medium text-fs-accent-cyan px-3 py-1.5 border border-fs-accent-cyan/30 rounded hover:bg-fs-accent-cyan/10 transition-colors">
                    View
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState 
              title="No projects yet" 
              description="Create your first testing workspace to start scanning APIs."
              action={
                <Link href="/projects/new" className="rounded-sm bg-fs-accent-cyan px-4 py-2 text-sm font-medium tracking-wide text-white hover:opacity-90 transition-opacity shadow-sm">
                  Create Project
                </Link>
              }
            />
          )}
        </SectionCard>

        <SectionCard title="Recent Findings">
          {isLoading ? (
            <div className="flex justify-center items-center h-48 text-zinc-500 text-sm">Loading findings...</div>
          ) : stats?.recent_findings && stats.recent_findings.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_findings.map((finding) => (
                <div key={finding.id} className="p-4 rounded border border-zinc-800 bg-zinc-900/50 flex justify-between items-center">
                  <div className="truncate pr-4 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                        finding.severity.toLowerCase() === 'critical' ? 'bg-red-500/20 text-red-400' :
                        finding.severity.toLowerCase() === 'high' ? 'bg-orange-500/20 text-orange-400' :
                        finding.severity.toLowerCase() === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {finding.severity}
                      </span>
                      <span className="text-xs text-zinc-400">{finding.category}</span>
                    </div>
                    <h3 className="font-medium text-sm text-white truncate">{finding.title}</h3>
                  </div>
                  <Link href={`/projects/${finding.project_id}/findings/${finding.id}`} className="text-xs font-medium text-fs-accent-cyan px-3 py-1.5 border border-fs-accent-cyan/30 rounded hover:bg-fs-accent-cyan/10 transition-colors whitespace-nowrap">
                    Details
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState 
              title="No findings" 
              description="Run a scan to detect vulnerabilities and business logic flaws."
              icon={<ShieldAlert size={24} />}
            />
          )}
        </SectionCard>
      </div>
    </div>
  )
}
