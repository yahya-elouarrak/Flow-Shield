import Link from "next/link";
import { FlowShieldLogo } from "@/components/flowshield/logo";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-[#020814]">
      <div className="z-10 w-full max-w-5xl items-center justify-center flex flex-col gap-8 text-center">
        <div className="flex justify-center scale-150 mb-8">
          <FlowShieldLogo />
        </div>
        
        <p className="text-xl md:text-2xl text-[#8B9AAF] max-w-3xl font-light tracking-tight">
          Secure APIs. <span className="font-medium text-[#13D8E5]">Protect business flows.</span>
        </p>
        
        <p className="text-base text-[#8B9AAF] max-w-2xl">
          AI-Assisted Grey-Box API Security and Business Logic Testing Platform.
        </p>

        <div className="mt-12">
          <Link 
            href="/dashboard" 
            className="rounded-sm bg-fs-accent-cyan px-8 py-2.5 text-sm font-medium tracking-wide text-white shadow-sm transition-all hover:opacity-90"
          >
            Go to Dashboard &rarr;
          </Link>
        </div>
      </div>
    </main>
  );
}
