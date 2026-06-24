FROM node:22-alpine
WORKDIR /workspace
COPY package.json package-lock.json* ./
COPY apps/edge-service/package.json apps/edge-service/package.json
COPY packages/shared/package.json packages/shared/package.json
RUN npm install --workspace @fde-gym/edge-service --include-workspace-root
COPY apps/edge-service apps/edge-service
WORKDIR /workspace/apps/edge-service
EXPOSE 3001
CMD ["npm", "run", "start"]

