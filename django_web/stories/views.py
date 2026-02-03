from django.shortcuts import render
from requests.exceptions import RequestException
from web.flask_client import flask_get


def story_list(request):
    try:
        stories = flask_get("/stories", params={"status": "published"})
        error = None
    except RequestException as e:
        stories = []
        error = f"Flask API is not reachable: {e}"

    return render(request, "stories/story_list.html", {"stories": stories, "error": error})
