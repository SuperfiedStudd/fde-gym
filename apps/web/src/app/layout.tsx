import type { Metadata } from 'next'

import { Nav } from '@/components/nav'

import './globals.css'

export const metadata: Metadata = {
  title: { default: 'fde-gym // ClaimOps', template: '%s // fde-gym' },
  description: 'A personal forward-deployed engineering practice environment.',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-theme="terminal">
      <body>
        <Nav />
        <main>{children}</main>
        <footer>
          <span>FDE-GYM / CLAIMOPS</span>
          <span>fictional data · local environment</span>
        </footer>
      </body>
    </html>
  )
}

