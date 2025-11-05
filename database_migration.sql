-- Add status tracking columns to transcripts table
-- Run this in your Supabase SQL editor

ALTER TABLE transcripts 
ADD COLUMN IF NOT EXISTS job_id TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending';

-- Create index for faster job_id lookups
CREATE INDEX IF NOT EXISTS idx_transcripts_job_id ON transcripts(job_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_status ON transcripts(status);

-- Update existing records to have 'completed' status
UPDATE transcripts 
SET status = 'completed' 
WHERE status IS NULL AND ai_feedback IS NOT NULL;
