"use client"

import { PageHeader } from "@/components/flowshield/page-header"
import { SectionCard } from "@/components/flowshield/section-card"

export default function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <PageHeader 
        title="Settings" 
        description="Global platform settings and AI configurations."
      />
      
      <div className="space-y-6">
        <SectionCard title="Ollama Configuration" description="Configure connection to your local or remote Ollama instance.">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-900 dark:text-slate-300 mb-2">Base URL</label>
              <input 
                type="text" 
                className="w-full max-w-md rounded-md border border-slate-300 dark:border-white/10 bg-white dark:bg-zinc-900 px-4 py-2 text-sm text-slate-900 dark:text-white"
                defaultValue="http://host.docker.internal:11434"
                disabled
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-900 dark:text-slate-300 mb-2">Default Model</label>
              <input 
                type="text" 
                className="w-full max-w-md rounded-md border border-slate-300 dark:border-white/10 bg-white dark:bg-zinc-900 px-4 py-2 text-sm text-slate-900 dark:text-white"
                defaultValue="qwen2.5-coder:7b"
                disabled
              />
            </div>
            <p className="text-xs text-slate-500">Note: Currently these must be configured via environment variables in docker-compose.yml.</p>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
