"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { fetchApi } from "@/lib/api-client"
import { type Project } from "@/lib/types"
import { PageHeader } from "@/components/flowshield/page-header"
import { SectionCard } from "@/components/flowshield/section-card"

export default function NewProjectPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    base_url: "",
    environment_type: "local"
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const project = await fetchApi<Project>("/projects", {
        method: "POST",
        body: JSON.stringify(formData)
      })
      router.push(`/projects/${project.id}`)
    } catch (err: any) {
      setError(err.message || "An error occurred")
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <PageHeader 
        title="New Project" 
        description="Configure a new API target for security testing."
      />

      <SectionCard>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-sm bg-red-50 dark:bg-red-500/10 p-4 border border-red-200 dark:border-red-500/20">
              <div className="text-sm text-red-700 dark:text-red-400">{error}</div>
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-slate-900 dark:text-slate-300 mb-2">Project Name</label>
            <input 
              type="text" 
              required
              className="w-full rounded-sm border border-slate-300 dark:border-white/10 bg-white dark:bg-zinc-900 px-4 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="e.g. Core Banking API"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-900 dark:text-slate-300 mb-2">Target Base URL</label>
            <input 
              type="url" 
              required
              className="w-full rounded-sm border border-slate-300 dark:border-white/10 bg-white dark:bg-zinc-900 px-4 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
              value={formData.base_url}
              onChange={(e) => setFormData({...formData, base_url: e.target.value})}
              placeholder="https://api.example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-900 dark:text-slate-300 mb-2">Environment Type</label>
            <select 
              className="w-full rounded-sm border border-slate-300 dark:border-white/10 bg-white dark:bg-zinc-900 px-4 py-2 text-sm text-slate-900 dark:text-white focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              value={formData.environment_type}
              onChange={(e) => setFormData({...formData, environment_type: e.target.value})}
            >
              <option value="local">Local Development</option>
              <option value="lab">Test Lab</option>
              <option value="staging">Staging</option>
              <option value="bug_bounty">Bug Bounty / Production</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-900 dark:text-slate-300 mb-2">Description (Optional)</label>
            <textarea 
              className="w-full rounded-sm border border-slate-300 dark:border-white/10 bg-white dark:bg-zinc-900 px-4 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 h-24"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-200 dark:border-white/10">
            <button
              type="button"
              onClick={() => router.back()}
              className="rounded-sm px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={loading}
              className="rounded-sm bg-indigo-600 px-6 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-indigo-500 disabled:opacity-50"
            >
              {loading ? "Creating..." : "Create Project"}
            </button>
          </div>
        </form>
      </SectionCard>
    </div>
  )
}
