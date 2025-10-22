-- Antarctic Backend Database Schema
-- Execute this in Vercel Postgres after connecting the database

CREATE TABLE licenses (
  id SERIAL PRIMARY KEY,
  license_key VARCHAR(255) UNIQUE NOT NULL,
  license_type VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  last_used TIMESTAMP,
  usage_count INTEGER DEFAULT 0,
  is_banned BOOLEAN DEFAULT false,
  notes TEXT
);

-- Create indexes for better performance
CREATE INDEX idx_licenses_key ON licenses(license_key);
CREATE INDEX idx_licenses_type ON licenses(license_type);
CREATE INDEX idx_licenses_banned ON licenses(is_banned);
CREATE INDEX idx_licenses_expires ON licenses(expires_at);
