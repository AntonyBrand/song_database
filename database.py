import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Database connection settings
DB_CONFIG = {
    "dbname": "song_db",
    "user": "postgres",
    "password": "zrIgurukRpAhikevalam", # Replace with your password
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# new version with better handling for empty strings, using NULL instead of ""
def insert_song(title, poet, primary_language, languages, dialect, is_uncertain, lang_notes, rag, tal, description, raw_text, raw_notes, sarega=None, structured_content=None):
    """Inserts a new song into PostgreSQL, converting empty text inputs to NULL."""
    
    # Helper to convert empty or whitespace-only strings to None (SQL NULL)
    def clean_str(val):
        return val.strip() if val and val.strip() else None

    # Sanitize optional string fields
    poet = clean_str(poet)
    dialect = clean_str(dialect)
    lang_notes = clean_str(lang_notes)
    rag = clean_str(rag)
    tal = clean_str(tal)
    description = clean_str(description)
    raw_text = clean_str(raw_text)
    raw_notes = clean_str(raw_notes)
    sarega = clean_str(sarega)

    query = """
        INSERT INTO songs (
            title, 
            poet, 
            primary_language, 
            languages, 
            dialect_or_style, 
            is_language_uncertain, 
            language_notes, 
            rag, 
            tal, 
            description,
            raw_text, 
            raw_notes, 
            sarega, 
            structured_content, 
            stage
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING song_id;
    """
    
    # Calculate stage based on presence of text or structured data
    stage = 'fully_structured' if structured_content else ('raw' if raw_text else 'metadata_only')
    json_payload = json.dumps(structured_content) if structured_content else None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (
        title, poet, primary_language, languages, dialect, 
        is_uncertain, lang_notes, rag, tal, description,
        raw_text, raw_notes, sarega, json_payload, stage
    ))
    song_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return song_id

# old version with stray "" empty strings
# def insert_song(title, poet, primary_language, languages, dialect, is_uncertain, lang_notes, rag, tal, description, raw_text, raw_notes, structured_content=None):
#     """Inserts a new song into PostgreSQL."""
#     query = """
#         INSERT INTO songs (
#             title, poet, primary_language, languages, dialect_or_style, 
#             is_language_uncertain, language_notes, rag, tal, description,
#             raw_text, raw_notes, structured_content, stage
#         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         RETURNING song_id;
#     """
    
#     stage = 'fully_structured' if structured_content else 'raw'
#     json_payload = json.dumps(structured_content) if structured_content else None

#     conn = get_connection()
#     cur = conn.cursor()
#     cur.execute(query, (
#         title, poet, primary_language, languages, dialect, 
#         is_uncertain, lang_notes, rag, tal, description,
#         raw_text, raw_notes, json_payload, stage
#     ))
#     song_id = cur.fetchone()[0]
#     conn.commit()
#     cur.close()
#     conn.close()
#     return song_id

def fetch_all_songs():
    """Fetches all songs for display in Streamlit."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM songs ORDER BY created_at DESC;")
    songs = cur.fetchall()
    cur.close()
    conn.close()
    return songs



''' To add a general description field and a flexible way to link recordings (CDs, Cassettes, DVDs, YouTube links, MP3s)
that can be shared across multiple songs, 
the best practice in database design is to use a separate recordings reference table 
with a many-to-many link table.

This allows you to create a recording once (e.g., "1984 All India Radio Concert Cassette") and assign it to multiple songs, 
while also allowing a single song to belong to multiple recordings. '''

def insert_song_source(song_id, file_path, file_name, source_notes=None):
    """Saves manuscript/scan metadata into the song_sources table."""
    query = """
        INSERT INTO song_sources (song_id, file_path, file_name, source_notes)
        VALUES (%s, %s, %s, %s);
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (song_id, file_path, file_name, source_notes))
    conn.commit()
    cur.close()
    conn.close()

def fetch_all_recordings():
    """Fetches all existing recordings to populate dropdowns in Streamlit."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM recordings ORDER BY created_at DESC;")
    recordings = cur.fetchall()
    cur.close()
    conn.close()
    return recordings

def create_recording(title, media_type, url_or_location="", release_year=None, notes=""):
    """Creates a new reusable recording entry."""
    query = """
        INSERT INTO recordings (title, media_type, url_or_location, release_year, notes)
        VALUES (%s, %s, %s, %s, %s) RETURNING recording_id;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (title, media_type, url_or_location, release_year if release_year else None, notes))
    rec_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return rec_id

def link_song_to_recording(song_id, recording_id, track_number=None, recording_notes=""):
    """Links a song to a specific recording."""
    query = """
        INSERT INTO song_recordings (song_id, recording_id, track_number, recording_notes)
        VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (song_id, recording_id, track_number if track_number else None, recording_notes))
    conn.commit()
    cur.close()
    conn.close()