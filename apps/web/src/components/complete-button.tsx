'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'

export function CompleteButton({ missionId, completed }: { missionId: string; completed: boolean }) {
  const [pending, setPending] = useState(false)
  const router = useRouter()

  async function complete() {
    setPending(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/progress/${missionId}/complete`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({}),
      })
      if (!response.ok) throw new Error(`completion failed: ${response.status}`)
      router.refresh()
    } finally {
      setPending(false)
    }
  }

  return (
    <button className="primary-button" onClick={complete} disabled={completed || pending}>
      {completed ? 'Mission recorded' : pending ? 'Recording…' : 'Mark complete'}
    </button>
  )
}

