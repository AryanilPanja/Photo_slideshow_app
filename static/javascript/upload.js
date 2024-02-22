document.addEventListener('DOMContentLoaded', function () {

    const showMoreImagesButton = document.querySelector('#showMoreImages');
    const moreImagesDiv = document.querySelector('#moreImages');

    fetch(`/get_images/${username}`)  // Replace 123 with the actual user ID
    .then(response => response.json())
    .then(images => {

        // Loop through the images and create <img> elements
        images.forEach(image => {
            // Create an <img> element
            const img = document.createElement('img');

            // Set the src attribute to a data URL representing the image data
            const url = `data:${image.image_format};base64,${image.image_data}`;
            console.log(image.image_format);
            img.src = url;
            img.id = `${image.image_name}`;
            img.classList.add('img-thumbnail', 'mr-2', 'mb-2', 'selectable-image');

            moreImagesDiv.appendChild(img);

            img.addEventListener('click', function () {
                img.classList.toggle('selected');
                if (img.classList.contains('selected')) {
                    img.style.border = '4px solid blue';
                } else {
                    img.style.border = '4px solid transparent';
                }
            });
        });
    })
    .catch(error => {
        console.error('Error fetching images:', error);
    });

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

    const selectableImages = document.querySelectorAll('.selectable-image');

    selectableImages.forEach(function (image) {
        image.addEventListener('click', function () {
            image.classList.toggle('selected');
            if (image.classList.contains('selected')) {
                image.style.border = '4px solid blue';
            } else {
                image.style.border = '4px solid transparent';
            }
        });
    });

});

function genVid() {

    const selectedImages = document.querySelectorAll('.selected');
    let selected_images = [];

    selectedImages.forEach(function (image) {

        selected_images.push(image.id);

    });

    console.log(selected_images)

    const imgData = JSON.stringify(selected_images);

    fetch(`/save_selected_images`, {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: imgData

    })
    .then(response => {
        if (response.ok) {
            // Redirect to another page
            window.location.href = `/${username}/video`; // Replace with the URL of the other page
        } else {
            console.error('Error saving selected images');
        }
    })
    .catch(error => {
        console.error('Error saving selected images:', error);
    });

}





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
