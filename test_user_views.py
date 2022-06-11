"""File is testing user views ONLY."""

from app import app, CURR_USER_KEY
import os
import re
from unittest import TestCase

from models import db, connect_db, User, Comment, Pokemon
from flask import get_flashed_messages, session

os.environ['DATABASE_URL'] = "postgresql:///pokeapi_db"

db.drop_all()
db.create_all()

Pokemon.get_national_dex()
db.session.commit()

app.config['WTF_CSRF_ENABLED'] = False


class TestViewFunctions(TestCase):
    """Tests for different view functions from main application file."""

    def setup(self):
        """function creates a new user before each test that runs."""

        User.query.delete()
        Comment.query.delete()

        self.client = app.test_client()

    def test_home_view(self):
        """testing main home route view."""
        with app.test_client() as client:
            res = client.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>main page!</h1>', html)

    def test_signup_view(self):
        """testing signup route GET requests only."""

        with app.test_client() as client:
            res = client.get('/signup')
            html  = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Sign me up!', html)

    def test_login_view(self):
        """testing login route GET requests only."""

        with app.test_client() as client:
            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button class="btn btn-primary btn-lg">Log in</button>', html)

    def test_signup(self):
        """testing signup feature to ensure a new user can successfully sign up"""

        with app.test_client() as client:
            data = {
                'username': 'anon_man1',
                'email': 'anon@protonmail.com',
                'password': 'dc>marvel1',
                'image_url': None
            }

            res = client.post('/signup', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'Welcome to the community, {data["username"]}!', html)

    def test_signup_no_username(self):
        """testing signup feature to ensure that users cannot sign up without entering a username."""

        with app.test_client() as client:
            data = {'username': None, 'email': 'testing@gmail.com',
                    'password': 'adsfasdf'}
            
            res = client.post('/signup', data=data)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'This field is required.', res.data)

    def test_signup_no_password(self):
        """testing signup feature to ensure that users cannot sign up without entering a password"""

        with app.test_client() as client:
            data = {
                'username': 'failure_password',
                'email': 'diequint@hotmail.com',
                'password': None,
                'image_url': None
            }

            res = client.post('/signup', data=data)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Password must be at least 8 characters long!', res.data)

    def test_signup_short_password(self):
        """testing signup feature to ensure that users see error message if their password is too short"""

        with app.test_client() as client:
            data = {
                'username': 'el_barto',
                'email': 'los_simpsons@gmail.com',
                'password': '1234',
                'image_url': None
            }

            res = client.post('/signup', data=data)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Password must be at least 8 characters long!', res.data)

    def test_signup_no_email(self):
        """testing signup feature to ensure that users are not allowed to signup with a missing email."""

        with app.test_client() as client:
            data = {
                'username': 'failure',
                'password': 'noEmail_thx',
                'email': None,
                'image_url': None
            }

            res = client.post('/signup', data=data)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'This field is required.', res.data)

    def test_signup_invalid_email(self):
        """testing signup feature to ensure that users cannot signup with an invalid email address."""

        with app.test_client() as client:
            data = {
                'username': 'noEmailsHere',
                'email': 'hehexd',
                'password': 'this_should_fail',
                'image_url': None
            }

            res = client.post('/signup', data=data)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Invalid email address.', res.data)

    def test_auth_failure(self):
        """testing to ensure that non-authenticated users are able to see specific sections of the website such as other user profiles."""

        with app.test_client() as client:
            user = User.signup(username='dummy12', email='testingagain', password='anotheronehehe', image_url=None)

            db.session.commit()

            res = client.get(f'/users/{user.id}', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized', str(res.data))

    def test_user_edit_no_auth(self):
        """testing redirection for users that are attempting to access a user's edit profile view without auth."""

        with app.test_client() as client:

            test_user = User(
                username='person1',
                email='person@person.com',
                password='this_is_bad',
                image_url=None
            )

            User.signup(test_user.username, test_user.email, test_user.password, test_user.image_url)
            db.session.commit()

            res = client.get('/users/edit', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Access unauthorized.', res.data)

    def test_user_edit_incorrect_account(self):
        """testing to ensure that logged in users are not able to make edits to other user accounts."""

        with app.test_client() as c:

            first_user = User.signup(username='user_number_1', email='winning@gmail.com', password='anotherdayofcode', image_url=None)
            db.session.commit()

            second_user = User.signup(username='bigPlayShay', email='mrshape@yahoo.com', password='SKIIIIIIIIIIIIIIIIIIP', image_url=None)
            db.session.commit()

            c.post('/login', data={'username': second_user.username, 'password': second_user.password}, follow_redirects=True)

            res = c.post('/users/edit', data={'id': first_user.id, 'password': first_user.password, 'username': 'this_should_fail', 'email': first_user.email, 'image_url': None}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            self.assertIn(b'Access unauthorized', res.data)

    def test_login(self):
        """testing login feature"""

        with app.test_client() as client:

            new_user = User(
                username='petor_griffin',
                email='pg@protonmail.com',
                password='testing_again',
                image_url='https://images.unsplash.com/photo-1522529599102-193c0d76b5b6?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NXx8ZmFtaWx5JTIwZ3V5fGVufDB8fDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60'
            )

            User.signup(new_user.username, new_user.email, new_user.password, new_user.image_url)
            db.session.commit()

            res = client.post('/login', data={'username': new_user.username, 'password': new_user.password}, follow_redirects=True)
            html  = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'Welcome back, {new_user.username}!', html)
            
    def test_logout(self):
        """testing logout feature"""

        with app.test_client() as client:

            test_user = User.signup('lonestar', 'hot@outlook.com', 'I_am_scared', None)
            db.session.commit()

            User.authenticate(test_user.username, test_user.password)

            res = client.get('/logout', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('You Have Logged Out', html)

    def test_delete_user_profile(self):
        """testing if a user can actually completely delete their user profile and testing to ensure that the user profile is no longer visible in the database."""

        with app.test_client() as client:

            remove_user = User(
                username='remove',
                email='remove@gmail.com',
                password='remove1234',
                image_url= None
            )
            
            User.signup(remove_user.username, remove_user.email, remove_user.password, remove_user.image_url)
            db.session.commit()

            User.authenticate(remove_user.username, remove_user.password)

            res = client.post('/users/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            # check below is making sure that the removed user's ID is set as None since they deleted their profile.
            self.assertIsNone(remove_user.id)

    def test_delete_profile_no_auth(self):
        """testing that a user is redirected to home page if they attempt to delete another user's profile without auth."""

        with app.test_client() as client:

            authenticated_user = User(
                username='billy-bob',
                email='yehawbrother@gmail.com',
                password='yehawbrother1',
                image_url=None
            )

            User.signup(authenticated_user.username, authenticated_user.email, authenticated_user.password, authenticated_user.image_url)
            db.session.commit()

            res = client.post('/users/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Access unauthorized', res.data)

    def test_delete_profile_wrong_user(self):
        """testing that a logged in user CANNOT delete another user account."""

        with app.test_client() as c:

            og_user = User.signup(username='mr_snoop_D0G', email='lavidamasfina@outlook.com', password='mrworldwide', image_url=None)
            db.session.commit()

            second_user = User.signup(username='testingagain', email='testing23@gmail.com', password='testing1234', image_url=None)
            db.session.commit()

            c.post('/login', data={'username': second_user.username, 'password': second_user.password}, follow_redirects=True)

            res = c.post('/users/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            self.assertIn(b'Access unauthorized', res.data)

    def test_pokemon_generations_view(self):
        """testing the second page that users will see which is the list of all generations of pokedexes."""

        with app.test_client() as client:
            res = client.get('/pokedex-generations')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('kanto', html)

    def test_pokemon_generation_individual_view(self):
        """testing to ensure that data for a specific generation pokedex is visible."""

        with app.test_client() as client:
            res = client.get('/pokedex-generations/hoenn')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('spoink', html)

    def test_pokemon_details_view(self):
        """testing to ensure that data for a specific pokemon is visible"""

        with app.test_client() as client:
            res = client.get('/pokemon/charmander/detail')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Fire', html)

