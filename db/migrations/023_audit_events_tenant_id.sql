-- 023_audit_events_tenant_id.sql: Add tenant_id column to audit_events for multi-tenant isolation

-- Add tenant_id column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'scraper' 
        AND table_name = 'audit_events' 
        AND column_name = 'tenant_id'
    ) THEN
        ALTER TABLE scraper.audit_events 
        ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'default';
        
        CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_created
            ON scraper.audit_events (tenant_id, created_at DESC);
        
        CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_source
            ON scraper.audit_events (tenant_id, source) WHERE source IS NOT NULL;
    END IF;
END $$;

