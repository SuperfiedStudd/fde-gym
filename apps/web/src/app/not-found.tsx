import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="page-shell not-found">
      <p className="eyebrow">HTTP 404</p>
      <h1>Operation not found.</h1>
      <Link className="primary-button" href="/missions">Return to mission queue</Link>
    </div>
  )
}

