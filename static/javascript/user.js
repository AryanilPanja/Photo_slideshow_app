document.addEventListener('DOMContentLoaded', function () {

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
