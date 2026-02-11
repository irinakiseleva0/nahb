from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from requests.exceptions import RequestException

from .models import Play
from .forms import StoryForm
from .forms import PageForm, ChoiceForm
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
    for k in list(request.session.keys()):
        if k.startswith(f"ended_{story_id}_"):
            del request.session[k]
            request.session.modified = True

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
        "plays_per_story": list(plays_per_story),
        "endings": list(endings),
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


def story_builder(request, story_id: int):
    try:
        story = flask_get(f"/stories/{story_id}")
    except RequestException as e:
        raise Http404(f"Flask API error: {e}")

    page_form = PageForm()
    choice_form = ChoiceForm()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_page":
            page_form = PageForm(request.POST)
            if page_form.is_valid():
                payload = page_form.cleaned_data

                if not payload.get("is_ending"):
                    payload.pop("ending_label", None)

                try:
                    created = flask_post(f"/stories/{story_id}/pages", payload)
                    messages.success(
                        request, f"Page created (id={created.get('id')}).")
                    return redirect("story_builder", story_id=story_id)
                except RequestException as e:
                    messages.error(request, f"Failed to create page: {e}")

        elif action == "add_choice":
            choice_form = ChoiceForm(request.POST)
            if choice_form.is_valid():
                payload = choice_form.cleaned_data
                page_id = payload.pop("page_id")
                try:
                    created = flask_post(f"/pages/{page_id}/choices", payload)
                    messages.success(
                        request, f"Choice created (id={created.get('id')}).")
                    return redirect("story_builder", story_id=story_id)
                except RequestException as e:
                    messages.error(request, f"Failed to create choice: {e}")

        else:
            messages.error(request, "Unknown action.")

    return render(
        request,
        "stories/story_builder.html",
        {
            "story": story,
            "page_form": page_form,
            "choice_form": choice_form,
        },
    )
