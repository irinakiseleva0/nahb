from __future__ import annotations

from datetime import datetime
from enum import Enum

from .extensions import db


class StoryStatus(str, Enum):
    draft = "draft"
    published = "published"
    suspended = "suspended"


class Story(db.Model):
    __tablename__ = "stories"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.String(20),
        nullable=False,
        default=StoryStatus.draft.value,
    )

    start_page_id = db.Column(db.Integer, db.ForeignKey("pages.id"), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    pages = db.relationship(
        "Page",
        back_populates="story",
        cascade="all, delete-orphan",
        foreign_keys="Page.story_id",
    )
    start_page = db.relationship("Page", foreign_keys=[start_page_id], post_update=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "start_page_id": self.start_page_id,
        }


class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)

    story_id = db.Column(db.Integer, db.ForeignKey("stories.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)

    is_ending = db.Column(db.Boolean, nullable=False, default=False)
    ending_label = db.Column(db.String(120), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    story = db.relationship("Story", back_populates="pages", foreign_keys=[story_id])

    choices = db.relationship(
        "Choice",
        back_populates="page",
        cascade="all, delete-orphan",
        foreign_keys="Choice.page_id",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "story_id": self.story_id,
            "text": self.text,
            "is_ending": self.is_ending,
            "ending_label": self.ending_label,
        }


class Choice(db.Model):
    __tablename__ = "choices"

    id = db.Column(db.Integer, primary_key=True)

    page_id = db.Column(db.Integer, db.ForeignKey("pages.id"), nullable=False)
    text = db.Column(db.String(200), nullable=False)

    next_page_id = db.Column(db.Integer, db.ForeignKey("pages.id"), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    page = db.relationship("Page", back_populates="choices", foreign_keys=[page_id])
    next_page = db.relationship("Page", foreign_keys=[next_page_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "page_id": self.page_id,
            "text": self.text,
            "next_page_id": self.next_page_id,
        }
