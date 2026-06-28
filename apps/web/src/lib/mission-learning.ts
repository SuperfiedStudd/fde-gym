import type { MissionDetail } from '@/lib/api'

export type LearningHint = {
  level: 1 | 2 | 3
  title: string
  body: string
}

export type SystemArea = {
  name: string
  description: string
  sourceCount: number
}

export type MissionLearningGuide = {
  studyQuestions: string[]
  systemAreas: SystemArea[]
  files: string[]
  hints: LearningHint[]
  cursorPrompt: string
}

type AreaDefinition = Omit<SystemArea, 'sourceCount'> & {
  matches: (file: string) => boolean
}

const AREA_DEFINITIONS: AreaDefinition[] = [
  {
    name: 'Web cockpit',
    description: 'Operator-facing Next.js UI and browser interactions.',
    matches: (file) => file.startsWith('apps/web/'),
  },
  {
    name: 'ClaimOps API',
    description: 'FastAPI request boundaries, domain services, and persistence calls.',
    matches: (file) => file.startsWith('apps/api/'),
  },
  {
    name: 'Async worker',
    description: 'Queued work, retry behavior, and background processing.',
    matches: (file) => file.startsWith('apps/worker/'),
  },
  {
    name: 'Data layer',
    description: 'PostgreSQL schema, queries, indexes, and safe migrations.',
    matches: (file) =>
      file.includes('postgres') || file.includes('/migrations/') || file.startsWith('scripts/migrations/'),
  },
  {
    name: 'Observability',
    description: 'Metrics, logs, dashboards, and operational signals.',
    matches: (file) => file.includes('metrics') || file.includes('prometheus'),
  },
  {
    name: 'Delivery runtime',
    description: 'CI, service configuration, and local runtime orchestration.',
    matches: (file) =>
      file.startsWith('.github/') || file === 'docker-compose.yml' || file.includes('service configuration'),
  },
  {
    name: 'Mission evidence',
    description: 'Technical notes, runbooks, incident evidence, and design decisions.',
    matches: (file) => file.startsWith('missions/'),
  },
  {
    name: 'Focused evaluator',
    description: 'The tests that define observable success for this mission.',
    matches: (file) => file.startsWith('tests/'),
  },
]

function extractListSection(markdown: string, heading: string): string[] {
  const lines = markdown.split(/\r?\n/)
  const start = lines.findIndex((line) => line.trim() === `## ${heading}`)
  if (start < 0) return []

  const items: string[] = []
  for (const line of lines.slice(start + 1)) {
    if (line.startsWith('## ')) break
    const match = line.match(/^\s*-\s+(.+)$/)
    if (match) items.push(match[1].replace(/^`([^`]+)`$/, '$1'))
  }
  return items
}

function buildSystemAreas(files: string[]): SystemArea[] {
  const normalizedFiles = files.map((file) => file.toLowerCase())
  const areas = AREA_DEFINITIONS.flatMap(({ matches, ...area }) => {
    const sourceCount = normalizedFiles.filter(matches).length
    return sourceCount ? [{ ...area, sourceCount }] : []
  })

  return areas.length
    ? areas
    : [{ name: 'Mission brief', description: 'Use the brief to identify the affected runtime boundary.', sourceCount: 1 }]
}

export function buildMissionLearningGuide(mission: MissionDetail): MissionLearningGuide {
  const listedFiles = extractListSection(mission.brief, 'Files likely involved')
  const files = listedFiles.length ? listedFiles : [`missions/${mission.readme_path}`]
  const reflectionQuestions = extractListSection(mission.brief, 'Interview reflection questions')
  const primaryFile = files[0]
  const testFile = files.find((file) => file.startsWith('tests/'))
  const traceTarget = files.find((file) => file !== primaryFile && !file.startsWith('tests/')) ?? testFile
  const evaluatorSignals = mission.checks.join(', ')

  const studyQuestions = [
    `What contract or invariant should ${mission.skill.toLowerCase()} protect in this scenario?`,
    reflectionQuestions[0] ?? `Where should this failure be contained before it affects another service?`,
    `Before editing, which evaluator signal do you expect to fail first: ${evaluatorSignals}?`,
  ]

  const hints: LearningHint[] = [
    {
      level: 1,
      title: 'Concept hint',
      body: `Frame this as a ${mission.skill.toLowerCase()} problem. Name the invariant implied by “${mission.summary}” and decide which layer should own it before looking for a code change.`,
    },
    {
      level: 2,
      title: 'Debugging direction',
      body: `Start at ${primaryFile}${traceTarget ? ` and trace the behavior toward ${traceTarget}` : ''}. Look for the earliest point where actual behavior can diverge from the brief; do not patch a later symptom first.`,
    },
    {
      level: 3,
      title: 'Test-focused hint',
      body: `Read ${testFile ?? 'the focused evaluator'} before editing. Group its expectations around ${evaluatorSignals}, then make the smallest hypothesis-driven change and rerun only this mission's evaluator.`,
    },
  ]

  const cursorPrompt = `You are my tutor for FDE Gym mission ${mission.id}: ${mission.title}.

Teaching rules:
- Do not solve the mission automatically.
- Teach the concept first.
- Ask me what I think before suggesting edits.
- Reveal hints gradually.
- Explain the failing test before code.
- Never paste the final answer unless I explicitly ask.
- Keep all MISSION_BUG(...) markers.
- Do not change acceptance criteria unless there is a scaffold typo.

Mission context:
- Skill: ${mission.skill}
- Goal: ${mission.summary}
- Open first: ${files.join(', ')}
- Evaluator signals: ${evaluatorSignals}

Start by teaching the core concept in plain language. Then ask what I think is failing and wait for my answer before suggesting any edit.`

  return {
    studyQuestions,
    systemAreas: buildSystemAreas(files),
    files,
    hints,
    cursorPrompt,
  }
}
