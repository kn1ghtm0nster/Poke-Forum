"""file is testing the pokemon routes for adding, editing, and removing comments both with and without auth."""

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, User, Comment, Pokemon
from flask import get_flashed_messages, session

os.environ['DATABASE_URL'] = "postgresql:///pokeapi_db"

db.drop_all()
db.create_all()

Pokemon.get_national_dex()
db.session.commit()

app.config['WTF_CSRF_ENABLED'] = False


class TestPokemonViews(TestCase):
    """tests for all pokemon routes that take user input."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Comment.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser_id = 8080
        self.testuser.id = self.testuser_id

        db.session.commit() 
        

    #################################################################
    # TESTS FOR NO AUTH ON POKEMON COMMENT ROUTES.
    #################################################################
    
    def test_add_comment_no_auth_GET(self):
        """testing GET request for new comment without auth."""

        with app.test_client() as client:
            res = client.get('/pokemon/pikachu/add-comment', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Access unauthorized', res.data)

    def test_add_comment_without_auth_POST(self):
        """testing POST request WITHOUT auth to ensure that users are seeing an error message and being routed back to the signup page."""

        with self.client as c:

            res = c.post('/pokemon/charmander/add-comment', data={'comment': 'this should NOT work'}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            # ensuring that users are seeing the flash message.
            self.assertIn(b'Access unauthorized', res.data)

            # ensuring that the signup form is being seen in html response for non-authorized users.
            self.assertIn(b'Sign me up!', res.data)

    def test_delete_comment_no_auth(self):
        """testing no auth to ensure that users that are not authenticated cannot make request to remove specific comments that are already in the db."""

        with self.client as c:

            comment_auth_user = Comment(
                text= 'this pokemon is awesome!',
                user_id=self.testuser.id,
                pokemon_id=3
            )

            db.session.add(comment_auth_user)
            db.session.commit()

            res = c.post(f'/comments/{comment_auth_user.id}/delete', data={'id': comment_auth_user.id}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            
            self.assertIn(b'Access unauthorized.', res.data)

    #################################################################
    # TESTS FOR ADDING COMMENTS WITH AUTH
    #################################################################

    def test_add_comment_with_auth_GET(self):
        """testing GET request with auth to ensure that the comment text area populates."""

        with app.test_client() as client:
            user = User(
                username='dummy123',
                password='testing1234',
                email='success@protonmail.com',
                image_url=None
            )

            User.signup(user.username, user.email, user.password, user.image_url)
            db.session.commit()

            client.post('/login', data={'username': user.username, 'password': user.password}, follow_redirects=True)

            res = client.get('/pokemon/charmander/add-comment', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Add New Comment', html)
    
    def test_add_comment_with_auth_POST(self):
        """testing POST request with auth to ensure that the comment is sent to the backend db."""

        with self.client as c:
            with c.session_transaction() as sess:
                # forcing the session to see user id that was hard coded at the start of the tests (tricking the session) for auth purposes.
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post('/pokemon/charmander/add-comment', data={'comment': 'posting under charmander'}, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)

            # ensuring that the new comment posted was truly added and is visible in the pokemon's view within HTMl elements.
            self.assertIn('posting under charmander', html)
    

    def test_add_comment_with_blank_text_POST(self):
        """testing POST request with auth BUT no comment text to ensure that users see an error message on the front end."""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            res = c.post('/pokemon/charmander/add-comment', data={'comment': None }, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)

            # ensuring that the custom message from the form is being seen on the html response.
            self.assertIn('Comments cannot be blank!', html)

    def test_incorrect_user_add_comment_POST(self):
        """testing POST request to ensure that logged in users cannot add comments as other users."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1234

            wrong_user = User.signup(username='incorrectPerson', email='incorrect@gmail.com', password='asdfasfdsdf', image_url=None)
            db.session.commit()

            res = c.post('/pokemon/pikachu/add-comment', data={'comment': 'this should NOT work'}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            
            self.assertIn(b'Access unauthorized', res.data)

    #################################################################
    # TESTS FOR EDITING A COMMENT WITH AUTH
    #################################################################

    def test_edit_comment_GET(self):
        """testing GET request to make sure that the form is populating on the front end."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            testuser_comment = Comment(
                text='testing edit',
                user_id = self.testuser.id,
                pokemon_id = 1
            )

            db.session.add(testuser_comment)
            db.session.commit()

            res = c.get(f'/comments/{testuser_comment.id}/edit', follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            # checking to see if the comment that we saved to the db is populating on the edit form.
            self.assertIn(b'testing edit', res.data)


    def test_edit_comment_POST(self):
        """testing POST request to make sure that the changes made are saved and reflecting on the frontend."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            testuser_comment_2 = Comment(
                text='editing this one.',
                user_id=self.testuser.id,
                pokemon_id = 13
            )

            db.session.add(testuser_comment_2)
            db.session.commit()

            res = c.post(f'/comments/{testuser_comment_2.id}/edit', data={'comment':'editing this again 2'}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            # checking to see if the updated comment has been saved on the frontend.
            self.assertIn(b'editing this again 2', res.data)

    def test_edit_comment_incorrect_user(self):
        """testing POST request to ensure that other users CANNOT edit comments for other users."""

        with self.client as c:

            wrong_comment = Comment(text='This belongs to another user', user_id=8080, pokemon_id=4)
            
            db.session.add(wrong_comment)
            db.session.commit()

            wrong_user = User.signup(username='weongAgain', email='another@gmail.com', password='ASDFASDsdsdF', image_url=None)

            db.session.commit()

            c.post('/login', data={'username': wrong_user.username, 'password': wrong_user.password}, follow_redirects=True)

            res = c.post(f'/comments/{wrong_comment.id}/edit', data={'comment': 'This also should NOT work'}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            # ensuring that authenticated users are getting an error message if they attempt to edit another user's post.
            self.assertIn(b'Access unauthorized', res.data)

    #################################################################
    # TESTS FOR DELETING COMMENTS WITH AUTH
    #################################################################
    
    def test_delete_comment_with_auth(self):
        """testing delete feature for authenticated users on their own comments"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            

            remove_comment = Comment(
                text= 'remove me',
                user_id = self.testuser.id,
                pokemon_id = 2
            )

            db.session.add(remove_comment)
            db.session.commit()

            res = c.post(f'/comments/{remove_comment.id}/delete', data={'id': remove_comment.id}, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)

            # testing to ensure that we are really redirected to the user's profile page by checking for the user's username.
            self.assertIn(f'{self.testuser.username}', html)

            # checking to ensure that the comment that was removed from the db is no longer appearing in the user's profile page.
            self.assertNotIn('remove me', html)

    def test_delete_comment_wrong_user(self):
        """testing delete feature to ensure users cannot delete comments that belong to different users."""

        with self.client as c:
            
            wrong_comment = Comment(text='Bulbasaur squad!', user_id=self.testuser.id, pokemon_id=1)
            
            db.session.add(wrong_comment)
            db.session.commit()

            incorrect_user = User.signup(username='Hiker_Marsh', email='hikingizfun@protonmail.com', password='geodude22', image_url=None)

            db.session.commit()

            c.post('/login', data={'username': incorrect_user.username, 'password': incorrect_user.password}, follow_redirects=True)

            res = c.post(f'/comments/{wrong_comment.id}/delete', data={'id': wrong_comment.id}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            self.assertIn(b'Access unauthorized', res.data)



