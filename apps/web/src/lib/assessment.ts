import 'server-only'

import { readFile } from 'node:fs/promises'
import path from 'node:path'

export type AssessmentResource = {
  path: string
  label: string
  description?: string
}

export type Assessment = {
  id: string
  title: string
  duration_minutes: number
  difficulty: string
  focus: string[]
  resources: AssessmentResource[]
  prompt: string
}

const manifestFields = [
  'id',
  'title',
  'duration_minutes',
  'difficulty',
  'focus',
  'resources',
] as const

export function getAssessmentRoot(): string {
  return process.env.ASSESSMENT_ROOT ?? path.resolve(process.cwd(), '../../assessment/current')
}

function nonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0
}

function parseResource(value: unknown): AssessmentResource {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('Invalid assessment resource')
  }
  const resource = value as Record<string, unknown>
  const fields = Object.keys(resource)
  if (
    !fields.every((field) => ['path', 'label', 'description'].includes(field)) ||
    !nonEmptyString(resource.path) ||
    path.basename(resource.path) !== resource.path ||
    !nonEmptyString(resource.label) ||
    (resource.description !== undefined && !nonEmptyString(resource.description))
  ) {
    throw new Error('Invalid assessment resource')
  }
  return {
    path: resource.path,
    label: resource.label,
    ...(resource.description ? { description: resource.description as string } : {}),
  }
}

function parseManifest(value: unknown): Omit<Assessment, 'prompt'> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('Invalid assessment manifest')
  }
  const manifest = value as Record<string, unknown>
  if (
    Object.keys(manifest).length !== manifestFields.length ||
    !manifestFields.every((field) => field in manifest) ||
    !nonEmptyString(manifest.id) ||
    !nonEmptyString(manifest.title) ||
    !Number.isInteger(manifest.duration_minutes) ||
    (manifest.duration_minutes as number) <= 0 ||
    !nonEmptyString(manifest.difficulty) ||
    !Array.isArray(manifest.focus) ||
    manifest.focus.length === 0 ||
    !manifest.focus.every(nonEmptyString) ||
    !Array.isArray(manifest.resources)
  ) {
    throw new Error('Invalid assessment manifest')
  }
  return {
    id: manifest.id,
    title: manifest.title,
    duration_minutes: manifest.duration_minutes as number,
    difficulty: manifest.difficulty,
    focus: manifest.focus,
    resources: manifest.resources.map(parseResource),
  }
}

export async function getCurrentAssessment(): Promise<Assessment | null> {
  const root = getAssessmentRoot()
  try {
    const [manifestText, prompt] = await Promise.all([
      readFile(path.join(root, 'assessment.json'), 'utf8'),
      readFile(path.join(root, 'prompt.md'), 'utf8'),
    ])
    const manifest = parseManifest(JSON.parse(manifestText) as unknown)
    await Promise.all(
      manifest.resources.map((resource) => readFile(path.join(root, 'resources', resource.path))),
    )
    return { ...manifest, prompt }
  } catch {
    return null
  }
}
