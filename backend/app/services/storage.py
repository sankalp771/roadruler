import uuid
try:
    from supabase import create_client, Client
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_KEY

    if url and key:
        supabase: Client = create_client(url, key)
    else:
        supabase = None
except ImportError:
    supabase = None

def upload_file_to_supabase(file_bytes: bytes, original_filename: str) -> str:
    ext = original_filename.split('.')[-1] if '.' in original_filename else 'jpg'
    if not supabase:
        return f"https://storage.roadruler.gov.in/complaints/{uuid.uuid4()}.{ext}"
    
    # Generate a unique filename
    ext = original_filename.split('.')[-1] if '.' in original_filename else 'jpg'
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Upload to 'complaints' bucket
    # The 'complaints' bucket must be public in Supabase
    bucket_name = "complaints"
    
    # Upload file
    res = supabase.storage.from_(bucket_name).upload(
        path=filename,
        file=file_bytes,
        file_options={"content-type": f"image/{ext}"}
    )
    
    # Get public URL
    public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
    return public_url
