from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for, flash, session, send_file
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity, jwt_required, decode_token
import mysql.connector
import pymysql
import numpy as np
from sqlalchemy import create_engine, text
import hashlib
import base64
from datetime import timedelta, datetime, timezone
from functools import wraps
import io
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
import os
import cv2
import glob
import base64
from io import BytesIO
from tempfile import NamedTemporaryFile
from moviepy.video.compositing.concatenate import concatenate_videoclips
#from moviepy.video.fx import fadein, fadeout, crossfade, slide_in,slide_out,wipe
import numpy as np

def transitionname_to_function(transition_name):
    transitions = {
        "crossfade": crossfade,
        "fadein": fadein,
        "fadeout": fadeout,
        "slide_in": slide_in,
        "slide_out": slide_out,
        "wipe": wipe
    }

def createVid(images, duration, transition):
    # print(f"image is {images}, and duration is {duration} and tansistion is {transition}")
    vid_frames = []
    for file in images:
        img = cv2.imread(file)
        # height, width , layers = img.shape
        # size = (width, height)
        vid_frames.append(img)

    height, width, _ = vid_frames[0].shape
    video_path = os.path.join(os.path.dirname(__file__), 'video.avi')  # Adjust the path as needed
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'DIVX'), 25.0, (width, height))


    for frame in vid_frames:
        out.write(frame)

    out = cv2.VideoWriter('video.avi',cv2.VideoWriter_fourcc(*'DIVX'), 25.0, (width,height))

    # for i in range(len(vid)):
    #     out.write(vid[i])

    out.release()
    flash(f"ur vid is somewhere but idk lol")
    return video_path

""" import matplotlib.pyplot as plt
def display_image(img, title=None):
    
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if title:
        plt.title(title)
    plt.show() """


def mp_cv(images,duration,transition, audio):
    print(duration)
    audio_file = url_for('static', filename='audio/'+audio+'.mp3')
    image_clips =[]
    for base64_image,dur,t in zip(images,duration,transition):
        #image_data = base64.b64decode(base64_image + b'==')

        decoded_image_data = np.frombuffer(base64_image, np.uint8)
        image_array = cv2.imdecode(decoded_image_data, cv2.IMREAD_COLOR)

        #display_image(image_array)
        #with image_array as img_buffer:

        image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

        #display_image(image_rgb)
        
        image_clip = ImageClip(image_rgb, duration=dur)
        image_clips.append(image_clip)
    
    transition_functions = [transitionname_to_function(transition_name) for transition_name in transition]

    final_clips = []
    for i, clip in enumerate(image_clips[:-1]):
        transition_clip = transition_functions[i](clip, image_clips[i+1])
        final_clips.append(clip)
        final_clips.append(transition_clip)
    final_clips.append(image_clips[-1])
        
    # Concatenate ImageClip objects to create a video
    video = concatenate_videoclips(image_clips, method="compose")

    # Write the video to a file
    video.write_videofile("./static/video/output_video.mp4", codec='libx264', fps=10)

app = Flask(__name__)

# Configure JWT settings
app.config['JWT_SECRET_KEY'] = 'extremelysupersecretstringasjwtsecretkey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
app.secret_key = 'evenmoreextremelysupersecretkeyforsessionsecurity'
jwt = JWTManager(app)

engine = create_engine('mysql+pymysql://ISS_Project:veryhardpassword@localhost/issproject')
cursor = engine.connect()

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
            response = make_response(redirect(url_for('adminpage')))
            response.set_cookie('jwt_token', access_token, httponly=True)
            return response

        # Hash the provided password
        hashed_password = hash_password(password)

        # Retrieve hashed password from the database
        result = cursor.execute(text("SELECT user_id, username, password FROM users WHERE username=:username"), {'username': username})
        user = result.fetchone()

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
            jwt_token = request.cookies.get('jwt_token')
            print("Checking token")
            try:
                print("entered try")
                # Verify the JWT token

                payload = decode_token(jwt_token)
                user = payload.get('sub')
                expiry = datetime.utcfromtimestamp(payload.get('exp')).replace(tzinfo=timezone.utc)

                if user == 'admin' and datetime.now(timezone.utc) < expiry:
                    print("token found")
                    # Redirect to the user's homepage
                    return redirect(url_for('adminpage'))

                if user and datetime.now(timezone.utc) < expiry:
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
            return render_template('sign_up.html')

        # Hash the provided password
        hashed_password = hash_password(password)

        # Check if username already exists in the database
        result = cursor.execute(text("SELECT user_id FROM users WHERE username=:username"), {'username':username})
        existing_user = result.fetchone()

        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400
        
        params = {'username':username, 'password':hashed_password, 'email':email}

        # Insert the new user into the database
        cursor.execute(text("INSERT INTO users (username, password, email_id) VALUES (:username, :password, :email)"), params)
        cursor.commit()

        # Generate JWT token
        access_token = create_access_token(identity=username)
        # Set JWT token as a cookie
        response = make_response(redirect(url_for('user_homepage', username=username)))
        response.set_cookie('jwt_token', access_token, httponly=True)
        return response

    else:
        return render_template('sign_up.html')
    

