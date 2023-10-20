"""SQLAlchemy models for Likes"""

from models.models import db
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

class Likes(db.Model):
    """Connection of a user_liking <-> liked_user."""

    __tablename__ = 'likes'

    user_being_liked_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_liking_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )