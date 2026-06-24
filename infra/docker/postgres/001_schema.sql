CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE roles (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name varchar(40) NOT NULL UNIQUE,
    description text NOT NULL DEFAULT ''
);

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email varchar(255) NOT NULL UNIQUE,
    display_name varchar(120) NOT NULL,
    role_id integer NOT NULL REFERENCES roles(id),
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE claims (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id varchar(80) NOT NULL UNIQUE,
    claimant_name varchar(160) NOT NULL,
    amount_cents integer NOT NULL,
    status varchar(40) NOT NULL DEFAULT 'draft',
    priority varchar(20) NOT NULL DEFAULT 'normal',
    category varchar(60) NOT NULL,
    version integer NOT NULL DEFAULT 1,
    created_by uuid NOT NULL REFERENCES users(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT claims_amount_nonnegative CHECK (amount_cents >= 0),
    CONSTRAINT claims_status_valid CHECK (
        status IN ('draft', 'submitted', 'reviewing', 'approved', 'denied', 'closed')
    ),
    CONSTRAINT claims_priority_valid CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

CREATE TABLE claim_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id uuid NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    event_type varchar(80) NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    idempotency_key varchar(120) UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE claim_notes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id uuid NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    author_id uuid NOT NULL REFERENCES users(id),
    body text NOT NULL,
    internal boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE assignments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id uuid NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES users(id),
    active boolean NOT NULL DEFAULT true,
    assigned_at timestamptz NOT NULL DEFAULT now(),
    released_at timestamptz
);

CREATE TABLE jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id uuid REFERENCES claims(id) ON DELETE SET NULL,
    kind varchar(80) NOT NULL,
    status varchar(40) NOT NULL DEFAULT 'pending',
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    attempts integer NOT NULL DEFAULT 0,
    max_attempts integer NOT NULL DEFAULT 3,
    last_error text,
    available_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id uuid REFERENCES users(id) ON DELETE SET NULL,
    action varchar(100) NOT NULL,
    resource_type varchar(60) NOT NULL,
    resource_id varchar(100) NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_claims_created_at ON claims (created_at DESC);
CREATE INDEX idx_claims_status_created_at ON claims (status, created_at DESC);
CREATE INDEX idx_claim_events_claim_created ON claim_events (claim_id, created_at DESC);
CREATE INDEX idx_jobs_ready ON jobs (status, available_at) WHERE status IN ('pending', 'retry');
CREATE INDEX idx_assignments_claim ON assignments (claim_id, assigned_at DESC);

COMMENT ON TABLE claims IS 'Fictional ClaimOps workflow records; contains no real personal data.';
COMMENT ON COLUMN claims.version IS 'Optimistic concurrency token; one mission intentionally ignores it.';

