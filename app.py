import os    # Import os module for env vars and db link (sql-alchemy)
import boto3
import uuid
from dotenv import load_dotenv
from botocore.config import Config

from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    get_jwt_identity,
    verify_jwt_in_request,
    decode_token,
    JWTManager
)
from flask import (
    Flask, request, jsonify, session
)
from flask_cors import CORS, cross_origin, logging
# Import DebugToolbarExtension class
from flask_debugtoolbar import DebugToolbarExtension
# from sqlalchemy.exc import IntegrityError

from models.models import db, connect_db   # sql-alchemy
# from models import User, File
from models.User import User
from models.File import File
from models.Likes import Likes

load_dotenv()

# CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# enable cors
CORS(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
jwt = JWTManager(app)

# debug, session -PUT ACTUAL VALUE IN ENV VAR
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(      # sql-alchemy
    "DATABASE_URL", 'postgresql:///friender')  # sql-alchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False         # sql-alchemy
app.config['SQLALCHEMY_ECHO'] = True            # sql-alchemy
# app.config['CORS_HEADERS'] = 'Content-Type'
# app.config['CORS_HEADERS'] = 'Access-Control-Allow-Origin'

connect_db(app)     # sql-alchemy

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)  # debug

AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')

print("DEFAULT REGION", os.environ.get('AWS_DEFAULT_REGION'))

s3 = boto3.resource('s3')
# s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))

s3_client = boto3.client(
    "s3",
    # os.environ.get('AWS_DEFAULT_REGION'),
    "us-east-2",
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    config=Config(signature_version='s3v4')
)


# TODO: add middleware -
# could use verify_jwt_in_request with optional=True

@app.before_request
def verify_jwt():
    """ Check that a token is valid, if it is provided.
        Token is optional.
    """

    verify_jwt_in_request(locations=['headers', 'cookies'], optional=True)
    # try:
    #     # optional = no token is okay

    # except:
    #     # return error that token is invalid
    #     return jsonify({'message': 'Token is invalid!'}), 401


@jwt_required()
@app.post("/users/<id>/images")
# @cross_origin(origins='*', headers=['Content-Type', 'Access-Control-Allow-Origin', 'Authorization'])
def upload_img(id):
    """Handle profile image upload

    Create new File for profile image(s) and uploads profile images to s3 bucket,
    adding the s3 image key to db.

    Returns string: "[img.filename] successfully uploaded!" or Error message
    """

    # TODO: validate file? checking if it has executable code? sanitize
    uploaded_imgs = request.files.getlist("file")  # MultiDict

    # print("request.files", request.files)
    # print("UPLOADED IMGS = ", uploaded_imgs)

    for img in uploaded_imgs:
        # img = request.files.get('file')

        # TODO: handle errors if no file

        # create unique key for s3 bucket using uuid & filename
        key = f"{uuid.uuid4()}-{img.filename}"

        # TODO: put this in a try block? catch & send any errors?
        # upload image file into s3 bucket
        s3.Bucket(AWS_BUCKET_NAME).put_object(Key=key, Body=img)

        print("USER_ID FROM UPLOAD=====", id)

        new_img = File(
            filename=img.filename,
            aws_key=key,
            bucket=AWS_BUCKET_NAME,
            user_id=id
        )

        db.session.add(new_img)

    # After all iterations: commit all added Files to database
    db.session.commit()

    return f"{img.filename} successfully uploaded!"


@app.get("/users/<id>/images")
def get_images_by_id(id):

    image_keys = File.get_image_keys_by_id(id)
    image_urls = [s3_client.generate_presigned_url(
        'get_object',
        Params={'Key': key, 'Bucket': AWS_BUCKET_NAME},
        ExpiresIn=3600
    ) for key in image_keys]

    return jsonify({"images": image_urls})


@app.post("/login")
def login():

    # TODO: data validation

    user = User.authenticate(
        request.json.get("username"),
        request.json.get("password")
    )

    # if username != "test" or password != "test":
    #     return jsonify({"msg": "Bad username or password"}), 401

    # data stored on "sub" of token
    token = create_access_token(identity=user.id)
    print("token = ", token)
    return jsonify(token=token)


