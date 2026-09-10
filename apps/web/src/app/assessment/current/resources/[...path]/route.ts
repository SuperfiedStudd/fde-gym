import { readFile } from 'node:fs/promises'
import path from 'node:path'

import { getAssessmentRoot, getCurrentAssessment } from '@/lib/assessment'

export const dynamic = 'force-dynamic'

export async function GET(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path: segments } = await params
  if (segments.length !== 1) return new Response('Not found', { status: 404 })

  const assessment = await getCurrentAssessment()
  const resource = assessment?.resources.find((item) => item.path === segments[0])
  if (!resource) return new Response('Not found', { status: 404 })

  try {
    const content = await readFile(path.join(getAssessmentRoot(), 'resources', resource.path))
    const download = new URL(request.url).searchParams.has('download')
    const headers: Record<string, string> = {
      'Content-Type': contentTypeFor(resource.path),
      'X-Content-Type-Options': 'nosniff',
    }
    if (download) {
      headers['Content-Disposition'] = `attachment; filename="${resource.path.replaceAll('"', '')}"`
    }
    return new Response(content, {
      headers,
    })
  } catch {
    return new Response('Not found', { status: 404 })
  }
}

function contentTypeFor(filename: string): string {
  const extension = path.extname(filename).toLowerCase()
  return {
    '.csv': 'text/csv; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.md': 'text/markdown; charset=utf-8',
    '.txt': 'text/plain; charset=utf-8',
  }[extension] ?? 'application/octet-stream'
}
