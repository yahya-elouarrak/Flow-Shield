import Image from "next/image"

export function FlowShieldLogo({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center ${className}`}>
      <Image 
        src="/images/logo_lockup_transparent.png" 
        alt="FlowShield Logo" 
        width={140} 
        height={32}
        className="object-contain"
        priority
      />
    </div>
  )
}
