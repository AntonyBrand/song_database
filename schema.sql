-- 1. Create Enum for tracking processing stages
CREATE TYPE song_stage AS ENUM ('raw', 'partially_structured', 'fully_structured');

-- 2. Create Songs Table
CREATE TABLE songs (
    song_id SERIAL PRIMARY KEY,
    
    -- Metadata
    title VARCHAR(255) NOT NULL,
    poet VARCHAR(255),
    primary_language VARCHAR(50) DEFAULT 'Bengali',
    languages TEXT[] DEFAULT ARRAY['Bengali'],
    dialect_or_style VARCHAR(100),
    is_language_uncertain BOOLEAN DEFAULT FALSE,
    language_notes TEXT,
    
    rag VARCHAR(100),
    tal VARCHAR(100),
    
    -- Processing Stage & Notes
    stage song_stage DEFAULT 'raw',
    overall_notes TEXT,
    
    -- Stage 1: Raw
    raw_text TEXT,
    raw_notes TEXT,
    
    -- Stages 2 & 3: Structured JSON (Tripodi, Shloka, Swaralipi/Sarega)
    structured_content JSONB,
    structured_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create Source Images / Scans Table
CREATE TABLE song_sources (
    source_id SERIAL PRIMARY KEY,
    song_id INT REFERENCES songs(song_id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    source_notes TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create Performance Index on JSONB Column
CREATE INDEX idx_songs_structured ON songs USING gin (structured_content);