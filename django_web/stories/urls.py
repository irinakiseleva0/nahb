from django.urls import path
from .views import story_list

urlpatterns = [
    path("stories/", story_list, name="story_list"),
]
