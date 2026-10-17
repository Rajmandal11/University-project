import uuid
import shutil
from pathlib import Path

from django.conf import settings
from django.http import StreamingHttpResponse
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages

from .models import StoredMedia
from .store import store_media

from .yolo import (
    detect_image,
    detect_video,
    generate_camera
)


def landing(request):

    return render(
        request,
        "detection/landing.html"
    )


def about(request):

    return render(
        request,
        "detection/about.html"
    )


def index(request):

    context = {}

    # ==========================================
    # IMAGE
    # ==========================================

    if request.method == "POST":

        detection_type = request.POST.get(
            "detection_type"
        )

        # --------------------------------------
        # IMAGE DETECTION
        # --------------------------------------

        if detection_type == "image":

            image = request.FILES.get(
                "image"
            )

            if image:

                upload_dir = (
                    Path(settings.MEDIA_ROOT)
                    / "uploads"
                )

                result_dir = (
                    Path(settings.MEDIA_ROOT)
                    / "results"
                )

                upload_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                result_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                filename = (
                    f"{uuid.uuid4().hex}_"
                    f"{image.name}"
                )

                image_path = (
                    upload_dir / filename
                )

                with open(
                    image_path,
                    "wb+"
                ) as destination:

                    for chunk in image.chunks():

                        destination.write(
                            chunk
                        )

                # YOLO
                result, detections = detect_image(
                    str(image_path)
                )

                # Create annotated image
                annotated = result.plot()

                result_filename = (
                    f"result_"
                    f"{uuid.uuid4().hex}.jpg"
                )

                result_path = (
                    result_dir
                    / result_filename
                )

                import cv2

                cv2.imwrite(
                    str(result_path),
                    annotated
                )

                result_url = (
                    settings.MEDIA_URL
                    + "results/"
                    + result_filename
                )

                context = {
                    "result_url": result_url,
                    "detections": detections,
                    "image_name": image.name,
                    "active_tab": "photo",
                }


        # --------------------------------------
        # VIDEO DETECTION
        # --------------------------------------

        elif detection_type == "video":

            video = request.FILES.get(
                "video"
            )

            if video:

                upload_dir = (
                    Path(settings.MEDIA_ROOT)
                    / "uploads"
                )

                result_dir = (
                    Path(settings.MEDIA_ROOT)
                    / "results"
                )

                upload_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                result_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                filename = (
                    f"{uuid.uuid4().hex}_"
                    f"{video.name}"
                )

                video_path = (
                    upload_dir / filename
                )

                with open(
                    video_path,
                    "wb+"
                ) as destination:

                    for chunk in video.chunks():

                        destination.write(
                            chunk
                        )

                result_filename = (
                    f"detected_"
                    f"{uuid.uuid4().hex}.mp4"
                )

                output_path = (
                    result_dir
                    / result_filename
                )

                detections = detect_video(
                    str(video_path),
                    str(output_path)
                )

                result_url = (
                    settings.MEDIA_URL
                    + "results/"
                    + result_filename
                )

                context = {
                    "video_result_url":
                        result_url,

                    "video_name":
                        video.name,

                    "total_frames":
                        len(detections),

                    "active_tab":
                        "video",
                }

    return render(
        request,
        "detection/index.html",
        context
    )


# ==========================================
# LIVE CAMERA
# ==========================================

def live(request):

    return StreamingHttpResponse(
        generate_camera(),
        content_type=(
            "multipart/x-mixed-replace;"
            "boundary=frame"
        )
    )


def store_result(request):

    if request.method != "POST":
        return redirect("index")

    result_url = request.POST.get("result_url", "")
    result_name = Path(result_url.split("?")[0]).name
    result_path = Path(settings.MEDIA_ROOT) / "results" / result_name

    if not result_name or not result_path.is_file():
        messages.error(request, "The detection result could not be found.")
        return redirect("index")

    media_type = request.POST.get("media_type")
    if media_type not in {"image", "video"}:
        messages.error(request, "Unsupported result type.")
        return redirect("index")

    stored_dir = Path(settings.MEDIA_ROOT) / "stored" / f"{media_type}s"
    stored_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{result_path.suffix}"
    stored_path = stored_dir / stored_name
    shutil.copy2(result_path, stored_path)

    relative_path = stored_path.relative_to(settings.MEDIA_ROOT)
    StoredMedia.objects.create(
        name=result_name,
        file=str(relative_path),
        media_type=media_type
    )

    messages.success(request, "Detection result stored successfully.")
    return redirect("index")


def delete_result(request):

    if request.method == "POST":
        result_url = request.POST.get("result_url", "")
        result_name = Path(result_url.split("?")[0]).name
        result_path = Path(settings.MEDIA_ROOT) / "results" / result_name

        if result_name and result_path.is_file():
            result_path.unlink()
            messages.success(request, "Detection result deleted.")

    return redirect("index")


def stored_media(request):

    return redirect("index")

def store_media_view(request):

    if request.method != "POST":
        return redirect("index")

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        messages.error(
            request,
            "No image or video selected."
        )

        return redirect("index")

    try:

        # Store physical file
        stored_path = store_media(uploaded_file)

        # Determine media type
        if uploaded_file.content_type.startswith("image/"):
            media_type = "image"
        elif uploaded_file.content_type.startswith("video/"):
            media_type = "video"
        else:
            messages.error(
                request,
                "Only images and videos are supported."
            )

            return redirect("index")

        # Save database record
        StoredMedia.objects.create(
            name=uploaded_file.name,
            file=stored_path,
            media_type=media_type
        )

        messages.success(
            request,
            "Media stored successfully."
        )

    except Exception as e:

        messages.error(
            request,
            f"Storage error: {str(e)}"
        )

    return redirect("index")

 # STORE
    path(
        "store/",
        views.store_media_view,
        name="store_media"
    ),

    # STORED MEDIA
    path(
        "stored/",
        views.stored_media,
        name="stored_media"
    ),