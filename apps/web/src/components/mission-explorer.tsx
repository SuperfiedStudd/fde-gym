'use client'

import type { Mission, Progress } from '@fde-gym/shared'
import Link from 'next/link'
import { useMemo, useState } from 'react'

type Props = { missions: Mission[]; progress: Progress }

export function MissionExplorer({ missions, progress }: Props) {
  const [level, setLevel] = useState('ALL')
  const [skill, setSkill] = useState('ALL')
  const skills = [...new Set(missions.map((mission) => mission.skill))].sort()
  const filtered = useMemo(
    () =>
      missions.filter(
        (mission) =>
          (level === 'ALL' || mission.level === level) &&
          (skill === 'ALL' || mission.skill === skill),
      ),
    [level, missions, skill],
  )

  return (
    <>
      <div className="filterbar">
        <label>
          <span>Level</span>
          <select value={level} onChange={(event) => setLevel(event.target.value)}>
            <option>ALL</option>
            {['LV1', 'LV2', 'LV3', 'LV4'].map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        </label>
        <label>
          <span>Skill</span>
          <select value={skill} onChange={(event) => setSkill(event.target.value)}>
            <option>ALL</option>
            {skills.map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        </label>
        <span className="result-count">{filtered.length.toString().padStart(2, '0')} tasks</span>
      </div>

      <div className="mission-grid">
        {filtered.map((mission) => {
          const completed = Boolean(progress.completed[mission.id])
          return (
            <Link className="mission-card" href={`/missions/${mission.id}`} key={mission.id}>
              <div className="mission-meta">
                <span className="level-code">{mission.level}</span>
                <span className={completed ? 'state-complete' : 'state-open'}>
                  {completed ? 'COMPLETE' : 'OPEN'}
                </span>
                <span>{mission.estimated_minutes}m</span>
              </div>
              <h2>{mission.title}</h2>
              <p>{mission.summary}</p>
              <div className="labels">
                {mission.labels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              <div className="mission-footer">
                <span>{mission.skill}</span>
                <span aria-hidden>↗</span>
              </div>
            </Link>
          )
        })}
      </div>
    </>
  )
}

