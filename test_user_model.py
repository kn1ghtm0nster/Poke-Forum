"""unit tests for user model class ONLY"""

from app import app
import os
from unittest import TestCase

from models import db, User, Comment,  Pokemon

os.environ['DATABASE_URL'] = "postgresql:///testing_db"

db.drop_all()
db.create_all()

Pokemon.get_national_dex()
db.session.commit()


"""
TODO:
    - add test for user model in the event that an argument is missing from the class (basically testing for an error).
    - add test for user model in the evne incorrect information is entered like a number in the image url section.
"""

class UserModelTestCase(TestCase):
    """Testing user model ONLY"""

    def setUp(self):
        """Create test client before each test"""

        User.query.delete()
        Comment.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """does the user model work as intended?"""

        new_user = User(
            email='testing@testing.com',
            username='testinguser1',
            password='COMPLETELY_HASHED'
        )

        db.session.add(new_user)
        db.session.commit()

        # checking to ensure that the comments for a new user model are completely empty.
        self.assertEqual(len(new_user.comments), 0)

    def test_user_repr(self):
        """Is the user model represented as described in models file?"""

        new_user = User(
            email='testing@testing.com',
            username='testinguser1',
            password='COMPLETELY_HASHED'
        )

        db.session.add(new_user)
        db.session.commit()

        self.assertEqual(
            f'<User #{new_user.id}: {new_user.username}, {new_user.email}>', new_user.__repr__())

    def test_user_authentication(self):
        """Testing the authentication feature through models file."""

        dummy = User.signup(
            username="testing1",
            email="testing1@yahoo.com",
            password="testing1234",
            image_url=None
        )

        u = User.authenticate(dummy.username, "testing1234")

        self.assertIsNotNone(u)
        self.assertEqual(u.id, dummy.id)

    def test_wrong_username(self):
        """Testing wrong username for a new user."""

        correct_user = User.signup(
            username="dj_khaled",
            email="wedabest@gmail.com",
            password="another_one",
            image_url=None
        )

        # ensuring that the wrong username returns a false response from authenticate method on class.
        self.assertFalse(User.authenticate('Dj_khaled', correct_user.password))

    def test_wrong_password(self):
        """Testing wrong password for new user and ensuring that a false response from the authenticate class method is returned."""

        u = User.signup(
            username='wrong_pass',
            email="testing3@yahoo.com",
            password='wrongpassword',
            image_url=None
        )

        self.assertFalse(User.authenticate(u.username, 'Wrongpassword'))