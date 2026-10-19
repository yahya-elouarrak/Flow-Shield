"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { fetchApi } from "@/lib/api-client"
import { PageHeader } from "@/components/flowshield/page-header"
import { SectionCard } from "@/components/flowshield/section-card"
import { FileText, Download, Code, FileJson, AlertCircle, File } from "lucide-react"
import { API_BASE_URL } from "@/lib/api-client"

interface ScanJob {
  id: string
  status: string
  phase: string
  progress: number
  created_at: string
}

export default function ReportsPage() {
  const params = useParams()
  const projectId = params.id as string

  const [scans, setScans] = useState<ScanJob[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadScans() {
      try {
        const data = await fetchApi<ScanJob[]>(`/projects/${projectId}/scans`)
        setScans(Array.isArray(data) ? data : [])
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    loadScans()
  }, [projectId])

  const completedScans = scans.filter(s => s.status === 'completed')
  const latestScan = completedScans.length > 0 ? completedScans[0] : null

  const handleDownload = (format: 'html' | 'json' | 'markdown' | 'pdf', scanId?: string) => {
    let url = ''
    if (scanId) {
      url = `${API_BASE_URL}/scans/${scanId}/reports/${format}`
    } else {
      url = `${API_BASE_URL}/projects/${projectId}/reports/${format}`
    }
    
    // Create an invisible anchor element to trigger the download
    const a = document.createElement('a')
    a.href = url
    // Add target=_blank so HTML opens in a new tab if they don't force download
    if (format === 'html') {
      a.target = '_blank'
    } else {
      a.download = `flowshield-report-${format === 'markdown' ? 'md' : format}`
    }
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading reports...</div>
  }

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Security Reports" 
        description="Generate and download professional security assessment reports."
      />

      {error && (
        <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400 p-4 rounded-md flex items-center gap-2">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {completedScans.length === 0 ? (
        <SectionCard>
          <div className="text-center py-12">
            <div className="mx-auto w-12 h-12 bg-slate-100 dark:bg-white/5 rounded-full flex items-center justify-center text-slate-400 mb-4">
              <FileText size={24} />
            </div>
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No Reports Available</h3>
            <p className="text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
              You need to complete at least one security scan for this project before generating reports.
            </p>
          </div>
        </SectionCard>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <SectionCard title="Export Latest Project Report">
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
                Generate a comprehensive report based on the most recently completed scan ({latestScan?.id.split('-')[0]}). 
                This report includes all verified findings, evidence, and remediation advice.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <button 
                  onClick={() => handleDownload('html')}
                  className="flex flex-col items-center justify-center p-6 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 transition-colors group"
                >
                  <FileText className="w-8 h-8 text-indigo-500 mb-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-slate-900 dark:text-white">HTML Report</span>
                  <span className="text-xs text-slate-500 mt-1">Interactive Web format</span>
                </button>

                <button 
                  onClick={() => handleDownload('json')}
                  className="flex flex-col items-center justify-center p-6 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg hover:border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 transition-colors group"
                >
                  <FileJson className="w-8 h-8 text-emerald-500 mb-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-slate-900 dark:text-white">JSON Data</span>
                  <span className="text-xs text-slate-500 mt-1">Machine-readable</span>
                </button>

                <button 
                  onClick={() => handleDownload('markdown')}
                  className="flex flex-col items-center justify-center p-6 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg hover:border-amber-500 hover:bg-amber-50 dark:hover:bg-amber-500/10 transition-colors group"
                >
                  <Code className="w-8 h-8 text-amber-500 mb-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-slate-900 dark:text-white">Markdown</span>
                  <span className="text-xs text-slate-500 mt-1">Documentation format</span>
                </button>

                <button 
                  onClick={() => handleDownload('pdf')}
                  className="flex flex-col items-center justify-center p-6 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg hover:border-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors group"
                >
                  <File className="w-8 h-8 text-rose-500 mb-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-slate-900 dark:text-white">PDF Document</span>
                  <span className="text-xs text-slate-500 mt-1">Print-ready format</span>
                </button>
              </div>
            </SectionCard>

            <SectionCard title="Scan History Reports">
              <div className="space-y-4">
                {completedScans.slice(0, 5).map((scan) => (
                  <div key={scan.id} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-white/5 rounded-lg border border-slate-100 dark:border-white/5">
                    <div>
                      <div className="font-medium text-slate-900 dark:text-white flex items-center gap-2">
                        Scan {scan.id.split('-')[0]}
                        {scan.id === latestScan?.id && (
                          <span className="px-2 py-0.5 text-[10px] font-medium bg-indigo-100 text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-400 rounded">LATEST</span>
                        )}
                      </div>
                      <div className="text-xs text-slate-500">Completed on {new Date(scan.created_at).toLocaleString()}</div>
                    </div>
                    <div className="flex gap-2">
                      <button 
                        onClick={() => handleDownload('html', scan.id)}
                        className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-500/20 rounded transition-colors"
                        title="Download HTML"
                      >
                        <FileText size={16} />
                      </button>
                      <button 
                        onClick={() => handleDownload('json', scan.id)}
                        className="p-2 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-500/20 rounded transition-colors"
                        title="Download JSON"
                      >
                        <FileJson size={16} />
                      </button>
                      <button 
                        onClick={() => handleDownload('pdf', scan.id)}
                        className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-500/20 rounded transition-colors"
                        title="Download PDF"
                      >
                        <File size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>

          <div className="space-y-6">
            <SectionCard title="About Reports">
              <div className="prose prose-sm dark:prose-invert">
                <p>FlowShield reports are automatically generated based on verified findings and deterministic evidence collected during scans.</p>
                
                <h4>Data Redaction</h4>
                <p>All sensitive information, such as authentication tokens, passwords, and PII found in HTTP payloads, are automatically redacted before being stored or presented in reports.</p>
                
                <h4>Evidence-Based</h4>
                <p>Our reports prioritize zero false positives. Every reported finding includes the exact HTTP request and response that proves the vulnerability exists.</p>
              </div>
            </SectionCard>
          </div>
        </div>
      )}
    </div>
  )
}
