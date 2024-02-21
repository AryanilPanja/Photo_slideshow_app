document.addEventListener('DOMContentLoaded', function () {

    fetch(`/get_images/${username}`)  // Replace 123 with the actual user ID
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
            img.className = 'card-img-top';

            const outer_div = document.createElement('div');
            const inner_div = document.createElement('div');

            outer_div.classList.add('col', 'mb-4');
            inner_div.className = 'card';

            inner_div.appendChild(img);
            outer_div.appendChild(inner_div);
            image_container.appendChild(outer_div);
        });
    })
    .catch(error => {
        console.error('Error fetching images:', error);
    });

});