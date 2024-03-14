document.addEventListener('DOMContentLoaded', function () {

    const video = document.getElementById('videoPlayer');
    const playPauseBtn = document.getElementById('playPauseBtn');
    const rewindBtn = document.getElementById('rewindBtn');
    const fastForwardBtn = document.getElementById('fastForwardBtn');

    let durations = [];
    let curr_image = 0;
    let transition = /* transition */

    playPauseBtn.addEventListener('click', function() {
        if (video.paused) {
            video.play();
            playPauseBtn.innerHTML = '<span class="bi bi-pause-circle-fill"></span>';
        } else {
            video.pause();
            playPauseBtn.innerHTML = '<span class="bi bi-play-circle-fill"></span>';
        }
    });

    rewindBtn.addEventListener('click', function() {
        video.currentTime -= 5; 
    });

    fastForwardBtn.addEventListener('click', function() {
        video.currentTime += 5; 
    });

    fetch(`/get_selected_images/${username}`)  // Replace 123 with the actual user ID
    .then(response => response.json())
    .then(images => {
        // Get the container element to hold the images
        const image_container = document.getElementById('images');
        let i = 0;

        // Loop through the images and create <img> elements
        images.forEach(image => {
            // Create an <img> element
            const img = document.createElement('img');

            // Set the src attribute to a data URL representing the image data
            const url = `data:${image.image_format};base64,${image.image_data}`;
            console.log(image.image_format);
            img.src = url;

            image_container.appendChild(img);

            img.addEventListener('click', () => {
                // Remove 'selected' class from all images
                const allImages = image_container.querySelectorAll('img');
                allImages.forEach(otherImg => {
                    otherImg.classList.remove('selected');
                });
                // Add 'selected' class to the clicked image
                img.classList.add('selected');
                curr_image = i;
            });

            durations.push(5);
            i++;

        });

        firstimage = image_container.querySelector('img');
        firstimage.classList.add('selected');

        previewVid(durations, transition);

    })
    .catch(error => {
        console.error('Error fetching images:', error);
    });

    const slider = document.getElementById('imageLengthRange');

    slider.addEventListener('change', function() {

        durations[curr_image] = slider.value;
        previewVid(durations, transition);

    });

    const transition_buttons = document.getElementsByClassName('transition-icons').querySelectorAll('*');

    transition_buttons.forEach(button => {
        button.addEventListener('click', function() {
            transition = button.id;
            previewVid(durations, transition);
        });
    });


    function previewVid(durations, transition, user) {
        // Send selected images to Flask server to generate video
        const formData = new FormData();
        formData['durations[]'] = durations;
        formData['transition'] = transition;

        fetch(`/generate_video/${user}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            // Handle the result from the Flask server (e.g., display a link to the generated video)
            console.log(result.message);
            if (result.video_path) {
                // Assuming you have a video element with id 'videoPlayer'
                document.getElementById('videoPlayer').src = result.video_path;
            }
        })
        .catch(error => {
            console.error('Error generating video slideshow:', error);
        });
    }

});
