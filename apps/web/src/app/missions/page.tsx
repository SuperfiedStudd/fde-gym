import { MissionExplorer } from '@/components/mission-explorer'
import { getMissions, getProgress, safely } from '@/lib/api'

export const metadata = { title: 'Missions' }

export default async function MissionsPage() {
  const [missions, progress] = await Promise.all([
    safely(getMissions, []),
    safely(getProgress, { completed: {}, version: 1 }),
  ])
  return (
    <div className="page-shell">
      <div className="page-heading">
        <div>
          <p className="eyebrow">OPERATION BACKLOG / {missions.length.toString().padStart(2, '0')}</p>
          <h1>Mission queue</h1>
        </div>
        <p>Choose a failure mode, inspect the brief, then work entirely in your editor and terminal.</p>
      </div>
      {missions.length ? (
        <MissionExplorer missions={missions} progress={progress} />
      ) : (
        <div className="panel empty-state">Mission API unavailable. Start `api` and reload.</div>
      )}
    </div>
  )
}

