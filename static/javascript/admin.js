document.addEventListener('DOMContentLoaded', function () {

    const tablebody = document.getElementById('details');

    fetch('/get_user_details')
    .then(response => response.json())
    .then(users => {
        console.log('Fetched users:', users);
        users.forEach(user => {
            console.log('Processing user:', user); 
            
            let row = document.createElement('tr');
            let c1 = document.createElement('td');
            let c2 = document.createElement('td');

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

    const signoutbutton = document.getElementById('signout');

    signoutbutton.addEventListener('click', function() {

        fetch('/signout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                // Token deleted successfully
                //alert('Token deleted successfully!');
            } else {
                // Error handling
                //alert('Failed to delete token!');
            }
        })
        .catch(error => {
            console.error('Error deleting token:', error);
        });

    });

});
