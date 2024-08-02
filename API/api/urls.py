from django.urls import path
from .views import BlogPostListCreate

urlpatterns = [
    path("blogposts/", BlogPostListCreate.as_view(), name="blogpost-view-create")
]