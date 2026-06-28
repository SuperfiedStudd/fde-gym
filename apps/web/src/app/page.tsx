import Link from 'next/link'

import { StatusDot } from '@/components/status-dot'
import { getMissions, getProgress, getSystemHealth, safely } from '@/lib/api'

export default async function DashboardPage() {
  const [missions, progress, health] = await Promise.all([
    safely(getMissions, []),
    safely(getProgress, { completed: {}, version: 1 }),
    safely(getSystemHealth, null),
  ])
  const completed = Object.keys(progress.completed).length
  const completion = missions.length ? Math.round((completed / missions.length) * 100) : 0

  return (
    <div className="page-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">ENGINEERING PRACTICE ENVIRONMENT / 00</p>
          <h1>ClaimOps<br />control plane.</h1>
          <p className="lede">
            Diagnose broken services. Prove the repair. Record the operational judgment behind it.
          </p>
        </div>
        <div className="hero-actions">
          <Link className="primary-button" href="/missions">Open mission queue</Link>
          <code>python scripts/evaluate/list.py</code>
        </div>
      </section>

      <section className="metric-strip" aria-label="System metrics">
        <Metric label="System" value={health?.overall ?? 'offline'} status={health?.overall} />
        <Metric label="Queue depth" value={String(health?.queue_depth ?? '--')} />
        <Metric label="p95 latency" value={health ? `${health.p95_latency_ms} ms` : '--'} />
        <Metric label="Error rate" value={health ? `${(health.error_rate * 100).toFixed(1)}%` : '--'} />
        <Metric label="Progress" value={`${completion}%`} />
      </section>

      <section className="dashboard-grid">
        <div className="panel wide-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">MISSION QUEUE</p>
              <h2>Recommended next operation</h2>
            </div>
            <Link href="/missions">View all {missions.length} -&gt;</Link>
          </div>
          {missions[completed] ? (
            <Link className="next-mission" href={`/missions/${missions[completed].id}`}>
              <span className="level-code">{missions[completed].level}</span>
              <div>
                <h3>{missions[completed].title}</h3>
                <p>{missions[completed].summary}</p>
              </div>
              <span className="operation-id">{missions[completed].id}</span>
            </Link>
          ) : (
            <p className="empty-state">Mission API unavailable. Start the local stack to populate the queue.</p>
          )}
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">SERVICE MAP</p>
              <h2>Runtime status</h2>
            </div>
          </div>
          <div className="service-list">
            {health ? (
              Object.entries(health.components).map(([name, component]) => (
                <div key={name}>
                  <span><StatusDot status={component.status} />{name}</span>
                  <code>{component.latency_ms.toFixed(1)}ms</code>
                </div>
              ))
            ) : (
              <p className="empty-state">No telemetry. API may be offline.</p>
            )}
          </div>
        </div>

        <div className="panel terminal-panel">
          <div className="terminal-title"><span /> local operator commands</div>
          <pre><code>{`$ docker compose up --build -d
$ curl http://localhost:8000/health
$ python scripts/seed/enqueue.py
$ python scripts/evaluate/run.py \
    --mission lv1-request-validation
$ docker compose logs -f api worker`}</code></pre>
        </div>
      </section>
    </div>
  )
}

function Metric({ label, value, status }: { label: string; value: string; status?: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong className={status ? `text-${status}` : undefined}>{value}</strong>
    </div>
  )
}
