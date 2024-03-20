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
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
import os
import cv2
import glob
import base64
from io import BytesIO
from tempfile import NamedTemporaryFile
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx import fadein, fadeout
import numpy as np
import ffmpeg


def transitionname_to_filter(transition_name):
    filters = {
        "crossfade": "xfade=c='black':s=30:d=1",
        "fadein": "fade=in:st=0:d=1",
        "fadeout": "fade=out:st=0:d=1",
        "slide_in": "crop=in_w:in_h:t=0:d=1",
        "slide_out": "crop=out_w:out_h:t=0:d=1",
        "wipe": "crop=in_w:in_h:x=0:y=h:t=0:d=1"
    }
    return filters.get(transition_name)

def mp_cv(images, duration, transition, audio, resolution):
    print(duration)

    image_clips = []
    for base64_image, dur, t in zip(images, duration, transition):
        decoded_image_data = np.frombuffer(base64_image, np.uint8)
        image_array = cv2.imdecode(decoded_image_data, cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        image_clip = ImageClip(image_rgb, duration=dur)
        image_clips.append(image_clip)

    final_clips = []
    

    final_clips.append(image_clips[-1])

    audio_file = os.path.join(app.root_path, 'static', 'audio', audio + '.mp3')
    print(audio_file)
    audio_clip = AudioFileClip(audio_file)

    total_duration = sum(duration)
    num_loops = int(total_duration / audio_clip.duration) + 1

    composite_audio = CompositeAudioClip([audio_clip] * num_loops)
    composite_audio = composite_audio.set_duration(total_duration)


    #aryan 

    fade_duration = 1


    clips_with_transitions = []
    for i in range(len(image_clips) - 1):
        if image_clips[i+1]:
            image_clips[i+1] = image_clips[i+1].fx(fadeout, fade_duration)
            image_clips[i] = image_clips[i].fx(fadein, fade_duration)
            final = CompositeVideoClip([image_clips[i], image_clips[i+1].set_start(3).crossfadein(1)])

        # clip_with_transition = image_clips[i].crossfadeout(t)  # Fade out transition
        # clip_with_transition = clip_with_transition.set_end(t)  # Set end time for transition
        # next_clip = image_clips[i + 1].crossfadein(t)  # Fade in transition
        # clip_with_transition = concatenate_videoclips([clip_with_transition, next_clip])
        # clips_with_transitions.append(clip_with_transition)
    
    clips_with_transitions.append(image_clips[-1])

    for frame in image_clips.iter_frames(fps=image_clips.fps*5):
        frame = cv2.cvtColor(frame.astype('uint8'), cv2.COLOR_RGB2BGR)  # Convert to 8-bit depth
        cv2.imshow("Final Clip", frame)
    
    # Check for the 'q' key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

    # Concatenate ImageClip objects to create a video
    video = concatenate_videoclips(image_clips, method="compose")
    video = video.set_audio(composite_audio)

    # Write the video to a file
    video.write_videofile("./static/video/output_video.mp4",threads = 8, codec='libx264', fps=10)
    audio_clip.close()


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'extremelysupersecretstringasjwtsecretkey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
app.secret_key = 'evenmoreextremelysupersecretkeyforsessionsecurity'
jwt = JWTManager(app)

engine = create_engine('cockroachdb://iss_project:ebaf7wlpWMMep44CdmnHEA@issproject-4069.7s5.aws-ap-south-1.cockroachlabs.cloud:26257/issproject?sslmode=verify-full')
cursor = engine.connect()

@app.route('/')
def land():
    return render_template('welcome.html')

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if (username == 'admin' and password == 'admin'):

            access_token = create_access_token(identity='admin')
            response = make_response(redirect(url_for('adminpage')))
            response.set_cookie('jwt_token', access_token, httponly=True)
            return response

        hashed_password = hash_password(password)

        result = cursor.execute(text("SELECT user_id, username, password FROM users WHERE username=:username"), {'username': username})
        user = result.fetchone()

        if user and hashed_password == user[2]:
            access_token = create_access_token(identity=user[1])
            response = make_response(redirect(url_for('user_homepage', username=user[1])))
            response.set_cookie('jwt_token', access_token, httponly=True)
            response.headers['Authorization'] = f'Bearer {access_token}'
            return response

        return jsonify({'message': 'Invalid username or password'}), 401

    else:
        if 'jwt_token' in request.cookies:
            jwt_token = request.cookies.get('jwt_token')
            print("Checking token")
            try:
                print("entered try")

                payload = decode_token(jwt_token)
                user = payload.get('sub')
                expiry_timestamp = payload.get('exp')
                expiry = datetime.fromtimestamp(expiry_timestamp, timezone.utc)

                if user == 'admin' and datetime.now(timezone.utc) < expiry:
                    print("token found")
                    return redirect(url_for('adminpage'))

                if user and datetime.now(timezone.utc) < expiry:
                    print("token found")
                    return redirect(url_for('user_homepage', username=user))
                
            except Exception as e:
                # If an error occurs during token verification, return unauthorized
                pass

        # If no valid token is found or authentication fails, render the sign-in page
        return render_template('sign_in.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmpass = request.form.get('confirmPassword')
        email = request.form.get('email')

        if password != confirmpass:
            return render_template('sign_up.html')

        hashed_password = hash_password(password)

        result = cursor.execute(text("SELECT user_id FROM users WHERE username=:username"), {'username':username})
        existing_user = result.fetchone()

        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400
        
        params = {'username':username, 'password':hashed_password, 'email':email}

        cursor.execute(text("INSERT INTO users (username, password, email_id) VALUES (:username, :password, :email)"), params)
        cursor.commit()

        access_token = create_access_token(identity=username)
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
        jwt_token = request.cookies.get('jwt_token')
        if not jwt_token:
            return redirect(url_for('signin'))
        else:
            try:
                payload = decode_token(jwt_token)
                token_name = payload.get('sub')
                expiry_timestamp = payload.get('exp') 
                expiry = datetime.fromtimestamp(expiry_timestamp, timezone.utc)
                print(token_name)
                username = kwargs.get('username')

                if (token_name != username or datetime.now(timezone.utc) > expiry):
                    return redirect(url_for('signin'))

            except Exception as e:
                print('error: ', e)
                return redirect(url_for('signin'))
        
        return f(*args, **kwargs)
    return decorated_function


def authenticate_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jwt_token = request.cookies.get('jwt_token')
        if not jwt_token:
            return redirect(url_for('signin'))
        else:
            try:
                payload = decode_token(jwt_token)
                token_name = payload.get('sub')
                expiry_timestamp = payload.get('exp')  
                expiry = datetime.fromtimestamp(expiry_timestamp, timezone.utc)
                print(token_name)

                if (token_name != 'admin' or datetime.now(timezone.utc) > expiry):
                    return redirect(url_for('signin'))

            except Exception as e:
                print('error: ', e)
                return redirect(url_for('signin'))
        
        return f(*args, **kwargs)
    return decorated_function


@app.route('/signout', methods=['POST'])
@authentication
def signout():
    
    response = make_response(redirect(url_for('signin')))
    response.set_cookie('jwt_token', "", 0)
    response.set_cookie('session', "", 0)

    return response
    
    
@app.route('/<username>/home', methods=['GET'])
@authentication
def user_homepage(username):
    return render_template('user.html', username=username)

@app.route('/admin', methods=['GET'])
@authenticate_admin
def adminpage():
    return render_template('admin.html')

@app.route('/get_user_details')
@authenticate_admin
def get_user_details():
    result = cursor.execute(text("SELECT user_id, username, email_id FROM users"))
    users = result.fetchall()

    data = [[data for data in user] for user in users]
    return jsonify(data)

@app.route('/<username>/upload', methods=['GET'])
def upload(username):
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
@authentication
def history(username):
    return render_template('history.html', username=username)

@app.route('/get_images/<username>')
@authentication
def get_images(username):

    result = cursor.execute(text("SELECT user_id FROM users WHERE username=:username"), {'username':username})
    user_ids = result.fetchone()
    user_id = user_ids[0]

    result = cursor.execute(text("SELECT image, filename, file_type FROM images WHERE user_id=:user_id"), {'user_id':user_id})
    images_data = result.fetchall()

    images = []

    for image_data, image_name, image_format in images_data:

        image_data_base64 = base64.b64encode(image_data).decode('utf-8')

        images.append({
            'image_data': image_data_base64,
            'image_name': image_name,
            'image_format': image_format
        })

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
            
    result = cursor.execute(text(query), params)
    images_data = result.fetchall()

    images = []

    for image_data, image_name, image_format in images_data:

        image_data_base64 = base64.b64encode(image_data).decode('utf-8')

        images.append({
            'image_data': image_data_base64,
            'image_name': image_name,
            'image_format': image_format
        })

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

    return jsonify(final_list)

@app.route('/get_audio/<name>')
def get_audio(name):

    result = cursor.execute(text("SELECT audio_file, audio_type FROM audio WHERE audio_name=:name"), {'name':name})
    audio_data = result.fetchone()

    return send_file(io.BytesIO(audio_data[0]), mimetype=audio_data[1])

@app.route('/<username>/video', methods=['GET'])
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
                
        result = cursor.execute(text(query), params)
        images_data = result.fetchall()

        images = []

        for image_data, image_name, image_format in images_data:

            images.append(image_data)
        
        data = request.get_json()
        durations = data['durations']
        transition = data['transition']
        audio = data['audio']
        resolution = data['resolution']

        if not selected_images:
            return jsonify({'message': 'No selected images for slideshow'}), 400
        
        else:
            #video_path = NamedTemporaryFile(suffix=".mp4").name
            mp_cv(username, images,durations,transition, audio, resolution)  ##### ARYANIL'S JOB!!!!!!!!!!!!!

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

    except Exception as e:
        print('Error generating video:', e)
        return jsonify({'message': 'Error generating video'}), 500


@app.route('/delete_video/<username>', methods=['POST'])
@authentication
def delete_video(username):
    file_path = os.path.join(app.root_path, 'static', 'video', username + '_video.mp4')
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'Video has been deleted.'})
    else:
        return jsonify({'error': 'Video file does not exist.'}), 404


if __name__ == '__main__':
    app.run(debug=True)