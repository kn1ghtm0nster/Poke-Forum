
# Poke-Forum!

This tool uses the [PokeAPI](https://pokeapi.co/) to primarily display information about each generation of Pokmemon.

__NOTE:__ If you want to view the application before reading all the tech babble, then feel free to click on the link below!


* Live Application Link: [Poke-Forum](https://poke-forum.herokuapp.com/)

## Overview:

The Poke-Forum website was designed with an overall goal of making a free space for pokemon game fans to discuss their tips, tricks, and locations for catching and building a good pokemon roster. 

Each generation of pokemon have been broken down in the main view for registered users and they are free to explore their favorite entries and view some base stats along with the ability to leave comments and view other user profiles to see what else is being posted under another user's profile.

While the application is not very detailed now, there are __plenty__ of upcoming updates that will be rolled out and can be further [below](#upcoming-features).

## Features:

__NOTE__: More features are currently being worked on/developed and will be rolled out in new versions of the website soon.

Current features of the website are as follows:

* User account creation.
    * Passwords for user accounts are being hashed and salted using `Bcrypt`
* Pokemon view by generation.
* Viewing Pokemon individually.
* Ability to leave a comment on a specific pokemon.
    * Comments under individual Pokemon view will contain link to the user profile for comment and the date of said comment.
* Individual user profile views.
    * Viewing other user profiles to see which other pokemon they have commented under and go to that Pokemon's individual page.
* Editing comments 
    * Only for users that made that post. In other words only authorized users can update their own comments.
* Deleting comments
    * Only authorized users can delete their own comments
* Editing Profile  
    * Just like the comments, only authorized users will be allowed to edit their profile information.
    * __NOTE__: Users will need to enter their password to save changes in database. If they enter a wrong password, user will be routed back to their profile page.
* Deleting profile
    * Only authorized users can delete their own comments
* Basic Logging in/out functionality
    * Users can log in and out freely and their client will store their login information during the user's session to browse the other website components.

## Feature Details:

* User Accounts:
    * For user accounts, I used `Bcrypt` to generate user accounts as this library is standard for hashing and salting user passwords.
    * `Bcrypt` is also really easy to work with and was simple to add to the project by just importing the module to main application file.
    * Last reason that this module was used is to ensure that users are entering their appropriate credentials when editing their profile or logging in to the application.
    * User accounts also have the ability to edit and delete their own profile.
    * While editing, users have the ability of updating their username, email, or image that is displayed in their profile view. Once ready, users need only enter their password to save the changes.
    * The reason passwords are required is so that no one will be able to update another user's profile outside the application through a third party.

* Pokemon Generations View:
    * Main view for application which uses `Bootstrap 5`'s accordion class to display each pokemon by national `id` followed by the Pokemon `name`.
    * The application is storing the national Pokedex entries on the database and this is populated by sending a request to the `PokeAPI` endpoint `https://pokeapi.co/api/v2/pokedex/national`.
    * __NOTE__: This call is __NOT__ being done in any route but instead is only run whenever the seed file is run through the terminal and therefor only storing the pokemon name and the associated `national id`.
    * The reason that the server is storing the pokemon name and id on the database is to prevent the client DOM from making this call and overloading the API endpoint which can lead to getting IP banned.
    * Last part of this main view for each Pokemon generation is the sprite image that is seen next to the pokemon name. This is a call that is being done through the client's DOM via `Axios.` Since there are over 800 pokemon, the sprites will take time to populate. Developer (me) will be considering moving this information to the backend Pokemon table in the future meaning that any feedback is appreciated!

* Commenting:
    * Users that have registered with the application will be able to leave comments under a specific Pokemon that they are viewing in the website.
    * Additionally, users will be able to remove comments in their profile view as well as edit whichever comment they select.
    * Comments are editable and removable __ONLY__ under a logged in user's profile to prevent clutter in the individual pokemon view.
    * Comments are traversable from pokemon to user and vice versa meaning that you can view a user's profile by clicking their username and viewing a specific Pokemon's profile page by clicking the button that appears under the comment for a user's comment history.

* Deleting:
    * Users that are registered and logged in have the ability to remove specific comments and or their user profiles which will trigger a `cascade` effect on the relationships defined. In short, if a comment is removed, it's gone from the database and if a user profile is removed, the comments for that user will also be removed. 
    * The reason that this is done is due to the current schema not allowing the `comments` table to have nullable fields 

* Logging in/out:
    * It's quite simple, you log in and out. Buttons in the navbar will update your options accordingly.
    * User's that log in will have their user information stored in `Flask`'s `global` object which will be added on the client `session`.

## User Flow:

1. Register/Sign Up.
    * Or login if user already has account.
2. Select desired Pokemon generation from the pokemon-generations view.
3. Select desired Pokemon to view more details on that specific pokemon.
4. Add comment.
5. View comments under different user profiles.
6. View your own profile information.
    * Update profile or comment information.
    * Delete profile or comment.
7. Logout

## Technology Stack:

* Frontend
    * `HTML` / `Jinja`
    * `CSS` / `Bootstrap 5`
    * `Javascript` / `Axios` / `JQuery`

* Backend
    * `SQL` / `PostgreSQL`
    * `Python` / `Flask` / `SQLAlchemy` / `WTForms`

* API
    * [`PokeAPI`](https://pokeapi.co/)

## Upcoming Features:

* V-2.2 (Date: EST Aug 2022)
    * Password Reset for User Accounts.
    * New section for Release Notes.


## Misc

None of this project would have been possible without the great teachings from the folk over at Springboard so massive thank you for giving me the tools to build my first ever live application from scratch.

In addition and as stated above, a GIGANTIC shoutout to the developers that created the PokeAPI for all fans to consume and enjoy. If you didn't see the link to their docs, you can click [here](#poke-forum) to go back to the top.

Lastly, thank you to anyone who stops by and reads all of this. If you would like to report an issue or get to know more about this project over all feel free to reach out! Social information can be found [here](https://github.com/kn1ghtm0nster)