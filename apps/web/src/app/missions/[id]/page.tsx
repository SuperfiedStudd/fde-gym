import Link from 'next/link'
import { notFound } from 'next/navigation'
import ReactMarkdown from 'react-markdown'

import { CompleteButton } from '@/components/complete-button'
import { getMission, getProgress, safely } from '@/lib/api'

export default async function MissionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const mission = await safely(() => getMission(id), null)
  if (!mission) notFound()
  const progress = await safely(getProgress, { completed: {}, version: 1 })
  const completed = Boolean(progress.completed[id])

  return (
    <div className="page-shell detail-shell">
      <Link href="/missions" className="back-link">← mission queue</Link>
      <div className="detail-heading">
        <div>
          <div className="mission-meta">
            <span className="level-code">{mission.level}</span>
            <span>{mission.skill}</span>
            <span>{mission.estimated_minutes}m estimated</span>
          </div>
          <h1>{mission.title}</h1>
          <p>{mission.summary}</p>
        </div>
        <CompleteButton missionId={id} completed={completed} />
      </div>

      <div className="detail-grid">
        <article className="mission-brief">
          <ReactMarkdown>{mission.brief}</ReactMarkdown>
        </article>
        <aside>
          <div className="panel sticky-panel">
            <p className="eyebrow">RUN CHECKS</p>
            <code className="command-block">python scripts/evaluate/run.py --mission {mission.id}</code>
            <p className="eyebrow aside-label">EVALUATOR SIGNALS</p>
            <ul className="check-list">
              {mission.checks.map((check) => <li key={check}>{check}</li>)}
            </ul>
            <p className="eyebrow aside-label">LABELS</p>
            <div className="labels">
              {mission.labels.map((label) => <span key={label}>{label}</span>)}
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

