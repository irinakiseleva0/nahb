from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Page, Choice
from app.security import require_api_key  

bp = Blueprint("pages", __name__, url_prefix="/pages")

@bp.get("/<int:page_id>")
def get_page(page_id):
    page = Page.query.get_or_404(page_id)
    return jsonify({"page": page.to_dict(), "choices": [c.to_dict() for c in page.choices]})

@bp.post("/<int:page_id>/choices")
def create_choice(page_id):
    r = require_api_key()
    if r: return r

    Page.query.get_or_404(page_id)
    data = request.get_json(force=True)

    choice = Choice(page_id=page_id, text=data["text"], next_page_id=data["next_page_id"])
    db.session.add(choice)
    db.session.commit()

    return jsonify(choice.to_dict()), 201
