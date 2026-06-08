-- migrations/005_create_waitlist.sql
CREATE TABLE IF NOT EXISTS waitlist (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(50)  NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    wilaya     VARCHAR(50),
    lang       VARCHAR(5)   DEFAULT 'fr',
    source     TEXT,
    created_at TIMESTAMPTZ  DEFAULT NOW(),
    updated_at TIMESTAMPTZ  DEFAULT NOW()
);
