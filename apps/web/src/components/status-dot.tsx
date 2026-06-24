export function StatusDot({ status }: { status: 'healthy' | 'degraded' | 'critical' }) {
  return <span className={`status-dot status-${status}`} aria-label={status} />
}

