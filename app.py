import os
import re
import requests
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import AddNewUserForm, EditUserForm, LoginForm, CommentForm, EditCommentForm
from models import db, connect_db, User, Comment, Pokemon
from flask_bcrypt import Bcrypt

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

uri = os.environ.get('DATABASE_URL', 'postgresql:///pokeapi_db')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = AddNewUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        flash(f'Welcome to the community, {user.username}!', 'success')
        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash('You Have Logged Out', 'success')
    return redirect('/login')

########################################################################################
# USER ROUTES
########################################################################################

@app.route('/')
def home():
    """if the user is not logged in, we will show the main landing page otherwise, users will be redirected to the 'pokedex-generations' route."""

    if not g.user:
        return render_template('home.html')
    
    return redirect('/pokedex-generations')


@app.route('/users/<int:user_id>')
def profile_view(user_id):
    """function is responsible for displaying a user's profile including the comments that the user has posted."""

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)

    comments = (Comment.query.filter(Comment.user_id == user_id).order_by(
        Comment.timestamp.desc()).limit(20).all())

    return render_template('users/profile-detail.html', user=user, comments=comments)

@app.route('/users/edit', methods=['GET', 'POST'])
def edit_profile():
    """function is responsible for showing the edit form and handling the data that is submitted to backend server. This route also checks to ensure that a user is actually authenticated prior to displaying the edit form."""

    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    current_user = User.query.get(session[CURR_USER_KEY])

    if g.user.id != current_user.id:
        flash('Access unauthorized.', 'danger')
        return redirect('/')

    bcrypt = Bcrypt()

    form = EditUserForm(obj=current_user)

    password = form.password.data

    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password, password):
            flash('Incorrect Password!', 'danger')
            return redirect(f'/users/{current_user.id}')

        else:
            current_user.username = form.username.data
            current_user.email = form.email.data

            if not form.image_url.data:
                current_user.image_url = '/static/images/default-pic.png'
            else:
                current_user.image_url = form.image_url.data

            db.session.add(current_user)
            db.session.commit()
            return redirect(f'/users/{current_user.id}')

    return render_template('users/edit-profile.html', user=current_user, form=form)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    # current_user = User.query.get(session[CURR_USER_KEY])

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")


    # if g.user.id != current_user.id:
    #     flash('Access unauthorized.', 'danger')
    #     return redirect('/')

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    flash('User profile deleted.', 'info')
    return redirect("/signup")


########################################################################################
# COMMENT ROUTES
########################################################################################

@app.route('/pokemon/<pokemon_name>/add-comment', methods=['GET', 'POST'])
def add_pokemon_comment(pokemon_name):
    """
    route will show form for adding a new comment to a pokemon and handle data received from front end and saves to the backend
    
    IF no user is logged in, they will get routed to the signup route.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")

    form = CommentForm()

    pokemon = Pokemon.query.filter(Pokemon.pokemon_name == pokemon_name).one()

    if form.validate_on_submit():
        new_comment = Comment(text=form.comment.data, user_id=g.user.id, pokemon_id=pokemon.id)
        g.user.comments.append(new_comment)
        db.session.add(new_comment)
        db.session.commit()
        flash('Message added successfully!', 'success')
        return redirect(f'/pokemon/{pokemon_name}/detail')

    return render_template('comments/add-comment.html', form=form)


@app.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
def update_comment(comment_id):
    """
    function handles request to show edit form for previous comments and sends updated information to backend db. 
    
    IF user is not authenticated, they will get routed back to signup view.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")

    current_user = User.query.get(session[CURR_USER_KEY])

    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != g.user.id:
        flash('Access unauthorized', 'danger')
        return redirect('/pokedex-generations')

    form = EditCommentForm(data={'comment': comment.text})

    if form.validate_on_submit():

        comment.text = form.comment.data

        db.session.add(comment)
        db.session.commit()

        return redirect(f'/users/{current_user.id}')

    return render_template('users/edit-comment.html', user=current_user, form=form)

@app.route('/comments/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    """function handles request to have comments removed for the user who wrote the message ONLY. Users will not be able to remove comments from other users at this time."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/signup")
    
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect('/pokedex-generations')
    
    db.session.delete(comment)
    db.session.commit()

    return redirect(f'/users/{g.user.id}')


########################################################################################
# POKEMON ROUTES
########################################################################################

@app.route('/pokedex-generations')
def all_pokedexes_view():
    """function is responsible for returning the html view for all the different pokemon generations."""

    all_pokemon = Pokemon.query.all()

    kanto = [p for p in all_pokemon if p.id < 152]

    johto = [p for p in all_pokemon if p.id >= 152 and p.id < 252]

    hoenn = [p for p in all_pokemon if p.id >= 252 and p.id < 387]

    sinnoh = [p for p in all_pokemon if p.id >= 387 and p.id < 494]

    unova = [p for p in all_pokemon if p.id >=494 and p.id < 650]

    kalos = [p for p in all_pokemon if p.id >= 650 and p.id < 722]

    alola = [p for p in all_pokemon if p.id >= 722 and p.id < 810]

    galar = [p for p in all_pokemon if p.id >= 810 and p.id <= 905]    

    return render_template('users/pokedex-generations.html',kanto=kanto, johto=johto, hoenn=hoenn, sinnoh=sinnoh, unova=unova, kalos=kalos, alola=alola, galar=galar)

@app.route('/pokedex-generations/<name>')
def pokedex_view(name):
    """function is responsible for returning the individual view for the pokedex selected."""

    res = requests.get(f'https://pokeapi.co/api/v2/pokedex/{name}')
    dex_name = res.json()['name']
    all_pokemon = res.json()['pokemon_entries']

    return render_template('pokemon/pokedex.html', pokemon=all_pokemon, name=dex_name)


@app.route('/pokemon/<pokemon_name>/detail')
def pokemon_detail_view(pokemon_name):
    """function is responsible for showing the detailed view for a specific pokemon."""

    res = requests.get(
        f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}/')
    
    # contains the response object from the api call for the specific pokemon that a user is viewing.
    pokemon_data = res.json()
    
    # contains the types for the pokemon that was requested from the API.
    types = pokemon_data['types']

    # contains the stat information (list) for a pokemon.
    stats = pokemon_data['stats']

    # contains the pokemon's moves information (all available moves that the pokemon can learn)
    moves = pokemon_data['moves']

    # contains the pokemon's abilities.
    abilities = pokemon_data['abilities']

    # contains base exp for pokemon.
    base_xp = pokemon_data['base_experience']

    # contains the sprite information for pokemon (both shiny and non-shiny)
    front_default = pokemon_data['sprites']['front_default']
    front_shiny = pokemon_data['sprites']['front_shiny']

    # all comments for pokemon user is viewing.
    pokemon = Pokemon.query.filter(Pokemon.pokemon_name == pokemon_name).one()
    

    return render_template('pokemon/pokemon-details.html', name=pokemon_name, pokemon_data=pokemon_data, types=types, comments=pokemon.comments, stats=stats, moves=moves, front_img=front_default, shiny_img=front_shiny, abilities=abilities, base_xp=base_xp)

@app.route('/about')
def about():
    """returns information about the project overall."""

    return render_template('about.html')
