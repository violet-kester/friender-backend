"""SQLAlchemy models for User"""

from models.models import db
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from models.Likes import Likes
from models.Dislikes import Dislikes

bcrypt = Bcrypt()

DEFAULT_IMAGE_URL = "/static/images/default-pic.png"


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    hobbies = db.Column(
        db.Text,
        nullable=False
    )

    interests = db.Column(
        db.Text,
        nullable=False
    )

    location = db.Column(
        db.String(5),
        nullable=False
    )

    # friend_radius = db.Column(
    #     db.Integer,
    #     nullable=False
    # )

    @classmethod
    def signup(cls,
               username,
               password,
               email,
               hobbies,
               interests,
               # friend_radius
               location,
               ):
        """Sign up user.

        Hashes password and adds user to system.
        """
        print("input password=", password)
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        print("hashed pwd=", hashed_pwd)

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
            hobbies=hobbies,
            interests=interests,
            location=location,
            # friend_radius=friend_radius
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user with `username` and `password`.

        Searches for a user whose with matching password hash.
        If found, returns that user object.

        If not, returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def get_user_by_id(cls, id):
        """Gets user by id from db.
        Accepts id.
        Returns user object: {
            id,
            username,
            email,
            hobbies,
            interests,
            location
        }
        """

        user = cls.query.filter_by(id=id).first()

        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "hobbies": user.hobbies,
                "interests": user.interests,
                "location": user.location
            }

        return False

    def toDict(self):
        """Serialize data"""

        return {
            "id": self.id,
            "username": self.username
        }
    # FIXME: FINISH  SERIALIZE

    # 1:M relationship to Files (User:Files)

    # messages = db.relationship('Message', backref="user")

    liked_users = db.relationship(
        "User",
        secondary="likes",
        primaryjoin=(Likes.user_being_liked_id == id),
        secondaryjoin=(Likes.user_liking_id == id),
        backref="users_liking",
    )

    disliked_users = db.relationship(
        "User",
        secondary="dislikes",
        primaryjoin=(Dislikes.user_being_disliked_id == id),
        secondaryjoin=(Dislikes.user_disliking_id == id),
        backref="users_disliking",
    )

    def get_unrated_users(self):
        """Get all users that this user has not liked or disliked"""

        all_users = User.query.all()
        unrated_users = []
        # if not currently in likes or dislikes
        for user in all_users:
            if (
                user not in self.liked_users and
                user not in self.disliked_users and
                user.id != self.id
            ):
                unrated_users.append(user)

        # return that list of users
        return unrated_users

    def get_matches(self):
        """Get all users that have matched with this user
        (users that this user likes and that user likes them back)
        """

        matches = []

        for user in self.liked_users:
            if self in user.liked_users:
                matches.append(user)

        return matches
