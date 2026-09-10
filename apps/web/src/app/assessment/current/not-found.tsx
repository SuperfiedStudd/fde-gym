import Link from 'next/link'

export default function CurrentAssessmentNotFound() {
  return (
    <div className="page-shell not-found">
      <p className="eyebrow">ASSESSMENT SLOT EMPTY</p>
      <h1>No current assessment.</h1>
      <p className="empty-state">
        Load a candidate-safe assessment bundle from the repository root, then try again.
      </p>
      <Link className="primary-button" href="/assessment">Return to Assessment Mode</Link>
    </div>
  )
}
