declare module 'pino' {
  type ClaimOpsLogger = {
    info(bindings: object, message: string): void
  }

  export default function pino(options?: object): ClaimOpsLogger
}

