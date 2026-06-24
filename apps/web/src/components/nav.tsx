import Link from 'next/link'

const links = [
  { href: '/', label: 'Overview' },
  { href: '/missions', label: 'Missions' },
  { href: '/progress', label: 'Progress' },
]

export function Nav() {
  return (
    <header className="topbar">
      <Link href="/" className="brand" aria-label="fde-gym home">
        <span className="brand-mark">FDE</span>
        <span>GYM</span>
        <span className="environment">LOCAL</span>
      </Link>
      <nav aria-label="Primary navigation">
        {links.map((link) => (
          <Link href={link.href} key={link.href}>
            {link.label}
          </Link>
        ))}
      </nav>
      <div className="system-mode">
        <span className="pulse" /> ClaimOps sandbox
      </div>
    </header>
  )
}

