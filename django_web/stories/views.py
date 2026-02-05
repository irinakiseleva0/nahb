from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from requests.exceptions import RequestException

from .models import Play
from .forms import StoryForm
from web.flask_client import flask_get, flask_post, flask_put, flask_delete

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

    return render(request, "stories/play_page.html", {"page": page, "choices": choices})



def play_page(request, page_id: int):
    try:
        data = flask_get(f"/pages/{page_id}")
    except RequestException as e:
        raise Http404(f"Flask API error: {e}")

    page = data["page"]
    choices = data.get("choices", [])

    if page.get("is_ending"):
        story_id = page.get("story_id")
        ending_id = page.get("id")

        key = f"ended_{story_id}_{ending_id}"
        if not request.session.get(key):
            Play.objects.create(story_id=story_id, ending_page_id=ending_id)
            request.session[key] = True

    return render(request, "stories/play_page.html", {"page": page, "choices": choices})


def choose(request, page_id: int):
    if request.method != "POST":
        return redirect("play_page", page_id=page_id)

    next_page_id = request.POST.get("next_page_id")
    if not next_page_id:
        return redirect("play_page", page_id=page_id)

    return redirect("play_page", page_id=int(next_page_id))



def stats(request):
    plays_per_story = (
        Play.objects.values("story_id")
        .annotate(plays=Count("id"))
        .order_by("-plays")
    )

    endings = (
        Play.objects.values("story_id", "ending_page_id")
        .annotate(count=Count("id"))
        .order_by("story_id", "-count")
    )

    return render(request, "stories/stats.html", {
        "plays_per_story": plays_per_story,
        "endings": endings,
    })

def story_create(request):
    if request.method == "POST":
        form = StoryForm(request.POST)
        if form.is_valid():
            flask_post("/stories", form.cleaned_data)
            messages.success(request, "Story created in Flask.")
            return redirect("story_list")
    else:
        form = StoryForm(initial={"status": "published"})
    return render(request, "stories/story_form.html", {"form": form, "mode": "create"})


def story_edit(request, story_id: int):
    if request.method == "POST":
        form = StoryForm(request.POST)
        if form.is_valid():
            flask_put(f"/stories/{story_id}", form.cleaned_data)
            messages.success(request, "Story updated in Flask.")
            return redirect("story_list")
    else:
        s = flask_get(f"/stories/{story_id}")
        form = StoryForm(initial={
            "title": s.get("title"),
            "description": s.get("description"),
            "status": s.get("status"),
            "start_page_id": s.get("start_page_id"),
        })
    return render(request, "stories/story_form.html", {"form": form, "mode": "edit", "story_id": story_id})


def story_delete(request, story_id: int):
    if request.method == "POST":
        flask_delete(f"/stories/{story_id}")
        messages.success(request, "Story deleted in Flask.")
        return redirect("story_list")

    s = flask_get(f"/stories/{story_id}")
    return render(request, "stories/story_delete.html", {"story": s})
