import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

import { ThemeProvider } from "next-themes";
import { AppShell } from "@/components/layout/app-shell";
import { BackgroundPattern } from "@/components/flowshield/background-pattern";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FlowShield | AI-Assisted API Security",
  description: "Grey-box API security and business logic testing platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning className={`${inter.className} text-slate-900 dark:text-slate-100 min-h-screen antialiased selection:bg-cyan-500/30`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <BackgroundPattern />
          <AppShell>
            {children}
          </AppShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
