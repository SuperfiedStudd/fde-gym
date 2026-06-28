'use client'

import { useState } from 'react'

export function EvaluatorCommand({
  missionId,
  compact = false,
}: {
  missionId: string
  compact?: boolean
}) {
  const [copied, setCopied] = useState(false)
  const command = `python scripts/evaluate/run.py --mission ${missionId}`

  async function copyCommand() {
    await navigator.clipboard.writeText(command)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1600)
  }

  return (
    <div className={`command-block${compact ? ' command-block-compact' : ''}`}>
      <code>{command}</code>
      <button type="button" onClick={copyCommand} aria-label={`Copy evaluator command for ${missionId}`}>
        {copied ? 'Copied' : 'Copy'}
      </button>
    </div>
  )
}
