import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function maskSecret(secret: string): string {
  if (!secret) return ""
  if (secret.length <= 8) return "••••••••"
  return `${secret.slice(0, 4)}••••••••${secret.slice(-4)}`
}
