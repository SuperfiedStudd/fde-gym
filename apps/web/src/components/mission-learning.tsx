'use client'

import { useState } from 'react'

import type { MissionLearningGuide } from '@/lib/mission-learning'

export function MissionLearning({ guide }: { guide: MissionLearningGuide }) {
  const [revealedLevel, setRevealedLevel] = useState(0)
  const [copied, setCopied] = useState(false)

  async function copyTutorPrompt() {
    await navigator.clipboard.writeText(guide.cursorPrompt)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1600)
  }

  return (
    <section className="learning-mode" aria-labelledby="learning-mode-heading">
      <div className="learning-mode-heading">
        <div>
          <p className="eyebrow">MISSION LEARNING MODE</p>
          <h2 id="learning-mode-heading">Study before touching code.</h2>
        </div>
        <p>Build a mental model, predict the failure, then earn the next hint only when you need it.</p>
      </div>

      <div className="study-grid">
        <section className="learning-panel study-panel">
          <p className="eyebrow">STUDY FIRST</p>
          <h3>Questions to answer out loud</h3>
          <ol className="study-questions">
            {guide.studyQuestions.map((question) => <li key={question}>{question}</li>)}
          </ol>
        </section>

        <section className="learning-panel">
          <p className="eyebrow">SYSTEM MAP</p>
          <h3>Stack surfaces in play</h3>
          <div className="system-map">
            {guide.systemAreas.map((area, index) => (
              <div className="system-area" key={area.name}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <div>
                  <strong>{area.name}</strong>
                  <p>{area.description}</p>
                  <code>{area.sourceCount} mapped source{area.sourceCount === 1 ? '' : 's'}</code>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="learning-panel file-panel">
        <div>
          <p className="eyebrow">OPEN THESE FILES FIRST</p>
          <h3>Follow the failure path in order.</h3>
        </div>
        <ol className="file-list">
          {guide.files.map((file) => <li key={file}><code>{file}</code></li>)}
        </ol>
      </section>

      <section className="learning-panel hint-panel">
        <div className="hint-heading">
          <div>
            <p className="eyebrow">GUIDED HINTS</p>
            <h3>Reveal only enough to get moving.</h3>
          </div>
          <span>{revealedLevel}/3 unlocked</span>
        </div>
        <div className="hint-list">
          {guide.hints.map((hint, index) => {
            const revealed = revealedLevel > index
            const available = index === 0 || revealedLevel >= index
            return (
              <div className={`hint-item${revealed ? ' hint-revealed' : ''}`} key={hint.level}>
                <button
                  type="button"
                  onClick={() => setRevealedLevel(index + 1)}
                  disabled={!available || revealed}
                  aria-expanded={revealed}
                >
                  <span>Level {hint.level}</span>
                  <strong>{hint.title}</strong>
                  <small>{revealed ? 'Revealed' : available ? 'Reveal hint' : 'Unlock prior level'}</small>
                </button>
                {revealed && <p>{hint.body}</p>}
              </div>
            )
          })}
        </div>
      </section>

      <section className="learning-panel tutor-panel">
        <div className="tutor-heading">
          <div>
            <p className="eyebrow">CURSOR TUTOR PROMPT</p>
            <h3>Bring a teacher into the editor—not an answer machine.</h3>
          </div>
          <button type="button" onClick={copyTutorPrompt}>{copied ? 'Copied' : 'Copy prompt'}</button>
        </div>
        <pre><code>{guide.cursorPrompt}</code></pre>
      </section>
    </section>
  )
}
