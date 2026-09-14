import os
import uuid
from pathlib import Path

# --- CONFIGURATION ---
STORAGE_MODE = os.getenv("STORAGE_MODE", "local")  # Options: 'local', 's3', 'supabase'
LOCAL_UPLOAD_DIR = Path(__file__).parent / "uploads"

# Ensure local upload directory exists
LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_image(uploaded_file, folder_prefix: str = "sources") -> str:
    """
    Saves an uploaded file (from Streamlit/Flask) and returns its accessible path/URL.
    
    :param uploaded_file: Streamlit UploadedFile object or file-like object
    :param folder_prefix: Subfolder grouping (e.g., 'sources', 'scores')
    :return: File path or public URL string to store in PostgreSQL
    """
    # 1. Generate a collision-safe filename (e.g., 8f9b2a-page1.jpg)
    file_ext = Path(uploaded_file.name).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex[:8]}_{Path(uploaded_file.name).stem}{file_ext}"

    # 2. Route based on active storage mode
    if STORAGE_MODE == "local":
        return _save_locally(uploaded_file, folder_prefix, unique_filename)
    elif STORAGE_MODE == "s3":
        return _save_to_s3(uploaded_file, folder_prefix, unique_filename)
    elif STORAGE_MODE == "supabase":
        return _save_to_supabase(uploaded_file, folder_prefix, unique_filename)
    else:
        raise ValueError(f"Unsupported STORAGE_MODE: {STORAGE_MODE}")


# --- LOCAL IMPLEMENTATION ---
def _save_locally(uploaded_file, folder_prefix: str, filename: str) -> str:
    target_dir = LOCAL_UPLOAD_DIR / folder_prefix
    target_dir.mkdir(parents=True, exist_ok=True)
    
    destination_path = target_dir / filename

    # Write file bytes to disk
    with open(destination_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Return relative path for database storage (e.g., "uploads/sources/a1b2c3_scan.jpg")
    return str(Path("uploads") / folder_prefix / filename)


# --- CLOUD IMPLEMENTATION HOOKS (For Future Migration) ---
def _save_to_s3(uploaded_file, folder_prefix: str, filename: str) -> str:
    """Placeholder for AWS S3 / DigitalOcean Spaces upload."""
    # import boto3
    # s3 = boto3.client('s3')
    # s3.upload_fileobj(uploaded_file, "my-bucket", f"{folder_prefix}/{filename}")
    # return f"https://my-bucket.s3.amazonaws.com/{folder_prefix}/{filename}"
    pass

def _save_to_supabase(uploaded_file, folder_prefix: str, filename: str) -> str:
    """Placeholder for Supabase Storage bucket upload."""
    # supabase.storage.from_("song-scans").upload(f"{folder_prefix}/{filename}", uploaded_file.getvalue())
    # return supabase.storage.from_("song-scans").get_public_url(f"{folder_prefix}/{filename}")
    pass