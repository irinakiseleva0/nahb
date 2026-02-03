from django.http import Http404
from django.shortcuts import render, redirect
from requests.exceptions import RequestException

from web.flask_client import flask_get
from .models import Play


def story_list(request):
    try:
        stories = flask_get("/stories", params={"status": "published"})
        error = None
    except RequestException as e:
        stories = []
        error = f"Flask API is not reachable: {e}"

    return render(request, "stories/story_list.html", {"stories": stories, "error": error})


def play_start(request, story_id: int):
    try:
        data = flask_get(f"/stories/{story_id}/start")
    except RequestException as e:
        raise Http404(f"Flask API error: {e}")

    page = data["page"]
    choices = data.get("choices", [])

    if page.get("is_ending"):
        Play.objects.create(
            story_id=page.get("story_id"),
            ending_page_id=page.get("id"),
        )

    return render(request, "stories/play_page.html", {"page": page, "choices": choices})


def play_page(request, page_id: int):
    try:
        data = flask_get(f"/pages/{page_id}")
    except RequestException as e:
        raise Http404(f"Flask API error: {e}")

    page = data["page"]
    choices = data.get("choices", [])
    
    if page.get("is_ending"):
        Play.objects.create(
            story_id=page.get("story_id"),
            ending_page_id=page.get("id"),
        )

    return render(request, "stories/play_page.html", {"page": page, "choices": choices})


def choose(request, page_id: int):
    if request.method != "POST":
        return redirect("play_page", page_id=page_id)

    next_page_id = request.POST.get("next_page_id")
    if not next_page_id:
        return redirect("play_page", page_id=page_id)

    return redirect("play_page", page_id=int(next_page_id))
