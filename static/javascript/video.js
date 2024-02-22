document.addEventListener('DOMContentLoaded', function () {

    const video = document.getElementById('videoPlayer');
    const playPauseBtn = document.getElementById('playPauseBtn');
    const rewindBtn = document.getElementById('rewindBtn');
    const fastForwardBtn = document.getElementById('fastForwardBtn');

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
            });

        });
    })
    .catch(error => {
        console.error('Error fetching images:', error);
    });

});