const video = document.getElementById('videoPlayer');
const playPauseBtn = document.getElementById('playPauseBtn');
const rewindBtn = document.getElementById('rewindBtn');
const fastForwardBtn = document.getElementById('fastForwardBtn');
const imageLengthRange = document.getElementById('imageLengthRange');
const placeholderImages = document.querySelectorAll('#placeholderImages img');

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

placeholderImages.forEach(img => {
    img.addEventListener('click', () => {
        placeholderImages.forEach(otherImg => {
            otherImg.classList.remove('selected');
        });
        img.classList.add('selected');
    });
});