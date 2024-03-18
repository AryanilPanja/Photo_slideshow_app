document.addEventListener('DOMContentLoaded', function () {

    const video = document.getElementById('videoPlayer');
    const playPauseBtn = document.getElementById('playPauseBtn');
    const rewindBtn = document.getElementById('rewindBtn');
    const fastForwardBtn = document.getElementById('fastForwardBtn');
    const slider = document.getElementById('imageLengthRange');
    
    const finish = document.getElementById

    var durations = [];
    var curr_image = 0;
    var transition = 'none'
    var audio = sessionStorage.getItem('audio');
    

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
        var i = 0;

        // Loop through the images and create <img> elements
        images.forEach(image => {
            // Create an <img> element
            const img = document.createElement('img');

            // Set the src attribute to a data URL representing the image data
            const url = `data:${image.image_format};base64,${image.image_data}`;
            console.log(image.image_format);
            img.src = url;

            image_container.appendChild(img);

            durations.push(5);
            let image_id = i;

            img.addEventListener('click', () => {
                // Remove 'selected' class from all images
                const allImages = image_container.querySelectorAll('img');
                allImages.forEach(otherImg => {
                    otherImg.classList.remove('selected');
                });
                // Add 'selected' class to the clicked image
                img.classList.add('selected');
                curr_image = image_id;
                console.log(image_id);
                console.log(durations[image_id]);
                slider.value = String(durations[image_id]);
            });

            i++;

        });

        console.log(durations);

        firstimage = image_container.querySelector('img');
        firstimage.classList.add('selected');

        previewVid(durations, transition, audio);

    })
    .catch(error => {
        console.error('Error fetching images:', error);
    });

    

    slider.addEventListener('change', function() {

        durations[curr_image] = parseInt(slider.value);
        previewVid(durations, transition, audio);

    });

    const transition_icons = document.getElementsByClassName('transition-icons')[0];
    const transition_buttons = transition_icons.querySelectorAll('*');

    transition_buttons.forEach(button => {
        button.addEventListener('click', function() {
            transition = button.id;
            previewVid(durations, transition, audio);
        });
    });


    function previewVid(durations, transition, audio) {
        // Send selected images to Flask server to generate video
        const jsonData = {

            'durations' : durations,
            'transition' : transition,
            'audio' : audio

        };

        fetch(`/generate_video/${username}`, {
            method: 'POST',
            body: JSON.stringify(jsonData),
            headers:{'content-type': 'application/json'}
        })
        .then(result => {
            // Handle the result from the Flask server (e.g., display a link to the generated video)
            console.log('created');
                // Assuming you have a video element with id 'videoPlayer'
            document.getElementById('videoPlayer').src = `${video_path}`;
        })
        .catch(error => {
            console.error('Error generating video slideshow:', error);
        });
    }

});
