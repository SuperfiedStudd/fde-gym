import Link from 'next/link'
import { notFound } from 'next/navigation'
import ReactMarkdown from 'react-markdown'

import { CompleteButton } from '@/components/complete-button'
import { EvaluatorCommand } from '@/components/evaluator-command'
import { MissionLearning } from '@/components/mission-learning'
import { getMission, getProgress, safely } from '@/lib/api'
import { buildMissionLearningGuide } from '@/lib/mission-learning'

export default async function MissionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const mission = await safely(() => getMission(id), null)
  if (!mission) notFound()
  const progress = await safely(getProgress, { completed: {}, version: 1 })
  const completed = Boolean(progress.completed[id])
  const learningGuide = buildMissionLearningGuide(mission)

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
      </div>

      <MissionLearning guide={learningGuide} />

      <section className="evaluation-callout" aria-labelledby="evaluation-heading">
        <div className="evaluation-command">
          <p className="eyebrow">RUN BEFORE + AFTER</p>
          <h2 id="evaluation-heading">Prove the behavior locally.</h2>
          <p>Run once before solving to see the baseline, then run it again to verify your repair.</p>
          <EvaluatorCommand missionId={mission.id} />
        </div>
        <CompleteButton missionId={id} completed={completed} />
      </section>

      <div className="detail-grid">
        <article className="mission-brief">
          <ReactMarkdown>{mission.brief}</ReactMarkdown>
        </article>
        <aside>
          <div className="panel sticky-panel">
            <p className="eyebrow">RUN CHECKS</p>
            <EvaluatorCommand missionId={mission.id} compact />
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

