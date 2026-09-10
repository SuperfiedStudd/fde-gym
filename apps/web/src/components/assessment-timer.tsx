'use client'

import { useEffect, useState } from 'react'

type AssessmentTimerProps = {
  assessmentId: string
  durationMinutes: number
}

export function AssessmentTimer({ assessmentId, durationMinutes }: AssessmentTimerProps) {
  const durationSeconds = durationMinutes * 60
  const [remaining, setRemaining] = useState(durationSeconds)

  useEffect(() => {
    const storageKey = `fde-gym:assessment:${assessmentId}:ends-at`
    const storedEnd = Number(window.sessionStorage.getItem(storageKey))
    const endsAt = storedEnd > Date.now() ? storedEnd : Date.now() + durationSeconds * 1000
    window.sessionStorage.setItem(storageKey, String(endsAt))

    const update = () => {
      setRemaining(Math.max(0, Math.ceil((endsAt - Date.now()) / 1000)))
    }
    update()
    const interval = window.setInterval(update, 1000)
    return () => window.clearInterval(interval)
  }, [assessmentId, durationSeconds])

  const minutes = Math.floor(remaining / 60)
  const seconds = remaining % 60

  return (
    <div className={`assessment-timer${remaining === 0 ? ' assessment-timer-expired' : ''}`}>
      <span>Time remaining</span>
      <strong>{minutes.toString().padStart(2, '0')}:{seconds.toString().padStart(2, '0')}</strong>
    </div>
  )
}
