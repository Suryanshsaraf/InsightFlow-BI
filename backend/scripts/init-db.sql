-- InsightFlow Database Initialization Script
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create the user_data schema for dynamically created tables from CSV uploads
CREATE SCHEMA IF NOT EXISTS user_data;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA user_data TO insightflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA user_data TO insightflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA user_data GRANT ALL ON TABLES TO insightflow;

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'InsightFlow database initialized successfully';
    RAISE NOTICE 'Schema "user_data" created for dynamic CSV tables';
END $$;
