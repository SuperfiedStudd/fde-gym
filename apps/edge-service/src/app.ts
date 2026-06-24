import { Hono } from 'hono'
import { requestId } from 'hono/request-id'
import pino from 'pino'
import { z } from 'zod'

const logger = pino({ level: process.env.LOG_LEVEL ?? 'info' })

export const app = new Hono()
app.use('*', requestId())

app.get('/health', (context) => context.json({ status: 'ok', service: 'edge-service' }))

app.get('/profile', (context) => {
  const userId = context.req.header('x-user-id')
  if (!userId) return context.json({ detail: 'x-user-id required' }, 401)
  return context.json({ id: userId, preferences: { density: 'compact', theme: 'terminal' } })
})

const eventSchema = z.object({
  type: z.string().min(1),
  claimId: z.string().uuid(),
  payload: z.record(z.unknown()).default({}),
})

app.post('/events', async (context) => {
  const parsed = eventSchema.safeParse(await context.req.json())
  if (!parsed.success) return context.json({ detail: parsed.error.flatten() }, 422)
  logger.info({ requestId: context.get('requestId'), ...parsed.data }, 'edge_event_received')
  return context.json({ accepted: true, event: parsed.data }, 202)
})