""" def authenticate_required(f):
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
    return decorated_function """


def authentication(f):
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
                payload = decode_token(jwt_token)
                token_name = payload.get('sub')
                expiry = datetime.utcfromtimestamp(payload.get('exp')).replace(tzinfo=timezone.utc)
                print(token_name)
                username = kwargs.get('username')

                if (token_name != username or datetime.now(timezone.utc) > expiry):
                    return redirect(url_for('signin'))

            except Exception as e:
                print('error: ', e)
                # If an error occurs during token verification, redirect to sign-in page
                return redirect(url_for('signin'))
        
        # If authentication is successful, proceed to the decorated function
        return f(*args, **kwargs)
    return decorated_function


def authenticate_admin(f):
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
                payload = decode_token(jwt_token)
                token_name = payload.get('sub')
                expiry = datetime.utcfromtimestamp(payload.get('exp')).replace(tzinfo=timezone.utc)
                print(token_name)

                if (token_name != 'admin' or datetime.now(timezone.utc) > expiry):
                    return redirect(url_for('signin'))

            except Exception as e:
                print('error: ', e)
                # If an error occurs during token verification, redirect to sign-in page
                return redirect(url_for('signin'))
        
        # If authentication is successful, proceed to the decorated function
        return f(*args, **kwargs)
    return decorated_function


@app.route('/signout', methods=['POST'])
#@jwt_required()
@authentication
def signout():
    
    response = make_response(redirect(url_for('signin')))
    response.delete_cookie('jwt_token')
    response.delete_cookie('session')

    return response
    
    
# User homepage endpoint
@app.route('/<username>/home', methods=['GET'])
#@jwt_required()
@authentication
def user_homepage(username):
    # Render the user's homepage
    return render_template('user.html', username=username)

@app.route('/admin', methods=['GET'])
#@jwt_required()
@authenticate_admin
def adminpage():
    # Render the user's homepage
    return render_template('admin.html')

@app.route('/get_user_details')
@authenticate_admin
def get_user_details():
    result = cursor.execute(text("SELECT user_id, username, email_id FROM users"))
    users = result.fetchall()

    data = [[data for data in user] for user in users]
    return jsonify(data)

@app.route('/<username>/upload', methods=['GET'])
#@jwt_required()
def upload(username):
    # Render the user's homepage
    return render_template('upload.html', username=username)

@app.route('/upload_images/<username>', methods=['POST'])
@authentication
def upload_images(username):
    
    user_id_result = cursor.execute(text("SELECT user_id FROM users WHERE username=:username"), {'username':username})
    user_id = user_id_result.fetchone()[0]

    files = request.files.getlist('images[]')
    filenames = request.form.getlist('filenames[]')
    filetypes = request.form.getlist('filetypes[]')

    print(files)
    print(filenames)

    for i in range(len(files)):
        file = files[i]
        filename = filenames[i]
        filetype = filetypes[i]

        img = file.read()
        upload_time = datetime.now()

        params = {'user_id': user_id, 'img': img, 'filename': filename, 'upload_time': upload_time, 'filetype': filetype}
        cursor.execute(text("INSERT INTO images (user_id, image, filename, upload_time, file_type) VALUES (:user_id, :img, :filename, :upload_time, :filetype)"), params)

    cursor.commit()
    print("uploaded")
    return jsonify({'message': 'Images saved successfully'})

@app.route('/<username>/history', methods=['GET'])
#@jwt_required()
@authentication
def history(username):
    # Render the user's homepage
    return render_template('history.html', username=username)

