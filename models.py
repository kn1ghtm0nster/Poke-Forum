from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import requests

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.

    """

    db.app = app
    db.init_app(app)


class Pokemon(db.Model):
    """class for each individual pokemon which will also contain the relationships for the comments that each user has made."""

    __tablename__ = 'pokemon'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    pokemon_name = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    comments = db.relationship('Comment', cascade="all,delete")

    @classmethod
    def get_national_dex(cls):
        """function is making a call to the external API which will retrieve all the pokemon information and store the information on the backend db. This function does NOT run in the main application file but instead will be run on the seed file to populate the db."""
        res = requests.get('https://pokeapi.co/api/v2/pokedex/national')

        pokemon_object = res.json()['pokemon_entries']

        for item in pokemon_object:
            # pokemon_name =
            new_pokemon = Pokemon(
                pokemon_name=item['pokemon_species']['name']
            )
            db.session.add(new_pokemon)
        return 'completed'


class User(db.Model):
    """user class"""

    __tablename__ = 'users'

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    comments = db.relationship('Comment', cascade="all,delete")

    @classmethod
    def signup(cls, username, email, password, image_url):
        """function is responsible for taking information from the user signup form and creating a new user profile with a hashed password."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        # db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        """function is responsible for authenticating a user."""
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Comment(db.Model):
    """class for each individual comment that users make on a pokemon."""

    __tablename__ = 'comments'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        nullable=False,
    )

    pokemon_id = db.Column(
        db.Integer,
        db.ForeignKey('pokemon.id', ondelete='cascade'),
        nullable=False,
    )

    user = db.relationship('User')

    pokemon = db.relationship('Pokemon')
