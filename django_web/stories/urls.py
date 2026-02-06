from django.urls import path
from . import views

urlpatterns = [
    path("", views.story_list, name="story_list"),
    path("play/<int:story_id>/", views.play_start, name="play_start"),
    path("page/<int:page_id>/", views.play_page, name="play_page"),
    path("choose/<int:page_id>/", views.choose, name="choose"),
    path("stats/", views.stats, name="stats"),
    path("new/", views.story_create, name="story_create"),
    path("<int:story_id>/edit/", views.story_edit, name="story_edit"),
    path("<int:story_id>/delete/", views.story_delete, name="story_delete"),
    path("<int:story_id>/builder/", views.story_builder, name="story_builder"),

]
