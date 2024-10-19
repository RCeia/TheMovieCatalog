# YOUR PROJECT TITLE
#### Video Demo:  <URL HERE>
#### Description:
A Movies app that let's you organize the movies that you've seen and the movies you want to see. You can also check all your friends activity and see the movies they've been seeing and check their recomendations

Feature: User Following

This feature displays a list of users that the currently logged-in user is following. It retrieves the followed users based on the user's ID and presents the data in the user_list.html template, categorizing the list as 'following'.

Feature: User Followers

This feature displays a list of users who are following the currently logged-in user. It retrieves the followers based on the user's ID and presents the data in the user_list.html template, categorizing the list as 'followers'.

Feature: Watchlist

This feature allows a logged-in user to view their personal movie watchlist. If the user is not logged in, they are prompted to log in. The watchlist includes movies that the user has marked, fetching movie details via an external API and displaying them in the watchlist.html template.

Feature: Friends' Movie Interactions

This feature shows the logged-in user's list of friends and their movie interactions. It aggregates data on the most common movies watched by friends, retrieves movie details from an external API, and displays the top 10 in the friends.html template.

Feature: Movie Discovery

This feature allows users to discover trending and top-rated movies. It fetches data from an external API and displays the top 10 trending and top-rated movies in the discover.html template. Logged-in users will also see their personal interactions with these movies (watched, liked, or added to their watchlist).

Feature: User Registration

This feature handles the registration of new users. It collects the user's details (username, email, password), validates the input, and checks for existing accounts. Upon successful registration, the user is redirected to log in and can start using the site.

Feature: User Login

This feature manages user authentication. It verifies the user's email and password against the stored credentials. On successful login, the user is redirected to the homepage, while unsuccessful attempts trigger an error message.

Feature: User Logout

This feature logs the user out by clearing their session data and redirects them to the homepage with a confirmation message.

Feature: User List

This feature displays a list of all registered users. It fetches the usernames from the database and renders them in the list_users.html template.

Feature: User Profile

This feature shows the profile of a specific user, identified by their username. It includes information like the user's followers, following count, and their recent movie interactions. The movie details are fetched from an external API, and the profile is displayed in the profile.html template. If the current user is logged in, they can compare their status with the viewed profile.

Feature: Movie Details Fetching
REDE
This feature allows the application to fetch detailed movie information from the TMDB API using a movie name. It retrieves data like the movie's ID and credits, which are used to provide detailed information to users.

Feature: Movie Details Display

This feature enables users to search for and view detailed information about a specific movie by its name. It leverages the movie data fetched from the TMDB API and displays it in the movie_details.html template. If the movie is not found, an error message is shown.

Feature: Movie Status API

This feature provides an API endpoint that checks a logged-in user's interaction status with a particular movie (liked, watched, or added to the watchlist). The API returns a JSON response indicating the user's current interaction status.

Feature: Movie Actions (Watch, Like, Watchlist)

This feature allows logged-in users to interact with movies by marking them as watched, liked, or adding them to their watchlist. It updates the user's interaction status for a movie and returns a success response in JSON format.

Feature: Follow User

This feature lets a logged-in user follow another user. Upon attempting to follow someone, the application checks if the user exists and whether the current user is already following them. If not, the current user starts following the target user, and a success message is displayed.

Feature: Unfollow User

This feature enables the current logged-in user to unfollow another user. It checks if the target user exists and whether the current user is following them. If the user is successfully unfollowed, a notification is shown.

Feature: Movie Search

This feature allows users to search for movies by querying the TMDB API. Users can input a movie name, and the results are displayed in a search results page. If an error occurs or no query is provided, appropriate messages are shown.

Feature: Search Friends

This feature allows users to search for other users by their username. The search query is passed through URL parameters, and the results are displayed in a user list. If no query is provided, the user is redirected back to the friends page.
