import uuid
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlparse
from supabase import create_client, Client
from app.core.config import settings

url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY

if url and key:
    supabase: Client = create_client(url, key)
else:
    supabase = None

def upload_file_to_supabase(
    file_bytes: bytes,
    original_filename: str,
    content_type: str | None = None,
) -> str:
    if not supabase:
        raise Exception("Supabase is not configured.")
    if not file_bytes:
        raise ValueError("Cannot upload an empty file.")
    
    # Keep only the extension and use the actual MIME type for storage metadata.
    extension = Path(original_filename or "").suffix.lower()
    media_type = (content_type or mimetypes.guess_type(original_filename or "")[0] or "").lower()
    if media_type == "image/jpg":
        media_type = "image/jpeg"
    if media_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError("Only JPEG, PNG, and WebP images are supported.")
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        extension = mimetypes.guess_extension(media_type) or ".jpg"
    if extension == ".jpe":
        extension = ".jpg"
    filename = f"{uuid.uuid4()}{extension}"
    
    # Upload to 'complaints' bucket
    # The 'complaints' bucket must be public in Supabase
    bucket_name = "complaints"
    
    # Upload file
    res = supabase.storage.from_(bucket_name).upload(
        path=filename,
        file=file_bytes,
        file_options={"content-type": media_type}
    )
    
    # Get public URL
    public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
    return public_url


def delete_file_from_supabase(public_url: str) -> None:
    """Delete an uploaded complaint image by its public URL."""
    if not supabase:
        raise RuntimeError("Supabase is not configured.")

    parsed_url = urlparse(public_url)
    configured_host = urlparse(settings.SUPABASE_URL).hostname
    if parsed_url.hostname != configured_host:
        raise ValueError("Image URL does not belong to the configured Supabase project.")

    marker = "/storage/v1/object/public/complaints/"
    if marker not in parsed_url.path:
        raise ValueError("Image URL is not a public object in the complaints bucket.")

    object_name = unquote(parsed_url.path.split(marker, 1)[1])
    if not object_name:
        raise ValueError("Image URL does not contain an object name.")
    supabase.storage.from_("complaints").remove([object_name])
