# -*- coding: utf-8 -*-
import os
import io
import json
from flask import Flask, render_template, g, flash, request, redirect, url_for, send_from_directory, session, jsonify, abort, make_response
from random import randint
from time import strftime
from wtforms import Form, TextField, FileField, TextAreaField, validators, StringField, SubmitField, BooleanField, SelectField, SelectMultipleField, PasswordField, RadioField
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from data import Sakes

from werkzeug import utils
from google.cloud import vision

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from flask_login import LoginManager, UserMixin, login_user, logout_user

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': 'sora-sakelibrary',
})

db = firestore.client()


# user = auth.create_user(
#     email='user@example.com',
#     email_verified=False,
#     phone_number='+15555550100',
#     password='secretPassword',
#     display_name='John Doe',
#     photo_url='http://www.example.com/12345678/photo.png',
#     disabled=False)
# print('Sucessfully created new user: {0}'.format(user.uid))

client = vision.ImageAnnotatorClient()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    return app

app = create_app()

basedir = os.path.abspath(os.path.dirname(__file__))
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'static'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_TYPE='image',
    DROPZONE_MAX_FILE_SIZE=3,
    DROPZONE_MAX_FILES=30,
)
dropzone = Dropzone(app)

app.config['MAX_CONTENT_LENGTH'] = 1 * 2024 * 2024
app.config['SECRET_KEY'] = os.urandom(24)

Sakes = Sakes()



# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + 'static/img'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB
latestImgPath = []
imageFileName = []






@app.route('/upload')
def upload():
    return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
  if request.method == 'POST':
    f = request.files['file']
    filename = utils.secure_filename(f.filename)
    f.save('static/' + filename)
    img_path = 'static/'+ os.path.join(os.path.dirname(__file__),f.filename)
    with io.open(img_path, 'rb') as image_file:
      content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    visionApiText=[]
    pureText=[]
    for text in texts:
      visionApiText.append('\n"{}"'.format(text.description))
      pureText.append(text.description)
      return render_template('uploader.html',visionApiText=visionApiText, image=img_path, text=pureText)


@app.route('/uploads',methods=['POST', 'GET'])
def uploads():
    if request.method == 'POST':
        f = request.files.get('file')
        img_path = os.path.join(app.config['UPLOADED_PATH'], f.filename)
        latestImgPath.append(img_path)
        imageFileName.append(f.filename)
        f.save(img_path)
    return render_template('uploads.html')


@app.route('/uploadpreview', methods = ['GET', 'POST'])
def uploadpreview():
  if request.method == 'POST':
    img_path = latestImgPath.pop()
    img_filename = imageFileName.pop()
    print('img_filename'+img_filename)
    with io.open(img_path, 'rb') as image_file:
      content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    visionApiText=[]
    pureText=[]
    for text in texts:
      visionApiText.append('\n"{}"'.format(text.description))
      pureText.append(text.description)
      return render_template('uploadpreview.html',visionApiText=visionApiText, img_path=img_path, img_filename=img_filename, text=pureText)

class SakeSearchForm(Form):
    choices = [('Sake Name', 'Sake Name'),
               ('Maker', 'Maker'),
               ('Region', 'Region')]
    select = SelectField('Search for Sake:', choices=choices)
    search = StringField('')

class SignUpForm(Form):
    firstname = TextField('Firstname:', validators=[validators.required()])
    lastname = TextField(':Lastname:', validators=[validators.required()])
    usertype = SelectField('Usertype:', choices=[('sake_consumer','Sake Consumer'),('sake_buyer','Sake Buyer'),('sake_maker','Sake Maker'), ('others','Others')], validators=[validators.required()])
    email = StringField("Email:",  validators=[validators.required("Please enter your email address.")])
    password = PasswordField("Password:",validators=[validators.DataRequired()])

def get_time_userAdded():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def write_user_log(firstname, lastname, usertype, email, password):
    email = 'sora@gmail.com'
    password = '2kazuhokai'
    print(user)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)

    if request.method == 'POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        usertype=request.form['usertype']
        email=request.form['email']
        password=request.form['password']
        

        if form.validate():
            write_user_log(firstname, lastname, usertype, email, password)
            flash('Hello: {} {}'.format(firstname, lastname))
            return render_template('home.html')

        else:
            flash('Error: All Fields are Required')
        
    return render_template('signup.html', form=form)



