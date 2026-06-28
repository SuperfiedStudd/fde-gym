import Link from 'next/link'

import { getMissions, getProgress, safely } from '@/lib/api'

export const metadata = { title: 'Progress' }

export default async function ProgressPage() {
  const [missions, progress] = await Promise.all([
    safely(getMissions, []),
    safely(getProgress, { completed: {}, version: 1 }),
  ])

  return (
    <div className="page-shell">
      <div className="page-heading">
        <div><p className="eyebrow">OPERATOR READINESS</p><h1>Progress matrix</h1></div>
        <div className="page-heading-copy">
          <p>Completion is a record, not a score. Keep the evidence and tradeoffs in your story bank.</p>
          <p className="manual-progress-note">Progress is manually recorded after local evaluator success.</p>
        </div>
      </div>
      <div className="level-matrix">
        {(['LV1', 'LV2', 'LV3', 'LV4'] as const).map((level) => {
          const levelMissions = missions.filter((mission) => mission.level === level)
          const done = levelMissions.filter((mission) => progress.completed[mission.id]).length
          const percent = levelMissions.length ? (done / levelMissions.length) * 100 : 0
          return (
            <section className="panel" key={level}>
              <div className="matrix-head"><span className="level-code">{level}</span><strong>{done}/{levelMissions.length}</strong></div>
              <div className="progress-track"><span style={{ width: `${percent}%` }} /></div>
              <ul>
                {levelMissions.map((mission) => (
                  <li key={mission.id} className={progress.completed[mission.id] ? 'done' : ''}>
                    <span>{progress.completed[mission.id] ? '✓' : '○'}</span>
                    <Link href={`/missions/${mission.id}`}>{mission.title}</Link>
                  </li>
                ))}
              </ul>
            </section>
          )
        })}
      </div>
    </div>
  )
}

