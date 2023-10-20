from app import app
from models.models import db
from models.User import User
from models.File import File
from models.Likes import Likes

db.drop_all()
db.create_all()

u1 = User.signup(
    username='lola_coconato',
    password='password',
    email='lola@email.com',
    hobbies="Workin' night shifts as a freakin' police officer in New York City can be tough on both my body and my freakin' mind. The long hours and irregular sleep patterns can freakin' take a toll on my health and my freakin' relationships. But I know that this is a freakin' essential part of the job, and that by workin' nights, I'm helpin' to keep the freakin' city safe while most people are freakin' asleep. So even on the toughest nights, I stay freakin' positive and focused on the freakin' mission.",
    interests="Bein' a freakin' police officer is a demandin' job, and it's freakin' easy to get caught up in the freakin' stress and intensity of the work. That's why I freakin' prioritize self-care, both on and off the freakin' job. Whether it's takin' a few freakin' minutes to meditate during a break, goin' for a freakin' run after my freakin' shift, or spendin' quality time with my freakin' loved ones, these small freakin' acts of self-care help me to stay freakin' grounded and resilient in the freakin' face of the challenges I encounter as a freakin' police officer in New York City.",
    location='10008'
)

u2 = User.signup(
    username='coolcat22',
    password='password123',
    email='catlover22@gmail.com',
    hobbies='playing with my cats, reading, hiking',
    interests='cat behavior, nature, science fiction',
    location='90210'
)

u3 = User.signup(
    username='foodie_girl',
    password='ilovefood',
    email='foodielover@gmail.com',
    hobbies='cooking, trying new restaurants, wine tasting',
    interests='culinary arts, nutrition, food history',
    location='10011'
)

u4 = User.signup(
    username='travel_buddy',
    password='letsgo',
    email='traveljunkie@gmail.com',
    hobbies='exploring new places, hiking, photography',
    interests='cultural immersion, adventure sports, international cuisine',
    location='94110'
)

u5 = User.signup(
    username='fitness_fanatic',
    password='gymrat',
    email='fitgirl@gmail.com',
    hobbies='weightlifting, yoga, running',
    interests='nutrition, sports science, injury prevention',
    location='60611'
)

# add users to db
db.session.add_all([u1, u2, u3, u4, u5])

db.session.commit()


# create a like relationship between user 1 and user 2
like1 = Likes(user_being_liked_id=2, user_liking_id=1)

# create a like relationship between user 1 and user 3
like2 = Likes(user_being_liked_id=3, user_liking_id=1)

# create a like relationship between user 4 and user 1
like3 = Likes(user_being_liked_id=1, user_liking_id=4)

# create a like relationship between user 2 and user 3
like4 = Likes(user_being_liked_id=3, user_liking_id=2)

# create a like relationship between user 2 and user 3
like5 = Likes(user_being_liked_id=1, user_liking_id=2)

# create a like relationship between user 2 and user 3
like6 = Likes(user_being_liked_id=2, user_liking_id=3)

# add the like relationships to db
db.session.add_all([like1, like2, like3, like4, like5, like6])

# db.session.add_all( seed data )
db.session.commit()