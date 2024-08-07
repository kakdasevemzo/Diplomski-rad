from django.urls import path
from .views import BlogPostListCreate, upload_telemetry


urlpatterns = [
    path("blogposts/", BlogPostListCreate.as_view(), name="blogpost-view-create"),
    path('sondes/telemetry/', upload_telemetry, name='upload_telemetry'),
]