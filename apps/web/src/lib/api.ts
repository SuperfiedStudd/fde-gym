import type { Mission, Progress } from '@fde-gym/shared'

export type MissionDetail = Mission & { brief: string }

export type SystemHealth = {
  generated_at: string
  overall: 'healthy' | 'degraded' | 'critical'
  queue_depth: number
  error_rate: number
  p95_latency_ms: number
  components: Record<
    string,
    { status: 'healthy' | 'degraded' | 'critical'; latency_ms: number; detail?: string }
  >
}

const API_URL = process.env.API_INTERNAL_URL ?? 'http://localhost:8000'

async function apiFetch<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: 'no-store' })
  if (!response.ok) throw new Error(`ClaimOps API ${path} returned ${response.status}`)
  return response.json() as Promise<T>
}

export async function getMissions(): Promise<Mission[]> {
  return apiFetch<Mission[]>('/missions')
}

export async function getMission(id: string): Promise<MissionDetail> {
  return apiFetch<MissionDetail>(`/missions/${encodeURIComponent(id)}`)
}

export async function getProgress(): Promise<Progress> {
  return apiFetch<Progress>('/progress')
}

export async function getSystemHealth(): Promise<SystemHealth> {
  return apiFetch<SystemHealth>('/system/health')
}

export async function safely<T>(operation: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await operation()
  } catch {
    return fallback
  }
}

