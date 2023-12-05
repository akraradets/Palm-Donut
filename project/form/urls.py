from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload-ndvi", views.upload_ndvi, name="upload-ndvi"),
    path("upload-shape", views.upload_shape, name="upload-shape"),
    path("calculate-donut", views.calculate_donut, name="upload-shape"),
    path("download-output", views.download_output, name="download-outout"),
]