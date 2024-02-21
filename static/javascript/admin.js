document.addEventListener('DOMContentLoaded', function () {

    const tablebody = document.querySelector('#details');

    fetch('/get_user_details')
    .then(response => response.json())
    .then(users => {
        console.log('Fetched users:', users); // Log fetched users array
        // Process the user details
        users.forEach(user => {
            console.log('Processing user:', user); // Log individual user object
            
            let row = document.createElement('tr');
            let c1 = document.createElement('td');
            let c2 = document.createElement('td');

            // Use backticks for string interpolation
            c1.innerHTML = `${user[1]}`;
            c2.innerHTML = `${user[2]}`;

            row.appendChild(c1);
            row.appendChild(c2);

            tablebody.appendChild(row);

        });
    })
    .catch(error => {
        console.error('Error fetching user details:', error);
    });

});
