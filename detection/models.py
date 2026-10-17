from django.db import models


class StoredMedia(models.Model):

    MEDIA_TYPES = (
        ("image", "Image"),
        ("video", "Video"),
    )

    name = models.CharField(max_length=255)

    file = models.FileField(
        upload_to="stored/"
    )

    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPES
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name