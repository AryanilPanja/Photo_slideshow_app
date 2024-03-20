document.addEventListener('DOMContentLoaded', function () {

    fetch(`/get_images/${username}`)  
    .then(response => response.json())
    .then(images => {
        const image_container = document.getElementById('images');

        images.forEach(image => {
            const img = document.createElement('img');

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