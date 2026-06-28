FROM node:22-alpine AS dependencies
WORKDIR /workspace
COPY package.json package-lock.json* ./
COPY apps/web/package.json apps/web/package.json
COPY apps/edge-service/package.json apps/edge-service/package.json
COPY packages/shared/package.json packages/shared/package.json
RUN npm install --workspace @fde-gym/web --include-workspace-root

FROM dependencies AS dev
COPY apps/web apps/web
COPY packages/shared packages/shared
WORKDIR /workspace/apps/web
ENV NODE_ENV=development
CMD ["npm", "run", "dev"]

FROM dependencies AS builder
COPY apps/web apps/web
COPY packages/shared packages/shared
WORKDIR /workspace/apps/web
RUN npm run build

FROM node:22-alpine AS runner
ENV NODE_ENV=production
WORKDIR /app
COPY --from=builder /workspace/apps/web/.next/standalone ./
COPY --from=builder /workspace/apps/web/.next/static ./apps/web/.next/static
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
