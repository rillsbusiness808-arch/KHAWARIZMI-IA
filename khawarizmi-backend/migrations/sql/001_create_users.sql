-- ══════════════════════════════════════════
-- 001_create_users.sql
-- ══════════════════════════════════════════
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    prenom          VARCHAR(100),
    wilaya          VARCHAR(50),
    filiere         VARCHAR(50) DEFAULT 'sciences',
    plan            VARCHAR(20) DEFAULT 'free',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_active     TIMESTAMPTZ DEFAULT NOW()
);
