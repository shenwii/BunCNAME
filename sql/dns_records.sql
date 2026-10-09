CREATE TABLE IF NOT EXISTS dns_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id INTEGER NOT NULL,
    host TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    ttl INTEGER DEFAULT 600,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    UNIQUE(domain_id, host, type)
);

CREATE INDEX IF NOT EXISTS idx_dns_domain_id ON dns_records(domain_id);
