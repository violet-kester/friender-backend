"""SQLAlchemy models for Dislikes"""

from models.models import db
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

class Dislikes(db.Model):
    """Connection of a user_disliking <-> disliked_user."""

    __tablename__ = 'dislikes'

    user_being_disliked_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_disliking_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )