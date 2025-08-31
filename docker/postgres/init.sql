-- Initialize English Learning Platform Database
-- This script runs when PostgreSQL container starts for the first time

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS english_learning;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search
CREATE EXTENSION IF NOT EXISTS "unaccent"; -- For accent-insensitive search

-- Create schemas for better organization
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set default search path
ALTER DATABASE english_learning SET search_path TO public, content, users, analytics;

-- Create initial indexes for performance
-- These will be expanded when we create the actual tables

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE english_learning TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;