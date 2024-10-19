# General application setup and configuration
import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Ensure the instance folder exists for storing the SQLite database
if not os.path.exists('instance'):
    os.makedirs('instance')

# Application configuration for the database and secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.getcwd()), 'instance/site.db')
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key

# Initialize SQLAlchemy for database operations and Bcrypt for password hashing
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Association table for the followers relationship (many-to-many between users)
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# Model for the Movie entity with fields for movie ID, title, and poster path
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    poster_path = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Movie('{self.title}', '{self.poster_path}')"

# Model for user interactions with movies (watched, liked, and added to watchlist)
class UserMovieInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    watched = db.Column(db.Boolean, default=False)
    liked = db.Column(db.Boolean, default=False)
    watchlist = db.Column(db.Boolean, default=False)

    # Relationship to link interaction with the Movie entity
    movie = db.relationship('Movie', backref='interactions', lazy=True)

    def __repr__(self):
        return f"UserMovieInteraction(User ID: {self.user_id}, Movie ID: {self.movie_id}, Watched: {self.watched}, Liked: {self.liked}, Watchlist: {self.watchlist})"

# Model for the User entity with fields for ID, username, email, and password
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # Relationships for user interactions with movies and following other users
    interactions = db.relationship('UserMovieInteraction', backref='user', lazy=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # Method to check if the user is following another user
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    # Method to check if the user is followed by another user
    def is_followed_by(self, user):
        return self.followers.filter(followers.c.follower_id == user.id).count() > 0

    # Method to follow another user
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            db.session.commit()

    # Method to unfollow a user
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            db.session.commit()

# Inject the current username into the context of all templates for use in navigation, etc.
@app.context_processor
def inject_username():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            username = user.username
    return dict(username=username)

# Route to show users that the current user is following
@app.route('/user/<int:user_id>/following')
def user_following(user_id):
    user = User.query.get_or_404(user_id)
    following_users = user.followed.all()  # Fetch all users that the current user is following
    return render_template('user_list.html', list_type='following', users=following_users)

# Route to show users that are following the current user
@app.route('/user/<int:user_id>/followers')
def user_followers(user_id):
    user = User.query.get_or_404(user_id)
    follower_users = user.followers.all()  # Fetch all users following the current user
    return render_template('user_list.html', list_type='followers', users=follower_users)

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for displaying the user's watchlist
@app.route('/watchlist')
def watchlist():
    # Displays the user's watchlist if logged in.
    if 'user_id' not in session:
        return render_template('login_prompt.html', page='watchlist')

    user_id = session['user_id']
    user = User.query.get(user_id)

    # Retrieves user's watchlisted movies.
    watchlist_interactions = UserMovieInteraction.query.filter_by(user_id=user_id, watchlist=True).all()

    watchlist_movies = []
    api_key = '16fc4b030758d787ba68479cc1aa9e1c'

    # Fetches movie details from external API.
    for interaction in watchlist_interactions:
        movie_id = interaction.movie_id
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            movie_info = {
                'title': data.get('title', 'Unknown Title'),
                'poster_path': data.get('poster_path', None)
            }
            watchlist_movies.append(movie_info)

    return render_template('watchlist.html', watchlist_movies=watchlist_movies)


# Route for displaying the user's friends and their movie interactions
@app.route('/friends')
def friends():
    # Displays the user's friends list and their movie interactions.
    if 'user_id' not in session:
        return render_template('login_prompt.html', page='friends')
    
    current_user = User.query.get(session['user_id'])
    if not current_user:
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('home'))

    friends = current_user.followed.all()
    movie_counts = {}

    # Aggregates movie interaction data from friends.
    for friend in friends:
        interactions = UserMovieInteraction.query.filter_by(user_id=friend.id).all()

        for interaction in interactions:
            if interaction:
                movie_id = str(interaction.movie_id)
                if movie_id in movie_counts:
                    movie_counts[movie_id] += 1
                else:
                    movie_counts[movie_id] = 1

    # Fetches the top 10 most common movies among friends.
    top_movies = sorted(movie_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    movie_details = []
    api_key = '16fc4b030758d787ba68479cc1aa9e1c'

    # Fetches detailed information for the top movies.
    for movie_id, _ in top_movies:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
        response = requests.get(url)
        data = response.json()

        movie_info = {
            'id': movie_id,
            'title': data.get('title', 'Unknown Title'),
            'poster_path': data.get('poster_path', 'default_poster_path.jpg')
        }
        movie_details.append(movie_info)

    return render_template('friends.html', movies=movie_details)


# Route for discovering trending and top-rated movies
@app.route('/discover')
def movies():
    # Displays trending and top-rated movies.
    api_key = '16fc4b030758d787ba68479cc1aa9e1c'
    
    trending_url = f'https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}'
    top_rated_url = f'https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&language=en-US&page=1'

    try:
        trending_response = requests.get(trending_url)
        top_rated_response = requests.get(top_rated_url)
        trending_response.raise_for_status()
        top_rated_response.raise_for_status()
        
        trending_movies = trending_response.json().get('results', [])[:10]
        top_rated_movies = top_rated_response.json().get('results', [])[:10]

        user_interactions = {}
        if 'user_id' in session:
            user_id = session['user_id']
            interactions = UserMovieInteraction.query.filter_by(user_id=user_id).all()
            user_interactions = {interaction.movie_id: {'watched': interaction.watched, 'liked': interaction.liked, 'watchlist': interaction.watchlist} for interaction in interactions}

    except requests.RequestException as e:
        flash(f'An error occurred while fetching movies: {e}', 'danger')
        trending_movies = []
        top_rated_movies = []
        user_interactions = {}

    return render_template('discover.html', trending_movies=trending_movies, top_rated_movies=top_rated_movies, user_interactions=user_interactions)


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Handles the user registration process
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or Email already exists!', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handles the user login process
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')

    return render_template('login.html')


# Route for user logout
@app.route('/logout')
def logout():
    # Logs the user out and clears the session
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# Route for listing all users
@app.route('/list_users')
def list_users():
    # Displays a list of all registered users
    users = User.query.all()
    usernames = [user.username for user in users]
    return render_template('list_users.html', usernames=usernames)


# Route for displaying a user's profile based on username
@app.route('/profile/<username>')
def profile_by_username(username):
    # Displays the profile of a specific user by their username
    user = User.query.filter_by(username=username).first()

    if user:
        following_count = user.followed.count()
        followers_count = user.followers.count()

        recent_activity_movies = UserMovieInteraction.query.filter_by(user_id=user.id).order_by(UserMovieInteraction.id.desc()).limit(10).all()

        api_key = '16fc4b030758d787ba68479cc1aa9e1c'
        movie_details = []

        # Fetches recent movie interactions
        for interaction in recent_activity_movies:
            movie_id = interaction.movie_id
            url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                movie_info = {
                    'id': movie_id,
                    'title': data.get('title', 'Unknown Title'),
                    'poster_path': data.get('poster_path', 'default_poster_path.jpg'),
                    'watched': interaction.watched,
                    'liked': interaction.liked,
                    'watchlist': interaction.watchlist
                }
                movie_details.append(movie_info)

        # Fetch the current user if logged in for comparison
        current_user = User.query.get(session.get('user_id')) if 'user_id' in session else None

        return render_template(
            'profile.html', 
            user=user, 
            following_count=following_count, 
            followers_count=followers_count,
            recent_activity_movies=movie_details,
            current_user=current_user
        )
    else:
        flash(f'User {username} not found.', 'danger')
        return redirect(url_for('home'))


# Function to get movie details from the TMDB API
def get_movie_details(movie_name):
    # Fetches movie details from the TMDB API using the movie name
    api_key = '16fc4b030758d787ba68479cc1aa9e1c'
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
    response = requests.get(search_url)
    data = response.json()

    if data['results']:
        movie_id = data['results'][0]['id']
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=credits"
        details_response = requests.get(details_url)
        return details_response.json()

    return None


# Route to display movie details
@app.route('/discover/<string:movie_name>')
def movie_details(movie_name):
    # Displays detailed information about a specific movie
    if not movie_name:
        flash('Movie name is required!', 'danger')
        return redirect(url_for('home'))
    
    movie_data = get_movie_details(movie_name)
    
    if movie_data:
        return render_template('movie_details.html', movie=movie_data)
    else:
        flash('Movie not found!', 'danger')
        return redirect(url_for('home'))


# API endpoint to fetch the status of a movie for the current user
@app.route('/api/movie/status')
def movie_status():
    # Checks if the user is logged in and returns movie interaction status
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    movie_id = request.args.get('movie_id')
    if not movie_id:
        return jsonify({'error': 'Invalid request'}), 400

    user_id = session['user_id']
    interaction = UserMovieInteraction.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if interaction:
        response_data = [int(interaction.liked), int(interaction.watched), int(interaction.watchlist)]
    else:
        response_data = [0, 0, 0]
    return jsonify(response_data)


# Route to handle movie actions like watch, like, and add to watchlist
@app.route('/movie/action', methods=['POST'])
def movie_action():
    # Updates the interaction (watched, liked, watchlist) of a user for a movie
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = session['user_id']
    data = request.get_json()
    movie_id = data.get('movie_id')
    action = data.get('action')

    if not movie_id or not action:
        return jsonify({'error': 'Invalid request'}), 400

    interaction = UserMovieInteraction.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if not interaction:
        interaction = UserMovieInteraction(user_id=user_id, movie_id=movie_id)

    if action == 'watch':
        interaction.watched = not interaction.watched
    elif action == 'like':
        interaction.liked = not interaction.liked
    elif action == 'watchlist':
        interaction.watchlist = not interaction.watchlist
    else:
        return jsonify({'error': 'Invalid action'}), 400

    db.session.add(interaction)
    db.session.commit()

    return jsonify({'success': True})


# Route for following a user
@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    # Allows the current user to follow another user
    if 'user_id' not in session:
        flash('Please log in to follow users.', 'danger')
        return redirect(url_for('login'))

    user_to_follow = User.query.filter_by(username=username).first()
    if user_to_follow is None:
        flash(f'User {username} not found.', 'danger')
        return redirect(url_for('home'))

    current_user = User.query.get(session['user_id'])
    if current_user is None:
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('home'))

    if current_user.is_following(user_to_follow):
        flash(f'You are already following {username}.', 'info')
    else:
        current_user.follow(user_to_follow)
        db.session.commit()
        flash(f'You are now following {username}!', 'success')

    return redirect(url_for('profile_by_username', username=username))


