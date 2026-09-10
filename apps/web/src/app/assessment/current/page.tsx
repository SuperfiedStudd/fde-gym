import Link from 'next/link'
import { notFound } from 'next/navigation'
import ReactMarkdown from 'react-markdown'

import { AssessmentTimer } from '@/components/assessment-timer'
import { getCurrentAssessment } from '@/lib/assessment'

export const dynamic = 'force-dynamic'

export default async function CurrentAssessmentPage() {
  const assessment = await getCurrentAssessment()
  if (!assessment) notFound()

  return (
    <div className="page-shell detail-shell assessment-detail">
      <Link href="/assessment" className="back-link">← assessment mode</Link>
      <div className="assessment-heading">
        <div>
          <p className="eyebrow">CURRENT ASSESSMENT / {assessment.id}</p>
          <h1>{assessment.title}</h1>
          <div className="assessment-meta">
            <span>{assessment.duration_minutes} minutes</span>
            <span>{assessment.difficulty}</span>
            {assessment.focus.map((item) => <span key={item}>{item}</span>)}
          </div>
        </div>
        <AssessmentTimer
          assessmentId={assessment.id}
          durationMinutes={assessment.duration_minutes}
        />
      </div>

      <div className="detail-grid assessment-content-grid">
        <article className="mission-brief assessment-prompt">
          <ReactMarkdown>{assessment.prompt}</ReactMarkdown>
        </article>
        <aside>
          <div className="panel sticky-panel assessment-resources">
            <p className="eyebrow">AVAILABLE RESOURCES / {assessment.resources.length}</p>
            {assessment.resources.length ? (
              <ul>
                {assessment.resources.map((resource) => (
                  <li key={resource.path}>
                    <div>
                      <strong>{resource.label}</strong>
                      {resource.description ? <p>{resource.description}</p> : null}
                      <code>{resource.path}</code>
                    </div>
                    <div className="resource-actions">
                      <a
                        href={`/assessment/current/resources/view/${encodeURIComponent(resource.path)}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open
                      </a>
                      <a
                        href={`/assessment/current/resources/${encodeURIComponent(resource.path)}?download=1`}
                        download={resource.path}
                      >
                        Download
                      </a>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-state">No additional resources supplied.</p>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
