from flask import Blueprint, request, jsonify, abort

from app.extensions import db
from app.models import Story, Page
from app.security import require_api_key

bp = Blueprint("stories", __name__, url_prefix="/stories")


@bp.get("")
def list_stories():
    status = request.args.get("status")

    query = Story.query
    if status:
        query = query.filter_by(status=status)

    stories = query.all()
    return jsonify([s.to_dict() for s in stories])


@bp.get("/<int:story_id>")
def get_story(story_id):
    story = Story.query.get_or_404(story_id)
    return jsonify(story.to_dict())


@bp.get("/<int:story_id>/start")
def get_start_page(story_id):
    story = Story.query.get_or_404(story_id)

    if not story.start_page_id:
        abort(400, "Story has no start page")

    page = Page.query.get_or_404(story.start_page_id)

    return jsonify({
        "page": page.to_dict(),
        "choices": [c.to_dict() for c in page.choices]
    })


@bp.post("")
def create_story():
    r = require_api_key()
    if r: return r
    data = request.get_json(force=True)

    story = Story(
        title=data["title"],
        description=data.get("description"),
        status=data.get("status", "draft"),
    )
    db.session.add(story)
    db.session.commit()

    return jsonify(story.to_dict()), 201


@bp.put("/<int:story_id>")
def update_story(story_id):
    story = Story.query.get_or_404(story_id)
    data = request.get_json(force=True)

    story.title = data.get("title", story.title)
    story.description = data.get("description", story.description)
    story.status = data.get("status", story.status)
    story.start_page_id = data.get("start_page_id", story.start_page_id)

    db.session.commit()
    return jsonify(story.to_dict())


@bp.delete("/<int:story_id>")
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)

    db.session.delete(story)
    db.session.commit()
    return "", 204



@bp.post("/<int:story_id>/pages")
def create_page(story_id):
    Story.query.get_or_404(story_id)
    data = request.get_json(force=True)

    page = Page(
        story_id=story_id,
        text=data["text"],
        is_ending=data.get("is_ending", False),
        ending_label=data.get("ending_label"),
    )

    db.session.add(page)
    db.session.commit()

    return jsonify(page.to_dict()), 201

