-- OpenSkill Studio — PostgreSQL initialization
-- This runs once when the postgres container is first created.

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create test database for CI
SELECT 'CREATE DATABASE openskill_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'openskill_test')\gexec
