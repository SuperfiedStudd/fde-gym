INSERT INTO roles (name, description) VALUES
    ('admin', 'Platform administrator'),
    ('supervisor', 'Claims operations supervisor'),
    ('adjuster', 'Claims adjuster'),
    ('auditor', 'Read-only compliance reviewer');

INSERT INTO users (id, email, display_name, role_id) VALUES
    ('10000000-0000-0000-0000-000000000001', 'ada.admin@claimops.test', 'Ada Admin', (SELECT id FROM roles WHERE name = 'admin')),
    ('10000000-0000-0000-0000-000000000002', 'sam.supervisor@claimops.test', 'Sam Supervisor', (SELECT id FROM roles WHERE name = 'supervisor')),
    ('10000000-0000-0000-0000-000000000003', 'alex.adjuster@claimops.test', 'Alex Adjuster', (SELECT id FROM roles WHERE name = 'adjuster')),
    ('10000000-0000-0000-0000-000000000004', 'riley.adjuster@claimops.test', 'Riley Adjuster', (SELECT id FROM roles WHERE name = 'adjuster')),
    ('10000000-0000-0000-0000-000000000005', 'audrey.auditor@claimops.test', 'Audrey Auditor', (SELECT id FROM roles WHERE name = 'auditor'));

INSERT INTO claims (
    id, external_id, claimant_name, amount_cents, status, priority, category, created_by, created_at
) VALUES
    ('20000000-0000-0000-0000-000000000001', 'CLM-2026-0001', 'Morgan Avery', 125000, 'submitted', 'high', 'property', '10000000-0000-0000-0000-000000000002', now() - interval '14 days'),
    ('20000000-0000-0000-0000-000000000002', 'CLM-2026-0002', 'Jordan Bell', 87500, 'reviewing', 'normal', 'auto', '10000000-0000-0000-0000-000000000003', now() - interval '12 days'),
    ('20000000-0000-0000-0000-000000000003', 'CLM-2026-0003', 'Casey Chen', 420000, 'approved', 'urgent', 'property', '10000000-0000-0000-0000-000000000002', now() - interval '10 days'),
    ('20000000-0000-0000-0000-000000000004', 'CLM-2026-0004', 'Taylor Diaz', 9900, 'denied', 'low', 'travel', '10000000-0000-0000-0000-000000000004', now() - interval '8 days'),
    ('20000000-0000-0000-0000-000000000005', 'CLM-2026-0005', 'Emerson Flynn', 210000, 'draft', 'normal', 'auto', '10000000-0000-0000-0000-000000000003', now() - interval '7 days'),
    ('20000000-0000-0000-0000-000000000006', 'CLM-2026-0006', 'Quinn Gupta', 53200, 'closed', 'normal', 'travel', '10000000-0000-0000-0000-000000000004', now() - interval '6 days');

INSERT INTO claims (external_id, claimant_name, amount_cents, status, priority, category, created_by, created_at)
SELECT
    'CLM-2026-' || lpad((100 + value)::text, 4, '0'),
    'Synthetic Claimant ' || value,
    10000 + value * 137,
    (ARRAY['draft', 'submitted', 'reviewing', 'approved', 'denied', 'closed'])[(value % 6) + 1],
    (ARRAY['low', 'normal', 'high'])[(value % 3) + 1],
    (ARRAY['auto', 'property', 'travel'])[(value % 3) + 1],
    '10000000-0000-0000-0000-000000000003',
    now() - make_interval(hours => value)
FROM generate_series(1, 54) AS value;

INSERT INTO claim_events (claim_id, event_type, payload, idempotency_key)
SELECT id, 'claim.seeded', jsonb_build_object('source', 'seed'), 'seed-' || id::text
FROM claims;

INSERT INTO claim_notes (claim_id, author_id, body, internal) VALUES
    ('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000003', 'Awaiting photo evidence review.', true),
    ('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', 'Approval confirmed by supervisor.', true),
    ('20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000004', 'Policy exclusion applies.', false);

INSERT INTO assignments (claim_id, user_id, active) VALUES
    ('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000003', true),
    ('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000004', true);

INSERT INTO jobs (id, claim_id, kind, status, payload, attempts, max_attempts) VALUES
    ('30000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 'claim.process', 'pending', '{"claim_id":"20000000-0000-0000-0000-000000000001"}', 0, 3),
    ('30000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000003', 'document.generate', 'pending', '{"claim_id":"20000000-0000-0000-0000-000000000003","simulate_failure":true}', 0, 3),
    ('30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000002', 'document.generate', 'failed', '{"claim_id":"20000000-0000-0000-0000-000000000002"}', 3, 3);

INSERT INTO audit_logs (actor_id, action, resource_type, resource_id, metadata) VALUES
    ('10000000-0000-0000-0000-000000000002', 'claim.approved', 'claim', '20000000-0000-0000-0000-000000000003', '{"source":"seed"}'),
    ('10000000-0000-0000-0000-000000000004', 'claim.denied', 'claim', '20000000-0000-0000-0000-000000000004', '{"source":"seed"}');