class AddSakeForm(Form):
    name = TextField('Sake Brandname:', validators=[validators.required()])
    saketype = SelectField('Sake Type:', choices=[('junmaidaiginjo','Junmai Daiginjo'),('Daiginjo','Daiginjo'),('Junmai Ginjo','Junmai Ginjo'), ('others','Others')])
    taste = TextField('taste:', validators=[validators.required()])
    description = TextAreaField('Description:', validators=[validators.required()])

def get_time_addsake():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def add_sake_to_db(name, saketype, taste, description):
    timestamp = get_time_addsake()
    db.collection('sakes').document(name).set({
        'createdAt': timestamp,
        'name': name,
        'saketype': saketype,
        'taste': taste,
        'Description': description,
    })



@app.route("/addSake", methods=['GET', 'POST'])
def addsake():
    form = AddSakeForm(request.form)

    if request.method == 'POST':
        name=request.form['name']
        saketype=request.form['saketype']
        taste=request.form['taste']
        description=request.form['description']

        if form.validate():
            add_sake_to_db(name, saketype, taste, description)
            flash('Sake Added!: {} {}'.format(name, saketype))

        else:
            flash('Error: All Fields are Required')
        
    return render_template('addSake.html', form=form)

class FeedbackForm(Form):
    title = TextField('Title:', validators=[validators.required()])
    feedback = TextAreaField('Feedback:', validators=[validators.required()])


def write_to_feedback(title, feedback):
    timestamp = strftime("%Y-%m-%dT%H:%M")
    db.collection('feedbacks').document(title).set({
        'createdAt': timestamp,
        'title': title,
        'feedback': feedback,
    })

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm(request.form)

    if request.method == 'POST':
        title=request.form['title']
        feedback=request.form['feedback']

        if form.validate():
            write_to_feedback(title, feedback)
            flash('Thank you for your feedback!')

        else:
            flash('Error: All Fields are Required')
        
    return render_template('feedback.html', form=form)


class AddMakerForm(Form):
    maker = TextField('Maker:', validators=[validators.required()])
    region = SelectField('Region:', choices=[('tokyo','Tokyo'),('osaka','Osaka'),('fukuoka','Fukuoka'),('niigata','Niigata')])
    url = TextField('Url:', validators=[validators.url(require_tld=True, message="Invalid URL")])


def write_to_makerlist(maker, region, url):
    timestamp = strftime("%Y-%m-%dT%H:%M")
    db.collection('makers').document(maker).set({
        'createdAt': timestamp,
        'maker': maker,
        'region': region,
        'url': url,
    })


@app.route("/addMaker", methods=['GET', 'POST'])
def addmaker():
    form = AddMakerForm(request.form)

    if request.method == 'POST':
        maker=request.form['maker']
        region=request.form['region']
        url=request.form['url']

        if form.validate():
            write_to_makerlist(maker, region, url)
            flash('Thank you for the information!')

        else:
            flash('Error: All Fields are Required')
        
    return render_template('addMaker.html', form=form)


#API
@app.route('/api/sakes', methods=['GET'])
def get_sakes():
    return jsonify({'Sakes': Sakes})

@app.route('/api/sake/<string:id>', methods=['GET'])
def get_sake(id):
    sake = [__sake__ for __sake__ in Sakes if __sake__['id'] == id]
    if len(sake) == 0:
        abort(404)
    return jsonify({'sake': sake[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route("/sake/<string:id>/")
def sake(id):
    for __sake__ in Sakes:
        if __sake__['id'] == id:
            print(__sake__['name'])
            return render_template("sake.html", id = id, name = __sake__['name'], type = __sake__['type'], maker = __sake__['maker'], region = __sake__['region'], image = __sake__['image'])



@app.route("/", methods=['GET', 'POST'])
def home():
    form = SakeSearchForm(request.form)
    # if request.method == 'POST':
    #     return search_results(form)
    return render_template("home.html", form=form)


@app.route('/logout')
def logout():
    # session.pop('username', None)
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('signup'))
    # return redirect(url_for('home'))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/sakelist")
def sakelist():
    return render_template("sakelist.html", sakes = Sakes)



if __name__ == '__main__':
    app.run()