@app.post("/users")
def create_user():
    """Handle user signup.

    Accepts JSON {
        "username": "testuser",
        "password": "password",
        "email": "test@mail.com",
        "hobbies": "I like hobbies",
        "interests": "I have interests",
        "location": "95816"
    }

    Create new User and add to db.

    Returns new user JSON data:
    {
            "user": {
                    id,
                    username,
                    email,
                    hobbies,
                    interests,
                    location
                }
    }
    """

    # grab new_user data, add new user to db
    new_user = User.signup(
        username=request.json.get('username'),
        password=request.json.get('password'),
        email=request.json.get('email'),
        hobbies=request.json.get('hobbies'),
        interests=request.json.get('interests'),
        location=request.json.get('location'),
        # friend_radius=request.form.get('friend_radius')
    )

    db.session.commit()

    # create response with only selected fields
    response_data = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "hobbies": new_user.hobbies,
        "interests": new_user.interests,
        "location": new_user.location,
        # "friend_radius": new_user.friend_radius
    }

    # TODO: ? serialized = response_data.serialize()

    # return 201 / new user json
    return (jsonify(response_data), 201)


@app.get("/users/<id>")
def get_user(id):
    """Get user by id.
    Returns user info: {
            "user": {
                    id,
                    username,
                    email,
                    hobbies,
                    interests,
                    location
                }
    }
    """

    user = User.get_user_by_id(id)

    return jsonify(user=user)


@app.post("/users/like/<int:liked_id>")
def like_user(liked_id):
    """Add a follow for the currently-logged-in user.
    """

    current_user_id = get_jwt_identity()
    print("user in like_user", current_user_id)

    # liked_user = User.query.get_or_404(liked_id)

    new_like = Likes(
        user_being_liked_id=liked_id,
        user_liking_id=current_user_id
    )
    db.session.add(new_like)
    db.session.commit()

    return "Success!"


@app.get('/users/<int:user_id>/matches')
def get_matches(user_id):
    """Get list of matched users for a user by id."""

    current_user = User.query.get_or_404(user_id)

    match_instances = current_user.get_matches()
    print("match instances=", match_instances)

    matches = []

    # iterate over matches
    for match in match_instances:

        # grab image keys
        match_image_keys = File.get_image_keys_by_id(match.id)

        # grab image urls
        match_image_urls = [s3_client.generate_presigned_url(
            'get_object',
            Params={'Key': key, 'Bucket': AWS_BUCKET_NAME},
            ExpiresIn=3600
        ) for key in match_image_keys]

        # craft array of objects - including array of imgs
        match_data = {
            "id": match.id,
            "username": match.username,
            "email": match.email,
            "hobbies": match.hobbies,
            "interests": match.interests,
            "location": match.location,
            "img_urls": match_image_urls
        }

        matches.append(match_data)

        # TODO: how can we designate a profile image

    return matches


@app.get('/users/<int:user_id>/unrated')
def get_unrated(user_id):
    """Route returns JSON of a list of users that have not been liked or
    disliked by the current user
    """

    user = User.query.get_or_404(user_id)

    unrated_users_instances = user.get_unrated_users()

    unrated_users = []

    # iterate over matches
    for unrated_user in unrated_users_instances:

        # grab image keys
        unrated_user_image_keys = File.get_image_keys_by_id(unrated_user.id)

        # grab image urls
        unrated_user_image_urls = [s3_client.generate_presigned_url(
            'get_object',
            Params={'Key': key, 'Bucket': AWS_BUCKET_NAME},
            ExpiresIn=3600
        ) for key in unrated_user_image_keys]

        # craft array of objects - including array of imgs
        unrated_user_data = {
            "id": unrated_user.id,
            "username": unrated_user.username,
            "email": unrated_user.email,
            "hobbies": unrated_user.hobbies,
            "interests": unrated_user.interests,
            "location": unrated_user.location,
            # "img_urls": unrated_user_image_urls
        }

        unrated_users.append(unrated_user_data)

    return unrated_users
