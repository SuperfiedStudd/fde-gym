import Link from 'next/link'

import { getCurrentAssessment } from '@/lib/assessment'

export const dynamic = 'force-dynamic'
export const metadata = { title: 'Assessment Mode' }

export default async function AssessmentPage() {
  const assessment = await getCurrentAssessment()

  return (
    <div className="page-shell assessment-landing">
      <section className="page-heading">
        <div>
          <p className="eyebrow">BUILD WITH AI / LIVE PRACTICE</p>
          <h1>Assessment Mode</h1>
        </div>
        <p>
          Work through an unfamiliar business problem with ChatGPT as interviewer and your coding
          agent as an implementation partner.
        </p>
      </section>

      <section className="assessment-landing-grid">
        <div className="panel assessment-status-panel">
          <p className="eyebrow">CURRENT ASSESSMENT</p>
          <div className="assessment-load-state">
            <span className={assessment ? 'status-dot status-healthy' : 'status-dot status-offline'} />
            <strong>{assessment ? 'Loaded' : 'Not loaded'}</strong>
          </div>
          {assessment ? (
            <>
              <h2>{assessment.title}</h2>
              <p>{assessment.duration_minutes} minutes · {assessment.difficulty}</p>
              <Link className="primary-button" href="/assessment/current">Open assessment</Link>
            </>
          ) : (
            <>
              <p className="empty-state">
                Load a candidate bundle from the repository root, then refresh this page.
              </p>
              <code className="assessment-load-command">
                python scripts/assessment/load.py &lt;assessment-directory&gt;
              </code>
            </>
          )}
        </div>

        <div className="panel assessment-instructions">
          <p className="eyebrow">WORKFLOW</p>
          <ol>
            <li><strong>Understand</strong><span>Clarify the outcome and constraints.</span></li>
            <li><strong>Diagnose</strong><span>Inspect the data and establish evidence.</span></li>
            <li><strong>Plan</strong><span>Choose a scoped approach and checks.</span></li>
            <li><strong>Implement</strong><span>Give your coding agent bounded work.</span></li>
            <li><strong>Verify / Debug</strong><span>Test the result and investigate failures.</span></li>
            <li><strong>Explain</strong><span>Present decisions, evidence, and tradeoffs.</span></li>
          </ol>
        </div>
      </section>
    </div>
  )
}
