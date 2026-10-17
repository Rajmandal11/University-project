from django.urls import path
from . import views


urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about, name="about"),
    path("index/", views.index, name="index"),
    path("live/", views.live, name="live_detection"),
     # STORE
    path(
        "store/",
        views.store_media_view,
        name="store_media"
    ),
    path("store-result/", views.store_result, name="store_result"),
    path("delete-result/", views.delete_result, name="delete_result"),

    # STORED MEDIA
    path(
        "stored/",
        views.stored_media,
        name="stored_media"
    ),
]