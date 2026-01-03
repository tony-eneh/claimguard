-- PostgreSQL Audit Log Schema for ClaimGuard E5 Experiment
-- Creates indexed table optimized for compliance queries

-- Drop table if exists (for clean reruns)
DROP TABLE IF EXISTS audit_log CASCADE;

-- Create audit_log table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(42) NOT NULL,           -- Ethereum address (0x + 40 hex chars)
    resource_id_hash VARCHAR(66) NOT NULL,  -- keccak256 hash (0x + 64 hex chars)
    action VARCHAR(20) NOT NULL,            -- READ, APPEND, UPDATE, DELETE, etc.
    allowed BOOLEAN NOT NULL,               -- true = allowed, false = denied
    timestamp TIMESTAMP DEFAULT NOW(),
    block_number INTEGER,                   -- Optional: for blockchain correlation
    transaction_hash VARCHAR(66)            -- Optional: for blockchain correlation
);

-- Create indexes for common query patterns
CREATE INDEX idx_subject ON audit_log(subject);
CREATE INDEX idx_resource ON audit_log(resource_id_hash);
CREATE INDEX idx_timestamp ON audit_log(timestamp);
CREATE INDEX idx_allowed ON audit_log(allowed);

-- Partial index for denials (compliance audits focus on these)
CREATE INDEX idx_denied ON audit_log(allowed) WHERE allowed = false;

-- Composite indexes for compound queries
CREATE INDEX idx_subject_timestamp ON audit_log(subject, timestamp);
CREATE INDEX idx_resource_timestamp ON audit_log(resource_id_hash, timestamp);

-- Analyze table for query optimization
ANALYZE audit_log;

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE audit_log TO claimguard;
GRANT USAGE, SELECT ON SEQUENCE audit_log_id_seq TO claimguard;

-- Display table info
\d audit_log

-- Success message
\echo 'PostgreSQL audit_log schema created successfully!'
