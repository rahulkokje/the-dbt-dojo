CREATE TABLE raw.account_audit (
    audit_id UUID PRIMARY KEY,
    account_id UUID NOT NULL,
    status TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('CURRENT', 'SAVINGS', 'SUB-ACCOUNT')),
    legal_entity TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    audit_operation CHAR(1) NOT NULL CHECK (audit_operation IN ('I', 'U')),
    opened_at TIMESTAMP,
    closed_at TIMESTAMP
);

-- To efficiently fetch latest records per account
CREATE INDEX idx_account_audit_account_updated
    ON raw.account_audit (account_id, updated_at DESC);

-- For filtering or grouping by account type
CREATE INDEX idx_account_audit_type
    ON raw.account_audit (type);

-- For filtering by status (e.g., OPEN, CLOSED, etc.)
CREATE INDEX idx_account_audit_status
    ON raw.account_audit (status);


CREATE TABLE raw.customer_accounts (
    customer_id UUID NOT NULL,
    account_id UUID NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('OWNER', 'MEMBER')),
    action TEXT NOT NULL CHECK (action IN ('ADDED', 'REMOVED')),
    created_at TIMESTAMP NOT NULL,

    PRIMARY KEY (customer_id, account_id, role, created_at)
);

-- Fast lookup of all customers linked to an account (useful for joins)
CREATE INDEX idx_customer_accounts_account_id
    ON raw.customer_accounts (account_id);

-- Fast lookup of all accounts linked to a customer
CREATE INDEX idx_customer_accounts_customer_id
    ON raw.customer_accounts (customer_id);