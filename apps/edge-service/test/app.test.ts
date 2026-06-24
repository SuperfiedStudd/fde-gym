import { describe, expect, it } from 'vitest'

import { app } from '../src/app.js'

describe('edge service', () => {
  it('reports health', async () => {
    const response = await app.request('/health')
    expect(response.status).toBe(200)
    expect(await response.json()).toEqual({ status: 'ok', service: 'edge-service' })
  })

  it('validates event payloads', async () => {
    const response = await app.request('/events', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ type: '' }),
    })
    expect(response.status).toBe(422)
  })
})

