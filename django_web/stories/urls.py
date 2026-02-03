from django.urls import path
from . import views

urlpatterns = [
    path("", views.story_list, name="story_list"),
    path("play/<int:story_id>/", views.play_start, name="play_start"),
    path("page/<int:page_id>/", views.play_page, name="play_page"),
    path("choose/<int:page_id>/", views.choose, name="choose"),
    path("stats/", views.stats, name="stats"),
]
