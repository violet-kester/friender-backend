import boto3

"""SQLAlchemy models for Files"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from models.models import db


class File(db.Model):
    """File in the system."""

    __tablename__ = 'files'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    filename = db.Column(
        db.String(100),
        nullable=False,
    )

    aws_key = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    bucket = db.Column(
        db.String(100),
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        unique=False
    )

    @classmethod
    def get_image_keys_by_id(cls, id):
        """Gets list of user image files by id.
        Accepts user id.
        Returns list of image keys : [ key1, key2, ... ]
        """
        image_files = cls.query.filter_by(user_id=id).all()

        image_keys = [f.aws_key for f in image_files]
        print("image_keys FROM CLASS METHOD", image_keys)

        return image_keys

    # db 1:M (user:files) relationship to user table on user_id
