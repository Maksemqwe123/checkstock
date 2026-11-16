import type { Snapshot } from './types'

const base = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '/api'

export async function fetchSnapshot(): Promise<Snapshot> {
  const res = await fetch(`${base}/inventory/snapshot`)
  if (!res.ok) {
    throw new Error(`API ${res.status}: не удалось загрузить сводку`)
  }
  return res.json() as Promise<Snapshot>
}