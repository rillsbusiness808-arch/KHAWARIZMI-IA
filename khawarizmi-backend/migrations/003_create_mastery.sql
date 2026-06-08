-- ══════════════════════════════════════════
-- 003_create_mastery.sql
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS mastery_micro_concepts (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    micro_concept_id    VARCHAR(50) NOT NULL REFERENCES micro_concepts(id),
    prochaine_revision  TIMESTAMPTZ DEFAULT NOW(),
    interval_jours      INTEGER DEFAULT 1,
    difficulty          FLOAT DEFAULT 0.0,
    stability           FLOAT DEFAULT 0.0,
    fsrs_state          JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (user_id, micro_concept_id)
);
