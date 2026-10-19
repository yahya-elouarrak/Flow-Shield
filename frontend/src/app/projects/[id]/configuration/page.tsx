"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { fetchApi } from "@/lib/api-client"
import { type Project, type TargetConfig, type Role, type Account, type AuthConfig, type LoginTestResult } from "@/lib/types"
import { SectionCard } from "@/components/flowshield/section-card"
import { EmptyState } from "@/components/flowshield/empty-state"
import {
  Users, Plus, Trash2, Play, CheckCircle2, XCircle, Loader2, KeyRound, Save, AlertTriangle, Check, Info
} from "lucide-react"

const inputCls = "rounded-sm border border-slate-300 dark:border-white/10 bg-white dark:bg-zinc-900 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 w-full"
const btnPrimary = "rounded-sm bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50 flex items-center gap-2"
const btnDanger = "text-red-600 dark:text-red-400 hover:text-red-500"
const btnGhost = "rounded-sm border border-slate-200 dark:border-white/10 px-3 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5 flex items-center gap-2"

export default function ConfigurationPage() {
  const params = useParams()
  const projectId = params.id as string

  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("target")

  // Target Config
  const [project, setProject] = useState<Project | null>(null)
  const [config, setConfig] = useState<TargetConfig | null>(null)
  const [savingTarget, setSavingTarget] = useState(false)
  const [targetSaved, setTargetSaved] = useState(false)

  // Auth Config & Accounts
  const [roles, setRoles] = useState<Role[]>([])
  const [accounts, setAccounts] = useState<Account[]>([])
  
  const [newRoleName, setNewRoleName] = useState("")
  const [newRoleLevel, setNewRoleLevel] = useState("1")
  const [newRoleDesc, setNewRoleDesc] = useState("")

  const [newAccLabel, setNewAccLabel] = useState("")
  const [newAccUsername, setNewAccUsername] = useState("")
  const [newAccSecret, setNewAccSecret] = useState("")
  const [newAccRoleId, setNewAccRoleId] = useState("")
  const [newAccAuthType, setNewAccAuthType] = useState("password")

  const [acForm, setAcForm] = useState({
    auth_type: "jwt", login_endpoint: "/auth/login", method: "POST",
    username_field: "email", password_field: "password",
    token_json_path: "access_token", header_template: "Bearer {token}",
    refresh_endpoint: "",
  })
  const [acSaving, setAcSaving] = useState(false)
  const [acSaved, setAcSaved] = useState(false)

  const [testingId, setTestingId] = useState<string | null>(null)
  const [testingAll, setTestingAll] = useState(false)
  const [testResults, setTestResults] = useState<Record<string, LoginTestResult>>({})

  const [readiness, setReadiness] = useState<any>(null)
  const [demoSetupLoading, setDemoSetupLoading] = useState(false)
  const [crapiSetupLoading, setCrapiSetupLoading] = useState(false)

  const [wordlists, setWordlists] = useState<{name: string, size_bytes: number}[]>([])
  const [uploadingWordlist, setUploadingWordlist] = useState(false)

  const fetchAll = async () => {
    try {
      const [p, c, r, a, ac, rd, wl] = await Promise.all([
        fetchApi<Project>(`/projects/${projectId}`),
        fetchApi<TargetConfig>(`/projects/${projectId}/target-config`).catch(() => null),
        fetchApi<Role[]>(`/projects/${projectId}/roles`),
        fetchApi<Account[]>(`/projects/${projectId}/accounts`),
        fetchApi<AuthConfig | null>(`/projects/${projectId}/auth-config`),
        fetchApi<any>(`/projects/${projectId}/readiness`).catch(() => null),
        fetchApi<any[]>(`/wordlists`).catch(() => [])
      ])
      
      setProject(p)
      if (c) setConfig(c)
      setRoles(r)
      setAccounts(a)
      if (ac) {
        setAcForm({
          auth_type: ac.auth_type, login_endpoint: ac.login_endpoint || "",
          method: ac.method, username_field: ac.username_field,
          password_field: ac.password_field, token_json_path: ac.token_json_path,
          header_template: ac.header_template, refresh_endpoint: ac.refresh_endpoint || "",
        })
      }
      if (rd) setReadiness(rd)
      if (wl) setWordlists(wl)
    } catch { }
    setLoading(false)
  }

  useEffect(() => { fetchAll() }, [projectId])

  const saveTargetConfig = async () => {
    if (!project || !config) return
    setSavingTarget(true)
    setTargetSaved(false)
    try {
      await fetchApi(`/projects/${projectId}`, { method: "PATCH", body: JSON.stringify({ base_url: project.base_url }) })
      await fetchApi(`/projects/${projectId}/target-config`, { method: "PATCH", body: JSON.stringify(config) })
      setTargetSaved(true)
      setTimeout(() => setTargetSaved(false), 3000)
      fetchAll()
    } finally {
      setSavingTarget(false)
    }
  }

  const saveAuthConfig = async () => {
    setAcSaving(true); setAcSaved(false)
    await fetchApi(`/projects/${projectId}/auth-config`, { method: "PATCH", body: JSON.stringify(acForm) })
    setAcSaving(false); setAcSaved(true)
    fetchAll()
    setTimeout(() => setAcSaved(false), 3000)
  }

  const addRole = async () => {
    if (!newRoleName.trim()) return
    await fetchApi(`/projects/${projectId}/roles`, {
      method: "POST",
      body: JSON.stringify({ name: newRoleName, level: parseInt(newRoleLevel) || 1, description: newRoleDesc || null }),
    })
    setNewRoleName(""); setNewRoleLevel("1"); setNewRoleDesc("")
    fetchAll()
  }

  const deleteRole = async (id: string) => {
    await fetchApi(`/projects/${projectId}/roles/${id}`, { method: "DELETE" })
    fetchAll()
  }

  const addAccount = async () => {
    if (!newAccLabel.trim() || !newAccUsername.trim()) return
    await fetchApi(`/projects/${projectId}/accounts`, {
      method: "POST",
      body: JSON.stringify({
        label: newAccLabel, username: newAccUsername, secret: newAccSecret || null,
        role_id: newAccRoleId || null, auth_type: newAccAuthType,
      }),
    })
    setNewAccLabel(""); setNewAccUsername(""); setNewAccSecret(""); setNewAccRoleId("")
    fetchAll()
  }

  const deleteAccount = async (id: string) => {
    await fetchApi(`/projects/${projectId}/accounts/${id}`, { method: "DELETE" })
    fetchAll()
  }

  const testLogin = async (accountId: string) => {
    setTestingId(accountId)
    try {
      const result = await fetchApi<LoginTestResult>(`/projects/${projectId}/accounts/${accountId}/login-test`, { method: "POST" })
      setTestResults(prev => ({ ...prev, [accountId]: result }))
    } catch (err: any) {
      setTestResults(prev => ({ ...prev, [accountId]: { account_id: accountId, account_label: "", success: false, masked_token: null, error: err.message } }))
    }
    setTestingId(null)
    fetchAll()
  }

  const testAllLogins = async () => {
    setTestingAll(true)
    try {
      const results = await fetchApi<LoginTestResult[]>(`/projects/${projectId}/auth/test`, { method: "POST" })
      const map: Record<string, LoginTestResult> = {}
      results.forEach(r => { map[r.account_id] = r })
      setTestResults(map)
    } catch { }
    setTestingAll(false)
    fetchAll()
  }

  const runMiniSubSetup = async () => {
    setDemoSetupLoading(true)
    try {
      await fetchApi(`/projects/${projectId}/demo/minisub-setup`, { method: "POST" })
      await fetchAll()
    } catch (err: any) {
      console.error("Failed to run minisub setup:", err)
      alert("Setup failed: " + (err.message || "Unknown error"))
    } finally {
      setDemoSetupLoading(false)
    }
  }

  const runCrapiSetup = async () => {
    setCrapiSetupLoading(true)
    try {
      await fetchApi(`/projects/${projectId}/demo/crapi-setup`, { method: "POST" })
      await fetchAll()
    } catch (err: any) {
      console.error("Failed to run crapi setup:", err)
      alert("Setup failed: " + (err.message || "Unknown error"))
    } finally {
      setCrapiSetupLoading(false)
    }
  }

  const handleUploadWordlist = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setUploadingWordlist(true)
    try {
      const formData = new FormData()
      formData.append("file", file)
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/wordlists/upload`, {
        method: "POST",
        body: formData
      })
      if (!res.ok) throw new Error("Upload failed")
      
      const wl = await fetchApi<any[]>(`/wordlists`).catch(() => [])
      if (wl) setWordlists(wl)
    } catch (err: any) {
      alert("Failed to upload: " + err.message)
    } finally {
      setUploadingWordlist(false)
      if (e.target) e.target.value = ''
    }
  }

  if (loading) return <div className="text-sm text-slate-500 p-4">Loading configuration...</div>

  const tabs = [
    { id: "target", label: "Target API" },
    { id: "auth", label: "Authentication" },
    { id: "roles", label: "Roles & Accounts" },
    { id: "safety", label: "Scope & Safety" },
    { id: "wordlists", label: "Discovery Wordlists" },
    { id: "readiness", label: "Readiness Check" },
  ]

  return (
    <div>
      <div className="mb-6 flex gap-4 overflow-x-auto pb-2 border-b border-slate-200 dark:border-white/10">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`whitespace-nowrap pb-2 text-sm font-medium ${activeTab === t.id ? 'text-indigo-600 border-b-2 border-indigo-600 dark:text-indigo-400' : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="space-y-8">
        
        {/* Banners for Demos */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30 rounded-sm p-4 flex flex-col justify-between h-full">
            <div>
              <h4 className="font-semibold text-indigo-900 dark:text-indigo-300">Testing against the MiniSub Demo Lab?</h4>
              <p className="text-sm text-indigo-700 dark:text-indigo-400/80 mt-1 mb-4">One-click configure Target URL, Roles, and seeded Test Accounts.</p>
            </div>
            <button onClick={runMiniSubSetup} disabled={demoSetupLoading || crapiSetupLoading} className={btnPrimary + " w-fit"}>
              {demoSetupLoading ? <Loader2 className="animate-spin" size={16} /> : <Play size={16} />}
              Configure MiniSub Demo
            </button>
          </div>

          <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800/30 rounded-sm p-4 flex flex-col justify-between h-full">
            <div>
              <h4 className="font-semibold text-emerald-900 dark:text-emerald-300">Testing against the crAPI Demo Lab?</h4>
              <p className="text-sm text-emerald-700 dark:text-emerald-400/80 mt-1 mb-4">One-click configure JWT Auth, Roles, and auto-seed Test Accounts directly in crAPI.</p>
            </div>
            <button onClick={runCrapiSetup} disabled={crapiSetupLoading || demoSetupLoading} className={`rounded-sm bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-50 flex items-center gap-2 w-fit`}>
              {crapiSetupLoading ? <Loader2 className="animate-spin" size={16} /> : <Play size={16} />}
              Configure crAPI Demo
            </button>
          </div>
        </div>

        {activeTab === "target" && (
          <SectionCard title="Target Configuration" action={
            <button onClick={saveTargetConfig} disabled={savingTarget} className={btnPrimary}>
              {savingTarget ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
              {targetSaved ? "Saved ✓" : "Save Target Config"}
            </button>
          }>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-xs font-medium text-slate-500 mb-1">Target API Base URL</label>
                  <input type="text" className={inputCls} value={project?.base_url || ""} onChange={(e) => setProject(p => p ? { ...p, base_url: e.target.value } : p)} />
                  <p className="text-xs text-slate-400 mt-1">The URL where your target API is hosted (e.g. http://vulnerable-saas:9000)</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Allowed Hosts (comma separated)</label>
                  <input type="text" className={inputCls} value={config?.allowed_hosts?.join(", ") || ""} onChange={(e) => setConfig(c => c ? { ...c, allowed_hosts: e.target.value.split(",").map(s => s.trim()).filter(Boolean) } : c)} />
                </div>
              </div>
            </div>
          </SectionCard>
        )}

        {activeTab === "auth" && (
          <SectionCard title="Authentication Configuration" action={
            <button onClick={saveAuthConfig} disabled={acSaving} className={btnPrimary}>
              {acSaving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
              {acSaved ? "Saved ✓" : "Save Auth Config"}
            </button>
          }>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Auth Type</label>
                <select value={acForm.auth_type} onChange={e => setAcForm(f => ({ ...f, auth_type: e.target.value }))} className={inputCls}>
                  <option value="jwt">JWT (Bearer Token)</option>
                  <option value="api_key">API Key</option>
                  <option value="none">None</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Login Endpoint</label>
                <input value={acForm.login_endpoint} onChange={e => setAcForm(f => ({ ...f, login_endpoint: e.target.value }))} placeholder="/auth/login" className={inputCls} />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">HTTP Method</label>
                <select value={acForm.method} onChange={e => setAcForm(f => ({ ...f, method: e.target.value }))} className={inputCls}>
                  <option value="POST">POST</option>
                  <option value="GET">GET</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Username Field Name</label>
                <input value={acForm.username_field} onChange={e => setAcForm(f => ({ ...f, username_field: e.target.value }))} placeholder="email" className={inputCls} />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Password Field Name</label>
                <input value={acForm.password_field} onChange={e => setAcForm(f => ({ ...f, password_field: e.target.value }))} placeholder="password" className={inputCls} />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Token JSON Path</label>
                <input value={acForm.token_json_path} onChange={e => setAcForm(f => ({ ...f, token_json_path: e.target.value }))} placeholder="access_token" className={inputCls} />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Header Template</label>
                <input value={acForm.header_template} onChange={e => setAcForm(f => ({ ...f, header_template: e.target.value }))} placeholder="Bearer {token}" className={inputCls} />
              </div>
            </div>
          </SectionCard>
        )}

        {activeTab === "roles" && (
          <div className="space-y-8">
            <SectionCard title="Roles">
              {roles.length > 0 && (
                <div className="overflow-x-auto -mx-6 mb-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-white/10 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                        <th className="px-6 py-3">Name</th>
                        <th className="px-6 py-3 w-20 text-center">Level</th>
                        <th className="px-6 py-3">Description</th>
                        <th className="px-6 py-3 w-16"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                      {roles.map(r => (
                        <tr key={r.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02]">
                          <td className="px-6 py-3 font-medium text-slate-900 dark:text-white">{r.name}</td>
                          <td className="px-6 py-3 text-center text-slate-500">{r.level}</td>
                          <td className="px-6 py-3 text-slate-500">{r.description || "—"}</td>
                          <td className="px-6 py-3">
                            <button onClick={() => deleteRole(r.id)} className={btnDanger}><Trash2 size={14} /></button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <div className="flex gap-3 items-end">
                <div className="flex-1">
                  <label className="block text-xs font-medium text-slate-500 mb-1">Name</label>
                  <input value={newRoleName} onChange={e => setNewRoleName(e.target.value)} placeholder="e.g. customer" className={inputCls} />
                </div>
                <div className="w-20">
                  <label className="block text-xs font-medium text-slate-500 mb-1">Level</label>
                  <input type="number" value={newRoleLevel} onChange={e => setNewRoleLevel(e.target.value)} className={inputCls} />
                </div>
                <button onClick={addRole} className={btnPrimary}><Plus size={14} /> Add Role</button>
              </div>
            </SectionCard>

            <SectionCard title="Test Accounts" action={
              accounts.length > 0 ? (
                <button onClick={testAllLogins} disabled={testingAll} className={btnGhost}>
                  {testingAll ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                  Test All Logins
                </button>
              ) : null
            }>
              {accounts.length > 0 && (
                <div className="overflow-x-auto -mx-6 mb-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-white/10 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                        <th className="px-6 py-3">Label</th>
                        <th className="px-6 py-3">Username</th>
                        <th className="px-6 py-3">Role</th>
                        <th className="px-6 py-3 text-center">Secret</th>
                        <th className="px-6 py-3">Status</th>
                        <th className="px-6 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                      {accounts.map(acc => {
                        const result = testResults[acc.id]
                        const status = result ? (result.success ? "success" : "error") : acc.login_status
                        return (
                          <tr key={acc.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02]">
                            <td className="px-6 py-3 font-medium text-slate-900 dark:text-white">{acc.label}</td>
                            <td className="px-6 py-3 font-mono text-slate-600 dark:text-slate-400">{acc.username}</td>
                            <td className="px-6 py-3">
                              {acc.role_name ? <span className="px-1.5 py-0.5 rounded-sm text-xs bg-indigo-100 text-indigo-700">{acc.role_name}</span> : "—"}
                            </td>
                            <td className="px-6 py-3 text-center">
                              {acc.has_secret ? <KeyRound size={14} className="inline text-emerald-500" /> : "—"}
                            </td>
                            <td className="px-6 py-3">
                              {status === "success" && <div className="text-emerald-600 flex items-center gap-1"><CheckCircle2 size={14}/> OK</div>}
                              {status === "error" && <div className="text-red-600 flex items-center gap-1"><XCircle size={14}/> Error</div>}
                              {!status && <span className="text-slate-400">Untested</span>}
                            </td>
                            <td className="px-6 py-3">
                              <div className="flex items-center gap-2">
                                <button onClick={() => testLogin(acc.id)} disabled={testingId === acc.id} className={btnGhost}>Test</button>
                                <button onClick={() => deleteAccount(acc.id)} className={btnDanger}><Trash2 size={14} /></button>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}
              <div className="border-t border-slate-100 dark:border-white/5 pt-4 mt-4 grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Label</label>
                  <input value={newAccLabel} onChange={e => setNewAccLabel(e.target.value)} placeholder="customer_a" className={inputCls} />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Username / Email</label>
                  <input value={newAccUsername} onChange={e => setNewAccUsername(e.target.value)} placeholder="a@ex.com" className={inputCls} />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Password</label>
                  <input type="password" value={newAccSecret} onChange={e => setNewAccSecret(e.target.value)} placeholder="••••••••" className={inputCls} />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Role</label>
                  <select value={newAccRoleId} onChange={e => setNewAccRoleId(e.target.value)} className={inputCls}>
                    <option value="">No role</option>
                    {roles.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                  </select>
                </div>
                <button onClick={addAccount} className={btnPrimary}><Plus size={14} /> Add</button>
              </div>
            </SectionCard>
          </div>
        )}

        {activeTab === "safety" && (
          <SectionCard title="Scope & Safety" action={
            <button onClick={saveTargetConfig} disabled={savingTarget} className={btnPrimary}>
              {savingTarget ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
              {targetSaved ? "Saved ✓" : "Save Safety Config"}
            </button>
          }>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h4 className="text-sm font-semibold mb-3">Rate Limiting</h4>
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Rate Limit (req/sec)</label>
                    <input type="number" className={inputCls} value={config?.max_requests_per_second || 0} onChange={(e) => setConfig(c => c ? { ...c, max_requests_per_second: parseInt(e.target.value) || 0 } : c)} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Max Total Requests Per Scan</label>
                    <input type="number" className={inputCls} value={config?.max_total_requests || 0} onChange={(e) => setConfig(c => c ? { ...c, max_total_requests: parseInt(e.target.value) || 0 } : c)} />
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-semibold mb-3">Test Behaviors</h4>
                <div className="space-y-3">
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded text-indigo-600" checked={config?.allow_destructive_tests || false} onChange={(e) => setConfig(c => c ? { ...c, allow_destructive_tests: e.target.checked } : c)} />
                    Allow Destructive Tests (Creates, Modifies)
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded text-indigo-600" checked={config?.allow_delete_requests || false} onChange={(e) => setConfig(c => c ? { ...c, allow_delete_requests: e.target.checked } : c)} />
                    Allow DELETE Requests
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded text-indigo-600" checked={config?.allow_payment_tests || false} onChange={(e) => setConfig(c => c ? { ...c, allow_payment_tests: e.target.checked } : c)} />
                    Allow Payment Flows
                  </label>
                </div>
              </div>
            </div>
          </SectionCard>
        )}

        {activeTab === "wordlists" && (
          <SectionCard title="Discovery Wordlists" action={
            <button onClick={saveTargetConfig} disabled={savingTarget} className={btnPrimary}>
              {savingTarget ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
              {targetSaved ? "Saved ✓" : "Save Config"}
            </button>
          }>
            <div className="space-y-6">
              <p className="text-sm text-slate-500">
                Select a wordlist to be used by the discovery engines (e.g. searching for hidden parameters or undocumented endpoints).
              </p>
              
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Selected Wordlist</label>
                <select 
                  className={inputCls} 
                  value={config?.selected_wordlist || ""} 
                  onChange={(e) => setConfig(c => c ? { ...c, selected_wordlist: e.target.value || null } : c)}
                >
                  <option value="">-- Use Engine Defaults --</option>
                  {wordlists.map(w => (
                    <option key={w.name} value={w.name}>{w.name} ({(w.size_bytes / 1024).toFixed(1)} KB)</option>
                  ))}
                </select>
              </div>

              <div className="border-t border-slate-200 dark:border-white/10 pt-6 mt-6">
                <h4 className="text-sm font-medium mb-3">Upload Custom Wordlist</h4>
                <div className="flex items-center gap-3">
                  <input 
                    type="file" 
                    accept=".txt" 
                    onChange={handleUploadWordlist} 
                    disabled={uploadingWordlist}
                    className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-sm file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 dark:file:bg-indigo-900/30 dark:file:text-indigo-400 dark:hover:file:bg-indigo-800/30"
                  />
                  {uploadingWordlist && <Loader2 className="animate-spin text-indigo-500" size={20} />}
                </div>
              </div>
            </div>
          </SectionCard>
        )}

        {activeTab === "readiness" && (
          <SectionCard title="Pre-Scan Readiness">
            {readiness ? (
              <div className="space-y-4">
                <div className={`p-4 rounded-sm border ${readiness.ready ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'}`}>
                  <h4 className={`text-lg font-semibold ${readiness.ready ? 'text-emerald-700' : 'text-red-700'}`}>
                    {readiness.ready ? "✓ Project is ready to scan" : "⚠ Project configuration incomplete"}
                  </h4>
                  <p className="text-sm mt-1 text-slate-600">Review the checks below to ensure a successful security scan.</p>
                </div>
                
                <div className="divide-y divide-slate-100 dark:divide-white/5 border border-slate-200 dark:border-white/10 rounded-sm">
                  {readiness.checks.map((check: any) => (
                    <div key={check.key} className="p-4 flex items-start gap-3">
                      {check.status === "pass" && <CheckCircle2 className="text-emerald-500 shrink-0 mt-0.5" size={18} />}
                      {check.status === "fail" && <XCircle className="text-red-500 shrink-0 mt-0.5" size={18} />}
                      {check.status === "warning" && <AlertTriangle className="text-amber-500 shrink-0 mt-0.5" size={18} />}
                      
                      <div>
                        <h5 className="font-semibold text-sm text-slate-900 dark:text-white">{check.label}</h5>
                        <p className="text-sm text-slate-500">{check.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-4 text-sm text-slate-500">Run a check to see readiness...</div>
            )}
          </SectionCard>
        )}

      </div>
    </div>
  )
}
