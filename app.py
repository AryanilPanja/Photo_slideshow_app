from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for, flash
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity
import mysql.connector
import hashlib

app = Flask(__name__)

# Configure JWT settings
app.config['JWT_SECRET_KEY'] = 'extremelysupersecretstringasjwtsecretkey'
jwt = JWTManager(app)

# MySQL connection
connection = mysql.connector.connect(
    user='ISS_Project', password='veryhardpassword', host='localhost', database='issproject'
)
cursor = connection.cursor()

@app.route('/')
def land():
    return render_template('welcome.html')

# Hashing function using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Endpoint for user login
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # Hash the provided password
        hashed_password = hash_password(password)

        # Retrieve hashed password from the database
        cursor.execute("SELECT user_id, username, password FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and hashed_password == user[2]:
            # Generate JWT token
            access_token = create_access_token(identity=user[0])
            # Set JWT token as a cookie
            response = make_response(redirect(url_for('user_homepage', username=user[1])))
            response.set_cookie('jwt_token', access_token, httponly=True)
            return response

        # If username or password is invalid, return error response
        return jsonify({'message': 'Invalid username or password'}), 401

    else:
        # Check for JWT token in the request cookies
        if 'jwt_token' in request.cookies:
            try:
                # Verify the JWT token
                verify_jwt_in_request()

                # Extract user identity from the JWT token
                current_user_id = get_jwt_identity()

                # Authenticate the user based on the extracted identity
                # This could involve fetching user details from the database
                cursor.execute("SELECT username FROM users WHERE user_id=%s", (current_user_id,))
                user = cursor.fetchone()

                if user:
                    # Redirect to the user's homepage
                    return redirect(url_for('user_homepage', username=user[0]))
            except Exception as e:
                # If an error occurs during token verification, return unauthorized
                pass

        # If no valid token is found or authentication fails, render the sign-in page
        return render_template('sign_in.html')


# Endpoint for user signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmpass = request.form.get('confirmPassword')
        email = request.form.get('email')

        if password != confirmpass:
            flash('Passwords do not match')

        # Hash the provided password
        hashed_password = hash_password(password)

        # Check if username already exists in the database
        cursor.execute("SELECT user_id FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, password, email_id) VALUES (%s, %s, %s)", (username, hashed_password, email))
        connection.commit()

        # Generate JWT token
        access_token = create_access_token(identity=username)
        # Set JWT token as a cookie
        response = make_response(redirect(url_for('user_homepage', username=username)))
        response.set_cookie('jwt_token', access_token, httponly=True)
        return response

    else:
        return render_template('sign_up.html')
    

# User homepage endpoint
@app.route('/<username>/home', methods=['GET'])
def user_homepage(username):
    # Render the user's homepage
    return render_template('user.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)
