from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from requests.exceptions import RequestException

from .models import Play, StoryOwnership, PlaySession
from .forms import StoryForm, PageForm, ChoiceForm
from web.flask_client import flask_get, flask_post, flask_put, flask_delete
from .permissions import author_required


# Helpers

def _get_session_key(request) -> str:
    #Ensures Django session exists (needed for anonymous autosave too).
    
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def require_story_owner(request, story_id: int) -> None:
    
    #Level 16 ownership: staff can manage everything, others can manage only their own stories.
    
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

    # Autosave Resume button support (works even for anonymous sessions)
    session_key = _get_session_key(request)

    story_ids = [s.get("id") for s in stories if isinstance(s, dict) and s.get("id") is not None]
    sessions = PlaySession.objects.filter(session_key=session_key, story_id__in=story_ids)
    resume_map = {ps.story_id: ps.current_page_id for ps in sessions}

    return render(
        request,
        "stories/story_list.html",
        {"stories": stories, "error": error, "resume_map": resume_map},
    )

# non-staff sees only their plays/staff sees all plays
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
    session_key = _get_session_key(request)

    # Optional: resume via ?resume=1
    if request.GET.get("resume") == "1":
        ps = PlaySession.objects.filter(session_key=session_key, story_id=story_id).first()
        if ps:
            return redirect("play_page", page_id=ps.current_page_id)

    # Clear "ending counted" flags for this story
    for k in list(request.session.keys()):
        if k.startswith(f"ended_{story_id}_"):
            del request.session[k]

    try:
        data = flask_get(f"/stories/{story_id}/start")
    except RequestException:
        messages.error(request, "This story has no start page yet. Open Build and create a start page.")
        return redirect("story_builder", story_id=story_id)

    page = data["page"]
    choices = data.get("choices", [])

    # Autosave start page
    PlaySession.objects.update_or_create(
        session_key=session_key,
        story_id=story_id,
        defaults={
            "current_page_id": page["id"],
            "user": request.user,
        },
    )

    return render(
        request,
        "stories/play_page.html",
        {"page": page, "choices": choices, "story_id": story_id},
    )


@login_required
def play_page(request, page_id: int):
    try:
        data = flask_get(f"/pages/{page_id}")
    except Exception as e:
        raise Http404(f"Flask API error: {e}")

    page = data["page"]
    choices = data.get("choices", [])

    # Autosave current page
    session_key = _get_session_key(request)
    story_id = page.get("story_id")
    if story_id is not None:
        PlaySession.objects.update_or_create(
            session_key=session_key,
            story_id=story_id,
            defaults={
                "current_page_id": page["id"],
                "user": request.user,
            },
        )

    # If ending reached -> store Play (linked to user for Level 16)
    if page.get("is_ending"):
        ending_id = page.get("id")

        key = f"ended_{story_id}_{ending_id}"
        if not request.session.get(key):
            Play.objects.create(
                user=request.user,
                story_id=story_id,
                ending_page_id=ending_id,
            )
            request.session[key] = True

    return render(request, "stories/play_page.html", {"page": page, "choices": choices, "story_id": story_id})


@login_required
def play_resume(request, story_id: int):
    session_key = _get_session_key(request)
    ps = PlaySession.objects.filter(session_key=session_key, story_id=story_id).first()
    if not ps:
        messages.info(request, "No saved progress for this story. Starting from the beginning.")
        return redirect("play_start", story_id=story_id)
    return redirect("play_page", page_id=ps.current_page_id)


@login_required
def play_reset(request, story_id: int):
    session_key = _get_session_key(request)
    PlaySession.objects.filter(session_key=session_key, story_id=story_id).delete()

    for k in list(request.session.keys()):
        if k.startswith(f"ended_{story_id}_"):
            del request.session[k]

    messages.success(request, "Progress reset. Starting from the beginning.")
    return redirect("play_start", story_id=story_id)


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

            # Save ownership in Django
            StoryOwnership.objects.create(story_id=created["id"], owner=request.user)

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
                    messages.success(request, f"Page created (id={created.get('id')}).")
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
                    messages.success(request, f"Choice created (id={created.get('id')}).")
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
