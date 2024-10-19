document.addEventListener('DOMContentLoaded', () => {
    // Function to toggle the responsive class on the nav-menu
    function toggleMenu() {
        const navMenu = document.getElementById('navMenu');
        if (navMenu) {
            navMenu.classList.toggle('responsive');
        }
    }

    // Event listener for the entire menu button, not just the icon
    const menuButton = document.querySelector('.nav-menu-btn');
    if (menuButton) {
        menuButton.addEventListener('click', toggleMenu);
    }

    // Initialize Slick Carousel for the popular movies
    $('#popular-this-week-carousel').slick({
        infinite: true,
        slidesToShow: 5,
        slidesToScroll: 1,
        arrows: true,
        dots: false,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 1,
                    dots: false
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1,
                    dots: false
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    dots: false
                }
            }
        ]
    });

    // Initialize Slick Carousel for the top-rated movies
    $('#top-rated-movies-carousel').slick({
        infinite: true,
        slidesToShow: 5,
        slidesToScroll: 1,
        arrows: true,
        dots: false,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 1,
                    dots: false
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1,
                    dots: false
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    dots: false
                }
            }
        ]
    });

    // Initialize Slick Carousel for the movie cast
    $('#cast-carousel').slick({
        infinite: true,
        slidesToShow: 4,
        slidesToScroll: 1,
        arrows: true,
        dots: true,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1,
                    dots: true
                }
            },
            {
                breakpoint: 1536,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 1,
                    dots: true
                }
            }
        ]
    });

    // Hide alerts after 5 seconds
    setTimeout(() => {
        $('#alert').fadeOut(1000);
    }, 5000);

    // Function to update button color based on action and status
    function updateButtonColor(button, action, isActive) {
        let color;
        switch (action) {
            case 'watch':
                color = isActive ? 'forestgreen' : 'gray';
                break;
            case 'like':
                color = isActive ? 'deeppink' : 'gray';
                break;
            case 'watchlist':
                color = isActive ? 'cornflowerblue' : 'gray';
                break;
            default:
                color = 'gray';
        }
        button.css('background-color', color);
    }

    // Function to fetch and update button states
    function initializeButtonStates() {
        $('.movie-action-btn').each(function() {
            const movieId = $(this).data('movie-id');

            fetch(`/api/movie/status?movie_id=${movieId}`)
                .then(response => response.json())
                .then(response => {
                    if (response.error) {
                        console.error('Error fetching movie status:', response.error);
                    } else {
                        // Update all buttons for the movie
                        const buttonActions = ['like', 'watch', 'watchlist'];
                        buttonActions.forEach((action, index) => {
                            const button = $(`.movie-action-btn[data-movie-id='${movieId}'][data-action='${action}']`);
                            if (button.length) {
                                updateButtonColor(button, action, response[index] === 1);
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Error fetching movie status:', error);
                    alert('An error occurred. Please try again.');
                });
        });
    }

    // Initialize button states on page load
    initializeButtonStates();

    // Event listener for movie action buttons
    $(document).on('click', '.movie-action-btn', function() {
        const movieId = $(this).data('movie-id');
        const action = $(this).data('action');
        const button = $(this);
        const currentColor = button.css('background-color');

        fetch('/movie/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ movie_id: movieId, action: action })
        })
        .then(response => response.json())
        .then(response => {
            if (response.success) {
                // Determine if the color should toggle
                const isActive = currentColor === 'rgb(128, 128, 128)';
                updateButtonColor(button, action, isActive);
            } else {
                console.error('Error performing movie action:', response);
            }
        })
        .catch(error => {
            console.error('Error performing movie action:', error);
            alert('An error occurred. Please try again.');
        });
    });
});
