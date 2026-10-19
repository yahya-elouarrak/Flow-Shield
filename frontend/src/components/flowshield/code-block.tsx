import { cn } from "@/lib/utils"

interface CodeBlockProps {
  code: string | object
  language?: string
  className?: string
}

export function CodeBlock({ code, language = "json", className }: CodeBlockProps) {
  const displayCode = typeof code === "string" ? code : JSON.stringify(code, null, 2)
  
  return (
    <div className={cn("rounded-sm border border-fs-border bg-[#020814] overflow-hidden", className)}>
      <div className="flex items-center px-3 py-1.5 border-b border-fs-border bg-[#061224] text-[10px] font-mono text-fs-muted uppercase tracking-widest">
        {language}
      </div>
      <pre className="p-3 overflow-x-auto text-[11px] leading-relaxed font-mono text-[#F8FAFC]">
        <code>{displayCode}</code>
      </pre>
    </div>
  )
}
