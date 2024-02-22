from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for, flash, session
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity, jwt_required
import mysql.connector
import hashlib
import base64
from datetime import timedelta, datetime
from functools import wraps

app = Flask(__name__)

# Configure JWT settings
app.config['JWT_SECRET_KEY'] = 'extremelysupersecretstringasjwtsecretkey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
app.secret_key = 'evenmoreextremelysupersecretkeyforsessionsecurity'
jwt = JWTManager(app)

# MySQL connection
connection = mysql.connector.connect(
    user='ISS_Project', password='veryhardpassword', host='localhost', database='issproject'
)
cursor = connection.cursor()

@app.route('/')
def land():
    print("landed")
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

        if (username == 'admin' and password == 'admin'):

            access_token = create_access_token(identity='admin')
            # Set JWT token as a cookie
            response = make_response(redirect(url_for('admin')))
            response.set_cookie('jwt_token', access_token, httponly=True)
            return response

        # Hash the provided password
        hashed_password = hash_password(password)

        # Retrieve hashed password from the database
        cursor.execute("SELECT user_id, username, password FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and hashed_password == user[2]:
            # Generate JWT token
            access_token = create_access_token(identity=user[1])
            # Set JWT token as a cookie
            response = make_response(redirect(url_for('user_homepage', username=user[1])))
            response.set_cookie('jwt_token', access_token, httponly=True)
            response.headers['Authorization'] = f'Bearer {access_token}'
            return response

        # If username or password is invalid, return error response
        return jsonify({'message': 'Invalid username or password'}), 401

    else:
        # Check for JWT token in the request cookies
        if 'jwt_token' in request.cookies:
            print("Checking token")
            try:
                print("entered try")
                # Verify the JWT token
                verify_jwt_in_request()

                print("token verified")

                # Extract user identity from the JWT token
                user = get_jwt_identity()

                if user:
                    print("token found")
                    # Redirect to the user's homepage
                    return redirect(url_for('user_homepage', username=user))
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
    

def authenticate_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if JWT token is present in the request cookies
        jwt_token = request.cookies.get('jwt_token')
        if not jwt_token:
            # Redirect to the sign-in page if JWT token is not present
            return redirect(url_for('signin'))
        else:
            try:
                # Verify the JWT token
                verify_jwt_in_request()
            except Exception as e:
                print(e)
                # If an error occurs during token verification, redirect to sign-in page
                return redirect(url_for('signin'))
        
        # If authentication is successful, proceed to the decorated function
        return f(*args, **kwargs)
    return decorated_function
    

# User homepage endpoint
@app.route('/<username>/home', methods=['GET'])
#@jwt_required()
def user_homepage(username):
    # Render the user's homepage
    return render_template('user.html', username=username)

@app.route('/admin', methods=['GET'])
#@jwt_required()
def adminpage():
    # Render the user's homepage
    return render_template('admin.html')

@app.route('/get_user_details')
def get_user_details():
    cursor.execute("SELECT user_id, username, email_id FROM users")
    users = cursor.fetchall()
    return jsonify(users)

@app.route('/<username>/upload', methods=['GET'])
#@jwt_required()
def upload(username):
    # Render the user's homepage
    return render_template('upload.html', username=username)

@app.route('/upload_images/<username>', methods=['POST'])
def upload_images(username):
    
    file = request.files['image']
    filename = request.form['filename']
    filetype = request.form['filetype']

    img = file.read()

    cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
    user_ids = cursor.fetchone()
    user_id = user_ids[0]

    time = datetime.now()

    cursor.execute("INSERT INTO images (user_id, image, filename, upload_time, file_type) VALUES (%s, %s, %s, %s, %s)", (user_id, img, filename, time, filetype))
    connection.commit()

    while cursor.nextset():
        pass

    print("uploaded")

    return jsonify({'message': 'images saved successfully'})

@app.route('/<username>/history', methods=['GET'])
#@jwt_required()
def history(username):
    # Render the user's homepage
    return render_template('history.html', username=username)

@app.route('/get_images/<username>')
def get_images(username):

    cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
    user_ids = cursor.fetchone()
    user_id = user_ids[0]
    print(user_id)

    # Query the database to fetch the image data
    cursor.execute("SELECT image, filename, file_type FROM images WHERE user_id = %s", (user_id,))
    images_data = cursor.fetchall()

    images = []

    # Loop through the retrieved image data
    for image_data, image_name, image_format in images_data:

        image_data_base64 = base64.b64encode(image_data).decode('utf-8')

        # Append each image detail to the list
        images.append({
            'image_data': image_data_base64,
            'image_name': image_name,
            'image_format': image_format
        })

    # Return the list of image details as JSON response
    return jsonify(images)

@app.route('/save_selected_images', methods=['POST'])
def save_images():
    
    selected_images = request.json
    session['selected_images'] = selected_images
    print(selected_images)

    return jsonify({'message': 'Selected images saved successfully'})

@app.route('/get_selected_images/<username>', methods=['GET'])
def get_selected_images(username):

    while cursor.nextset():
        pass

    cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
    user_ids = cursor.fetchone()
    user_id = user_ids[0]
    print(user_id)

    selected_images = session['selected_images']
    session['selected_images'] = []
    print(selected_images)

    if selected_images == []:
        return jsonify([])
    
    placeholders = ', '.join(['%s'] * len(selected_images))

    query = f"SELECT image, filename, file_type FROM images WHERE user_id = %s AND filename IN ({placeholders})"
    print(query)
    cursor.execute(query, [user_id] + selected_images)
    images_data = cursor.fetchall()

    images = []

    # Loop through the retrieved image data
    for image_data, image_name, image_format in images_data:

        image_data_base64 = base64.b64encode(image_data).decode('utf-8')

        # Append each image detail to the list
        images.append({
            'image_data': image_data_base64,
            'image_name': image_name,
            'image_format': image_format
        })

    # Return the list of image details as JSON response
    return jsonify(images)

@app.route('/<username>/video', methods=['GET'])
#@jwt_required()
def video(username):
    return render_template('video.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)