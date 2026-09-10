import { readFile } from 'node:fs/promises'
import path from 'node:path'
import Link from 'next/link'
import { notFound } from 'next/navigation'

import { getAssessmentRoot, getCurrentAssessment } from '@/lib/assessment'

export const dynamic = 'force-dynamic'

export default async function AssessmentResourcePage({
  params,
}: {
  params: Promise<{ path: string }>
}) {
  const { path: resourcePath } = await params
  const assessment = await getCurrentAssessment()
  const resource = assessment?.resources.find((item) => item.path === resourcePath)
  if (!assessment || !resource) notFound()

  let content: string
  try {
    content = await readFile(
      path.join(getAssessmentRoot(), 'resources', resource.path),
      'utf8',
    )
  } catch {
    notFound()
  }

  return (
    <div className="page-shell resource-view">
      <Link href="/assessment/current" className="back-link">← current assessment</Link>
      <div className="page-heading">
        <div>
          <p className="eyebrow">ASSESSMENT RESOURCE / {resource.path}</p>
          <h1>{resource.label}</h1>
        </div>
        {resource.description ? <p>{resource.description}</p> : null}
      </div>
      <pre><code>{content}</code></pre>
    </div>
  )
}
