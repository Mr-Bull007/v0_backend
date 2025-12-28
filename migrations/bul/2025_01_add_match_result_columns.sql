-- Add result-related columns to match table
-- These columns track match result information: result_type, walkover_reason, winner_source

ALTER TABLE `match`
ADD COLUMN `result_type` VARCHAR(20) NULL,
ADD COLUMN `walkover_reason` VARCHAR(30) NULL,
ADD COLUMN `winner_source` VARCHAR(20) NULL;

