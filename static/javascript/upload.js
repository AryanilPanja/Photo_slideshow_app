document.addEventListener('DOMContentLoaded', function () {

    const fileInput = document.getElementById('imageInput');
    const uploadedImagesDiv = document.querySelector('#uploadedImages');

    fileInput.addEventListener('change', function(event) {

        const files = event.target.files;
        const formData = new FormData();
    
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
    
            const filename = file.name;
            const filetype = file.type;

            formData.append('images[]', file);
            formData.append('filenames[]', filename);
            formData.append('filetypes[]', filetype);
    
            const reader = new FileReader();
    
            reader.onload = function(event) {
                const url = event.target.result;
    
                const img = document.createElement('img');
                img.src = url;
                img.id = `${filename}`;
                img.classList.add('img-thumbnail', 'mr-2', 'mb-2', 'selectable-image');
    
                uploadedImagesDiv.appendChild(img);
    
                img.addEventListener('click', function () {
                    img.classList.toggle('selected');
                    if (img.classList.contains('selected')) {
                        img.style.border = '4px solid blue';
                    } else {
                        img.style.border = '4px solid transparent';
                    }
                });
            };
    
            reader.readAsDataURL(file);
        }

        uploadFiles(formData);

    });

    function uploadFiles(formData) {
  
        fetch(`/upload_images/${username}`, {
          method: 'POST',
          body: formData
        })
        .then(response => {
          if (response.ok) {
            console.log('Image uploaded successfully');
          } else {
            console.error('Failed to upload image');
          }
        })
        .catch(error => {
          console.error('Error uploading image:', error);
        });
    }

    const showMoreImagesButton = document.querySelector('#showMoreImages');
    const moreImagesDiv = document.querySelector('#moreImages');

    fetch(`/get_images/${username}`)  
    .then(response => response.json())
    .then(images => {

        images.forEach(image => {
            const img = document.createElement('img');

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

    const select = document.getElementById('audio');
    const audioPlayer = document.getElementById('audioplayer');
    const audioSrc = document.getElementById('audiosrc');

    /* fetch(`/get_audio_names/${username}`)  // Replace 123 with the actual user ID
    .then(response => response.json())
    .then(audio => {

        // Loop through the images and create <img> elements
        audio.forEach(name => {
            // Create an <img> element

            let option = document.createElement('option');
            option.value = name;
            option.innerHTML = name;

            select.appendChild(option);

        });
    })
    .catch(error => {
        console.error('Error fetching audio:', error);
    }); */

    audioSrc.src = audio_path + 'alex-productions-training-day.mp3';
    audioPlayer.load()

    select.addEventListener('change', function() {

        let value = this.value;

        audioSrc.src = audio_path + value + '.mp3';
        audioPlayer.load()

        console.log(audioSrc.src);

    });

    /* select.addEventListener('change', function() {

        let value = this.value;

        fetch(`/get_audio/${value}`)
        .then(response => response.blob())
        .then(audio => {
    
            let audioURL = URL.createObjectURL(audio);

            const audioPlayer = document.getElementById('audiosrc');
            audioPlayer.src = audioURL;

            console.log(audioURL);

        })
        .catch(error => {
            console.error('Error fetching audio:', error);
        });

    }); */

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

});

function genVid() {

    sessionStorage.setItem('audio', document.getElementById('audio').value)

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
            window.location.href = `/${username}/video`; 
        } else {
            console.error('Error saving selected images');
        }
    })
    .catch(error => {
        console.error('Error saving selected images:', error);
    });

}
