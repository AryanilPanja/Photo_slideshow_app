document.addEventListener('DOMContentLoaded', function () {

    const video = document.getElementById('videoPlayer');
    const playPauseBtn = document.getElementById('playPauseBtn');
    const rewindBtn = document.getElementById('rewindBtn');
    const fastForwardBtn = document.getElementById('fastForwardBtn');
    const slider = document.getElementById('imageLengthRange');

    var durations = [];
    var curr_image = 0;
    var transition = 'none';
    var audio = sessionStorage.getItem('audio');
    var res = '720';
    

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

    fetch(`/get_selected_images/${username}`) 
    .then(response => response.json())
    .then(images => {
        const image_container = document.getElementById('images');
        var i = 0;

        images.forEach(image => {
            const img = document.createElement('img');

            const url = `data:${image.image_format};base64,${image.image_data}`;
            console.log(image.image_format);
            img.src = url;

            image_container.appendChild(img);

            durations.push(5);
            let image_id = i;

            img.addEventListener('click', () => {
                const allImages = image_container.querySelectorAll('img');
                allImages.forEach(otherImg => {
                    otherImg.classList.remove('selected');
                });
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

        previewVid(durations, transition, audio, res);

    })
    .catch(error => {
        console.error('Error fetching images:', error);
    });

    

    slider.addEventListener('change', function() {

        durations[curr_image] = parseInt(slider.value);
        previewVid(durations, transition, audio, res);

    });

    const transition_icons = document.getElementsByClassName('transition-icons')[0];
    const transition_buttons = transition_icons.querySelectorAll('*');

    transition_buttons.forEach(button => {
        button.addEventListener('click', function() {
            transition = button.id;
            previewVid(durations, transition, audio, res);
        });
    });


    const resolutionGrp = document.getElementsByClassName('btn-group')[0];
    const resolutionButtons = resolutionGrp.querySelectorAll('*');

    resolutionButtons.forEach(button => {
        button.addEventListener('click', function() {
            resolutionButtons.forEach(btn => {
                btn.classList.remove('btn-resolution-selected');
            });

            button.classList.add('btn-resolution-selected');
            res = button.id;
            previewVid(durations, transition, audio, res);
        });
    });


    function previewVid(durations, transition, audio, res) {
        const jsonData = {

            'durations' : durations,
            'transition' : transition,
            'audio' : audio,
            'resolution' : res

        };

        fetch(`/generate_video/${username}`, {
            method: 'POST',
            body: JSON.stringify(jsonData),
            headers:{'content-type': 'application/json'}
        })
        .then(result => {
            console.log('created');
            document.getElementById('videoPlayer').src = `${video_path}`;
            playPauseBtn.innerHTML = '<span class="bi bi-play-circle-fill"></span>';
        })
        .catch(error => {
            console.error('Error generating video slideshow:', error);
        });
    }

});

window.addEventListener('beforeunload', function() {

    fetch(`/delete_video/${username}`, {
        method: 'POST',
    })
    .then(response => {
        if (!response.ok) {
            console.error('Failed to delete file:', response.statusText);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
