# detection/store.py

import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage


# ============================================================
# STORAGE DIRECTORIES
# ============================================================

IMAGE_FOLDER = "stored/images/"
VIDEO_FOLDER = "stored/videos/"


# ============================================================
# STORE IMAGE
# ============================================================

def store_image(uploaded_file):
    """
    Store an uploaded image permanently.

    Returns:
        Relative path of the stored image.
    """

    extension = os.path.splitext(uploaded_file.name)[1].lower()

    filename = f"{uuid.uuid4().hex}{extension}"

    path = os.path.join(
        IMAGE_FOLDER,
        filename
    )

    saved_path = default_storage.save(
        path,
        uploaded_file
    )

    return saved_path


# ============================================================
# STORE VIDEO
# ============================================================

def store_video(uploaded_file):
    """
    Store an uploaded video permanently.

    Returns:
        Relative path of the stored video.
    """

    extension = os.path.splitext(uploaded_file.name)[1].lower()

    filename = f"{uuid.uuid4().hex}{extension}"

    path = os.path.join(
        VIDEO_FOLDER,
        filename
    )

    saved_path = default_storage.save(
        path,
        uploaded_file
    )

    return saved_path


# ============================================================
# STORE ANY MEDIA
# ============================================================

def store_media(uploaded_file):
    """
    Automatically determine whether the file
    is an image or video and store it.
    """

    content_type = uploaded_file.content_type

    if content_type.startswith("image/"):
        return store_image(uploaded_file)

    elif content_type.startswith("video/"):
        return store_video(uploaded_file)

    raise ValueError("Unsupported file type")