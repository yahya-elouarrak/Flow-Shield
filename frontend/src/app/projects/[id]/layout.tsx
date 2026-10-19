"use client"

import Link from "next/link"
import { usePathname, useParams } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { ReactNode } from "react"

export default function ProjectSubsectionsLayout({
  children,
}: {
  children: ReactNode,
}) {
  const pathname = usePathname()
  const params = useParams()
  const id = params?.id as string
  
  // Don't show the back button on the project overview page itself
  const isOverview = pathname === `/projects/${id}` || pathname === `/projects/${id}/`
  
  return (
    <>
      {!isOverview && (
        <div className="mb-6">
          <Link href={`/projects/${id}`} className="text-sm font-medium text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 flex items-center gap-1.5 w-fit transition-colors">
            <ArrowLeft size={16} /> Go back to Project Overview
          </Link>
        </div>
      )}
      {children}
    </>
  )
}
