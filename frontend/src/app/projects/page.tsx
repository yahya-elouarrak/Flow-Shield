"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { fetchApi } from "@/lib/api-client"
import { type Project } from "@/lib/types"
import { PageHeader } from "@/components/flowshield/page-header"
import { EmptyState } from "@/components/flowshield/empty-state"
import { StatusBadge } from "@/components/flowshield/status-badge"
import { FolderKanban, Trash2, AlertTriangle } from "lucide-react"

export default function ProjectsPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const loadProjects = () => {
    setLoading(true)
    fetchApi<Project[]>("/projects")
      .then(data => setProjects(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadProjects()
  }, [])

  const confirmDelete = async () => {
    if (!projectToDelete) return
    setIsDeleting(true)
    setDeleteError(null)
    try {
      await fetchApi(`/projects/${projectToDelete.id}`, { method: "DELETE" })
      setProjectToDelete(null)
      loadProjects()
    } catch (err: any) {
      setDeleteError(err.message || "Failed to delete project")
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div>
      <PageHeader 
        title="Projects" 
        description="Manage your testing workspaces and API targets."
        action={
          <Link 
            href="/projects/new" 
            className="rounded-sm bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Create Project
          </Link>
        }
      />

      {loading ? (
        <div className="text-sm text-slate-500">Loading projects...</div>
      ) : projects.length === 0 ? (
        <EmptyState 
          title="No projects found" 
          description="Get started by creating a new testing project."
          icon={<FolderKanban size={24} />}
          action={
            <Link href="/projects/new" className="text-sm font-semibold text-indigo-600 dark:text-indigo-400">
              Create Project &rarr;
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div 
              key={project.id} 
              onClick={() => router.push(`/projects/${project.id}`)}
              className="group rounded-sm border border-slate-200 dark:border-white/10 bg-white dark:bg-zinc-900/50 p-6 shadow-sm transition-all hover:border-slate-300 dark:hover:border-white/20 block cursor-pointer relative"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {project.name}
                </h3>
                <div className="flex items-center gap-3">
                  <StatusBadge status={project.environment_type} />
                  <button 
                    onClick={(e) => { e.stopPropagation(); setProjectToDelete(project); }}
                    className="text-slate-400 hover:text-red-500 transition-colors"
                    title="Delete project"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400 truncate mb-4 font-mono">
                {project.base_url}
              </p>
              <div className="text-xs text-slate-400">
                Created: {new Date(project.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {projectToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-zinc-900 rounded-sm shadow-xl max-w-md w-full border border-slate-200 dark:border-white/10 overflow-hidden">
            <div className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 bg-red-100 dark:bg-red-500/10 text-red-600 dark:text-red-400 rounded-sm">
                  <AlertTriangle size={24} />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Delete Project</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
                    Are you sure you want to delete <strong>{projectToDelete.name}</strong>? This action cannot be undone and will remove all associated target configurations, endpoints, scans, and findings.
                  </p>
                  
                  {deleteError && (
                    <div className="mb-4 p-3 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-sm text-sm text-red-600 dark:text-red-400">
                      {deleteError}
                    </div>
                  )}
                  
                  <div className="flex justify-end gap-3 mt-6">
                    <button 
                      onClick={() => {
                        if (!isDeleting) {
                          setProjectToDelete(null)
                          setDeleteError(null)
                        }
                      }}
                      disabled={isDeleting}
                      className="px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 rounded-sm disabled:opacity-50"
                    >
                      Cancel
                    </button>
                    <button 
                      onClick={confirmDelete}
                      disabled={isDeleting}
                      className="px-4 py-2 text-sm font-semibold text-white bg-red-600 hover:bg-red-500 rounded-sm disabled:opacity-50 flex items-center gap-2"
                    >
                      {isDeleting ? "Deleting..." : "Delete Project"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