@app.route('/get_images/<username>')
@authentication
def get_images(username):

    result = cursor.execute(text("SELECT user_id FROM users WHERE username=:username"), {'username':username})
    user_ids = result.fetchone()
    print(user_ids)
    user_id = user_ids[0]
    print(user_id)

    # Query the database to fetch the image data
    result = cursor.execute(text("SELECT image, filename, file_type FROM images WHERE user_id=:user_id"), {'user_id':user_id})
    images_data = result.fetchall()

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
@authentication
def get_selected_images(username):

    result = cursor.execute(text("SELECT user_id FROM users WHERE username=:username"), {'username':username})
    user_ids = result.fetchone()
    user_id = user_ids[0]
    print(user_id)

    selected_images = session['selected_images']
    print(selected_images)

    if selected_images == []:
        return jsonify([])
    
    placeholders = ', '.join([':image_filename' + str(i) for i in range(len(selected_images))])
    query = f"SELECT image, filename, file_type FROM images WHERE user_id = :user_id AND filename IN ({placeholders})"

    params = {'user_id': user_id}
    for i, image_filename in enumerate(selected_images):
        params['image_filename' + str(i)] = image_filename
            
    # Execute the query using SQLAlchemy's text() function to safely construct the query
    result = cursor.execute(text(query), params)
    images_data = result.fetchall()

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

@app.route('/get_audio_names/<username>', methods=['GET'])
def get_audio_names(username):
    
    """ result = cursor.execute(text("SELECT user_id FROM users WHERE username=:username"), {'username':username})
    user_ids = result.fetchone()
    print(user_ids)
    user_id = user_ids[0]
    print(user_id)

    # Query the database to fetch the image data
    result = cursor.execute(text("SELECT audio_name FROM audio WHERE user_id=:user_id"), {'user_id':user_id})
    audio_data = result.fetchall() """

    result = cursor.execute(text("SELECT audio_name FROM audio WHERE user_id = 0"))
    list = result.fetchall()

    """ list.extend(audio_data) """

    final_list = [row[0] for row in list]

    # Return the list of image details as JSON response
    return jsonify(final_list)

@app.route('/get_audio/<name>')
def get_audio(name):

    # Query the database to fetch the image data
    result = cursor.execute(text("SELECT audio_file, audio_type FROM audio WHERE audio_name=:name"), {'name':name})
    audio_data = result.fetchone()

    # Return the list of image details as JSON response
    return send_file(io.BytesIO(audio_data[0]), mimetype=audio_data[1])

@app.route('/<username>/video', methods=['GET'])
#@jwt_required()
@authentication
def video(username):
    return render_template('video.html', username=username)

@app.route('/generate_video/<username>', methods=['POST'])
@authentication
def generate_video(username):
    try:
        
        result = cursor.execute(text("SELECT user_id FROM users WHERE username=:username"), {'username':username})
        user_ids = result.fetchone()
        user_id = user_ids[0]
        print(user_id)

        selected_images = session['selected_images']
        print(selected_images)

        if selected_images == []:
            return jsonify([])
        
        placeholders = ', '.join([':image_filename' + str(i) for i in range(len(selected_images))])
        query = f"SELECT image, filename, file_type FROM images WHERE user_id = :user_id AND filename IN ({placeholders})"

        params = {'user_id': user_id}
        for i, image_filename in enumerate(selected_images):
            params['image_filename' + str(i)] = image_filename
                
        # Execute the query using SQLAlchemy's text() function to safely construct the query
        result = cursor.execute(text(query), params)
        images_data = result.fetchall()

        images = []

        # Loop through the retrieved image data
        for image_data, image_name, image_format in images_data:

            #image_data_base64 = base64.b64encode(image_data).decode('utf-8')

            # Append each image detail to the list
            images.append(image_data)
        
        data = request.get_json()
        durations = data['durations']
        transition = data['transition']
        audio = data['audio']

        if not selected_images:
            return jsonify({'message': 'No selected images for slideshow'}), 400
        
        else:
            #video_path = NamedTemporaryFile(suffix=".mp4").name
            mp_cv(images,durations,transition, audio)  ##### ARYANIL'S JOB!!!!!!!!!!!!!

            return 'GG'

            #return send_file(video_path, as_attachment=True)

        """ video_filename = f"{username}_slideshow.mp4"
        video_path = os.path.join('static', 'videos', video_filename)

        # Create a list to store ImageClips
        clips = []

        for image_data in selected_images:
            # Convert base64 image data to NumPy array
            nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
            img = ImageClip(nparr.tobytes(), duration=1)
            clips.append(img)

        # Concatenate the ImageClips to create a video
        video = VideoFileClip(clips, fps=1)

        # Write the video to a file
        video.write_videofile(video_path, codec='libx264', audio_codec='aac') """

        #return 'hello'
    except Exception as e:
        print('Error generating video:', e)
        return jsonify({'message': 'Error generating video'}), 500




if __name__ == '__main__':
    app.run(debug=True)