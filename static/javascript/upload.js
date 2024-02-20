document.addEventListener('DOMContentLoaded', function () {
    const selectableImages = document.querySelectorAll('.selectable-image');
    const showMoreImagesButton = document.querySelector('#showMoreImages');
    const moreImagesDiv = document.querySelector('#moreImages');

    showMoreImagesButton.addEventListener('click', function () {
        if (moreImagesDiv.classList.contains('hidden')) {
            moreImagesDiv.classList.remove('hidden');
            showMoreImagesButton.classList.add('underline');
            showMoreImagesButton.textContent = 'Hide Previous Images';
        } else {
            moreImagesDiv.classList.add('hidden');
            showMoreImagesButton.classList.remove('underline');
            showMoreImagesButton.textContent = 'Show Previous Images';
        }
    });

    selectableImages.forEach(function (image) {
        image.addEventListener('click', function () {
            image.classList.toggle('selected');
            if (image.classList.contains('selected')) {
                image.style.border = '4px solid blue';
            } else {
                image.style.border = 'none';
            }
        });
    });
});





/* not used for now
document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.getElementById('imageInput');
    const musicInput = document.getElementById('musicInput');
    const generateVideoButton = document.getElementById('generateVideo');

    generateVideoButton.addEventListener('click', generateVideo);

    function generateVideo() {
        const images = imageInput.files;
        const music = musicInput.files.length > 0 ? musicInput.files[0] : null;

        if (images.length === 0) {
            alert('Please select at least one image.');
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < images.length; i++) {
            formData.append('images', images[i]);
        }
        if (music) {
            formData.append('music', music);
        }

        fetch('/generate_video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Video generated successfully. You can download it from: ' + data.video_path);
            } else {
                alert('Error generating video: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error generating video:', error);
        });
    }
});

*/
