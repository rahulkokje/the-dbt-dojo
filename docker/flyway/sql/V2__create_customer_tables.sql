-- Create customer audit table to track all changes
CREATE TABLE IF NOT EXISTS raw.customer_audit (
    audit_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    kyc_status TEXT NOT NULL,
    tnc_country_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    audit_operation TEXT NOT NULL CHECK (audit_operation IN ('I', 'U'))
);

CREATE INDEX IF NOT EXISTS idx_customer_audit_customer_id ON raw.customer_audit(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_audit_updated_at ON raw.customer_audit(updated_at);