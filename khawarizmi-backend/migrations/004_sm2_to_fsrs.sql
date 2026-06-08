-- ═══════════════════════════════════════════════════════════════
-- Migration : SM-2 → FSRS
-- Table     : mastery_micro_concepts
-- Auteur    : Khawarizmi Backend
-- ═══════════════════════════════════════════════════════════════

-- ── UP ──────────────────────────────────────────────────────────

BEGIN;

-- 1. Ajouter les colonnes FSRS
ALTER TABLE mastery_micro_concepts
    ADD COLUMN IF NOT EXISTS difficulty     FLOAT   DEFAULT 0.0,
    ADD COLUMN IF NOT EXISTS stability      FLOAT   DEFAULT 0.0,
    ADD COLUMN IF NOT EXISTS fsrs_state     JSONB   DEFAULT '{}';

-- 2. Supprimer les colonnes SM-2 obsolètes
--    (après vérification que FSRS est opérationnel)
ALTER TABLE mastery_micro_concepts
    DROP COLUMN IF EXISTS easiness_factor,
    DROP COLUMN IF EXISTS repetitions;

-- 3. Supprimer retrievability — calculée à la volée
--    (valeur stockée = toujours périmée)
ALTER TABLE mastery_micro_concepts
    DROP COLUMN IF EXISTS retrievability;

-- 4. Index critiques pour les performances
--    Requête drill : user_id + prochaine_revision
CREATE INDEX IF NOT EXISTS idx_mastery_user_revision
    ON mastery_micro_concepts (user_id, prochaine_revision ASC);

--    Requête interleaving : user_id + chapitre
CREATE INDEX IF NOT EXISTS idx_mastery_user_chapitre
    ON mastery_micro_concepts (user_id, micro_concept_id);

--    Requête FSRS state lookup
CREATE INDEX IF NOT EXISTS idx_mastery_fsrs_state
    ON mastery_micro_concepts USING GIN (fsrs_state);

-- 5. Commentaires de documentation
COMMENT ON COLUMN mastery_micro_concepts.stability IS
    'Stabilité FSRS : durée de vie estimée du souvenir (en jours)';

COMMENT ON COLUMN mastery_micro_concepts.difficulty IS
    'Difficulté FSRS : 0.0 (facile) → 1.0 (très difficile)';

COMMENT ON COLUMN mastery_micro_concepts.fsrs_state IS
    'État complet de la carte FSRS sérialisé en JSON.
     Contient : due, stability, difficulty, reps, lapses, state, last_review.
     NE PAS modifier manuellement — géré par services/scheduler.py.';

COMMENT ON COLUMN mastery_micro_concepts.interval_jours IS
    'Cache d affichage uniquement (ex: "Revoir dans 4 jours").
     La vraie logique de planification est dans fsrs_state.';

COMMIT;


-- ── DOWN (rollback complet) ─────────────────────────────────────

-- BEGIN;
--
-- ALTER TABLE mastery_micro_concepts
--     ADD COLUMN IF NOT EXISTS easiness_factor FLOAT   DEFAULT 2.5,
--     ADD COLUMN IF NOT EXISTS repetitions     INTEGER DEFAULT 0,
--     ADD COLUMN IF NOT EXISTS retrievability  FLOAT   DEFAULT 0.0;
--
-- ALTER TABLE mastery_micro_concepts
--     DROP COLUMN IF EXISTS difficulty,
--     DROP COLUMN IF EXISTS stability,
--     DROP COLUMN IF EXISTS fsrs_state;
--
-- DROP INDEX IF EXISTS idx_mastery_user_revision;
-- DROP INDEX IF EXISTS idx_mastery_user_chapitre;
-- DROP INDEX IF EXISTS idx_mastery_fsrs_state;
--
-- COMMIT;
