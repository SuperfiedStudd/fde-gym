export type MissionLevel = 'LV1' | 'LV2' | 'LV3' | 'LV4'

export type Mission = {
  id: string
  title: string
  level: MissionLevel
  skill: string
  labels: string[]
  summary: string
  estimated_minutes: number
  checks: string[]
  readme_path: string
}

export type Progress = {
  completed: Record<string, { completed_at: string; notes?: string | null }>
  version: number
}

