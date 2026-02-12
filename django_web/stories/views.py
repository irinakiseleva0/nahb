from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from .models import Play, StoryOwnership
from .forms import StoryForm, PageForm, ChoiceForm
from web.flask_client import flask_get, flask_post, flask_put, flask_delete
from .permissions import author_required


# Helpers (Level 16 ownership)

def require_story_owner(request, story_id: int):

    if request.user.is_staff:
        return
    get_object_or_404(StoryOwnership, story_id=story_id, owner=request.user)


# Public pages

def story_list(request):

    try:
        stories = flask_get("/stories", params={"status": "published"})
        error = None
    except Exception as e:
        stories = []
        error = f"Flask API error: {e}"

    return render(request, "stories/story_list.html", {"stories": stories, "error": error})


@login_required
def stats(request):
    qs = Play.objects.all()
    if not request.user.is_staff:
        qs = qs.filter(user=request.user)

    plays_per_story = (
        qs.values("story_id")
        .annotate(plays=Count("id"))
        .order_by("-plays")
    )

    endings = (
        qs.values("story_id", "ending_page_id")
        .annotate(count=Count("id"))
        .order_by("story_id", "-count")
    )

    return render(
        request,
        "stories/stats.html",
        {"plays_per_story": list(plays_per_story), "endings": list(endings)},
    )


# Gameplay (Level 16: login required + Play.user)

@login_required
def play_start(request, story_id: int):
    # clear "ended" keys for this story run
    for k in list(request.session.keys()):
        if k.startswith(f"ended_{story_id}_"):
            del request.session[k]

    # block suspended stories
    try:
        story = flask_get(f"/stories/{story_id}")
        if story.get("status") == "suspended":
            messages.error(request, "This story is suspended.")
            return redirect("story_list")
    except Exception as e:
        raise Http404(f"Flask API error: {e}")

    try:
        data = flask_get(f"/stories/{story_id}/start")
    except Exception:
        messages.error(
            request,
            "This story has no start page yet. Open Build and create a start page.",
        )
        return redirect("story_builder", story_id=story_id)

    page = data["page"]
    choices = data.get("choices", [])
    return render(request, "stories/play_page.html", {"page": page, "choices": choices})


@login_required
def play_page(request, page_id: int):
    try:
        data = flask_get(f"/pages/{page_id}")
    except Exception as e:
        raise Http404(f"Flask API error: {e}")

    page = data["page"]
    choices = data.get("choices", [])

    if page.get("is_ending"):
        story_id = page.get("story_id")
        ending_id = page.get("id")

        key = f"ended_{story_id}_{ending_id}"
        if not request.session.get(key):
            # Level 16: Play must be linked to user
            Play.objects.create(
                user=request.user,
                story_id=story_id,
                ending_page_id=ending_id,
            )
            request.session[key] = True

    return render(request, "stories/play_page.html", {"page": page, "choices": choices})


@login_required
def choose(request, page_id: int):
    if request.method != "POST":
        return redirect("play_page", page_id=page_id)

    next_page_id = request.POST.get("next_page_id")
    if not next_page_id:
        return redirect("play_page", page_id=page_id)

    return redirect("play_page", page_id=int(next_page_id))


# Author tools (Level 16: login + role + ownership)

@author_required
@login_required
def story_create(request):
    if request.method == "POST":
        form = StoryForm(request.POST)
        if form.is_valid():
            created = flask_post("/stories", form.cleaned_data)

            # save ownership in Django
            StoryOwnership.objects.create(
                story_id=created["id"], owner=request.user)

            messages.success(request, "Story created in Flask.")
            return redirect("story_list")
    else:
        form = StoryForm(initial={"status": "published"})

    return render(request, "stories/story_form.html", {"form": form, "mode": "create"})


@author_required
@login_required
def story_edit(request, story_id: int):
    require_story_owner(request, story_id)

    if request.method == "POST":
        form = StoryForm(request.POST)
        if form.is_valid():
            flask_put(f"/stories/{story_id}", form.cleaned_data)
            messages.success(request, "Story updated in Flask.")
            return redirect("story_list")
    else:
        try:
            s = flask_get(f"/stories/{story_id}")
        except Exception as e:
            raise Http404(f"Flask API error: {e}")

        form = StoryForm(
            initial={
                "title": s.get("title"),
                "description": s.get("description"),
                "status": s.get("status"),
                "start_page_id": s.get("start_page_id"),
            }
        )

    return render(
        request,
        "stories/story_form.html",
        {"form": form, "mode": "edit", "story_id": story_id},
    )


@author_required
@login_required
def story_delete(request, story_id: int):
    require_story_owner(request, story_id)

    if request.method == "POST":
        try:
            flask_delete(f"/stories/{story_id}")
        except Exception as e:
            messages.error(request, f"Delete failed: {e}")
            return redirect("story_list")

        # remove ownership record too
        StoryOwnership.objects.filter(story_id=story_id).delete()

        messages.success(request, "Story deleted in Flask.")
        return redirect("story_list")

    try:
        s = flask_get(f"/stories/{story_id}")
    except Exception as e:
        raise Http404(f"Flask API error: {e}")

    return render(request, "stories/story_delete.html", {"story": s})


@author_required
@login_required
def story_builder(request, story_id: int):
    require_story_owner(request, story_id)

    try:
        story = flask_get(f"/stories/{story_id}")
    except Exception as e:
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
                except Exception as e:
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
                except Exception as e:
                    messages.error(request, f"Failed to create choice: {e}")

        else:
            messages.error(request, "Unknown action.")

    return render(
        request,
        "stories/story_builder.html",
        {"story": story, "page_form": page_form, "choice_form": choice_form},
    )
