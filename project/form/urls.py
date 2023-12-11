from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload-ndvi", views.upload_ndvi, name="upload-ndvi"),
    path("remove-ndvi", views.remove_ndvi, name="remove-ndvi"),
    path("upload-shape", views.upload_shape, name="upload-shape"),
    path("remove-shape", views.remove_shape, name="remove-shape"),
    path("calculate-donut", views.calculate_donut, name="upload-shape"),
    path("download-output", views.download_output, name="download-output"),
    path("remove-output", views.remove_output, name="remove-output"),
    path("clear-session", views.clear_session, name="clear-session"),
]