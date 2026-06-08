-- ══════════════════════════════════════════
-- 002_create_micro_concepts.sql
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS micro_concepts (
    id              VARCHAR(50) PRIMARY KEY,
    chapitre_id     VARCHAR(50) NOT NULL,
    matiere         VARCHAR(50) NOT NULL,
    nom             VARCHAR(255) NOT NULL,
    description     TEXT
);

CREATE INDEX IF NOT EXISTS idx_mc_chapitre
    ON micro_concepts (chapitre_id);