# Route for unfollowing a user
@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    # Allows the current user to unfollow another user
    if 'user_id' not in session:
        flash('Please log in to unfollow users.', 'danger')
        return redirect(url_for('login'))

    user_to_unfollow = User.query.filter_by(username=username).first()
    if user_to_unfollow is None:
        flash(f'User {username} not found.', 'danger')
        return redirect(url_for('home'))

    current_user = User.query.get(session['user_id'])
    if current_user is None:
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('home'))

    if current_user.is_following(user_to_unfollow):
        current_user.unfollow(user_to_unfollow)
        db.session.commit()
        flash(f'You have unfollowed {username}.', 'info')
    else:
        flash(f'You are not following {username}.', 'info')

    return redirect(url_for('profile_by_username', username=username))


# Route for searching movies
@app.route('/search')
def search():
    # Searches for movies using the TMDB API
    query = request.args.get('query')
    if not query:
        flash('Please enter a movie name to search.', 'danger')
        return redirect(url_for('home'))

    api_key = '16fc4b030758d787ba68479cc1aa9e1c'  # Replace with your actual TMDB API key
    search_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}'

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        movies = response.json().get('results', [])
    except requests.RequestException as e:
        flash(f'An error occurred while searching for movies: {e}', 'danger')
        movies = []

    return render_template('search_results.html', movies=movies, query=query)


# Route for searching friends
@app.route('/search_friends', methods=['GET', 'POST'])
def search_friends():
    # Searches for users based on a query (username)
    query = request.args.get('query', '')  # Get the search query from URL parameters
    if not query:
        flash('Please enter a username to search.', 'danger')
        return redirect(url_for('friends'))

    # Perform the search query to find matching users
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()

    return render_template('user_list.html', list_type='search_results', users=users)


if __name__ == '__main__':
    # Runs the Flask application
    app.run(debug=True)
