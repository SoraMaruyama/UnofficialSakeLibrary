# -*- coding: utf-8 -*-
import pyrebase
import uuid
import base64
import os
import io
import json
from datetime import datetime
from flask import Flask, render_template, g, flash, request, redirect, url_for, send_from_directory, session, jsonify, abort, make_response
from random import randint
from time import strftime
from wtforms import Form, TextField, FileField, TextAreaField, validators, StringField, SubmitField, BooleanField, SelectField, SelectMultipleField, PasswordField, RadioField
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
# from data import Sakes

from werkzeug import utils
from google.cloud import vision

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# from firebase_admin import auth
from flask_login import LoginManager, UserMixin, login_user, logout_user

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'sora-sakelibrary',
    'storageBucket': 'sora-sakelibrary.appspot.com',
})

db = firestore.client()


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


# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + 'static/'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB
latestImgPath = []
imageFileName = []


pyfirebase = pyrebase.initialize_app(config)
auth = pyfirebase.auth()
storage = pyfirebase.storage()


# Sakes = Sakes()

# for __sake__ in Sakes:
#     image = __sake__['image']
#     path = "item/" + image
#     itemurl = storage.child(path).get_url(None)
#     name = __sake__['name']
#     maker = __sake__['maker']
#     region = __sake__['region']

#     db.collection('sakes').document(name).set({
#         'createdAt': datetime.now(),
#         'id': str(uuid.uuid4()),
#         'name': name.decode("utf-8"),
#         'name_ja': __sake__['name_ja'].decode("utf-8"),
#         'type': __sake__['type'].decode("utf-8"),
#         'type_ja': __sake__['type_ja'],
#         'is_fruity': False,
#         'taste': '',
#         'maker': maker.decode("utf-8"),
#         'maker_ja': __sake__['maker_ja'].decode("utf-8"),
#         'region': region.decode("utf-8"),
#         'region_ja': __sake__['region_ja'].decode("utf-8"),
#         'url': __sake__['url'].decode("utf-8"),
#         'description': '',
#         'description_ja':'',
#         'image': str(image).decode("utf-8"),
#         'image_url': str(itemurl).decode("utf-8"),
#     })


@app.route('/uploads', methods=['POST', 'GET'])
def uploads():
    if request.method == 'POST':
        f = request.files.get('file')
        img_path = os.path.join(app.config['UPLOADED_PATH'], f.filename)
        latestImgPath.append(img_path)
        filename = f.filename
        imageFileName.append(filename)
        f.save(img_path)
        storagePath = "sakelabels/" + filename
        storage.child(storagePath).put(img_path)
        storageurl = storage.child(storagePath).get_url(None)
        db.collection(u'labels').document().set({
            u'createdAt': datetime.now(),
            u'filename': filename,
            u'storageurl': storageurl,
        })
    return render_template('uploads.html')


@app.route('/uploadpreview', methods=['GET', 'POST'])
def uploadpreview():
    if request.method == 'POST':
        img_path = latestImgPath.pop()
        img_filename = imageFileName.pop()

        with io.open(img_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.types.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        visionApiText = []
        pureText = []
        for text in texts:
            visionApiText.append('\n"{}"'.format(text.description))
            pureText.append(text.description)
        return render_template('uploadpreview.html', visionApiText=visionApiText, img_path=img_path, img_filename=img_filename, text=pureText)


class SakeSearchForm(Form):
    choices = ['Sake Name', 'Maker', 'Region']
    select = SelectField('Search for Sake:', choices=[
                         (choice, choice) for choice in choices])
    search = StringField('')


class SignUpForm(Form):
    firstname = TextField('Firstname:', validators=[validators.required()])
    lastname = TextField(':Lastname:', validators=[validators.required()])
    usertype = SelectField('Usertype:', choices=[],
                           validators=[validators.required()])
    email = StringField("Email:",  validators=[
                        validators.required("Please enter your email address.")])
    password = PasswordField("Password:", validators=[
                             validators.DataRequired()])


def write_user_log(firstname, lastname, usertype, email, password):
    user = auth.create_user_with_email_and_password(email, password)
    auth.send_email_verification(user['idToken'])
    db.collection(u'users').document(firstname).set({
        u'createdAt': datetime.now(),
        u'firstname': firstname,
        u'lastname': lastname,
        u'usertype': usertype,
        u'email': email,
    })


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)
    usertypes = ['Sake Consumer', 'Sake Buyer', 'Sake Maker', 'Others']
    form.usertype.choices = [(type, type) for type in usertypes]

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        usertype = request.form['usertype']
        email = request.form['email']
        password = request.form['password']

        if form.validate():
            write_user_log(firstname, lastname, usertype, email, password)
            form = SakeSearchForm(request.form)
            flash('Hello: {} {}'.format(firstname, lastname))
            return render_template('home.html', form=form)

        else:
            flash('Error: All Fields are Required')

    return render_template('signup.html', form=form)


class AddSakeForm(Form):
    name = TextField('Sake Brandname:', validators=[validators.required()])
    saketype = SelectField('Sake Type:', choices=[])
    taste = TextField('taste:', validators=[validators.required()])
    description = TextAreaField('Description:', validators=[
                                validators.required()])


def add_sake_to_db(name, saketype, taste, description):
    db.collection(u'sakes').document(name).set({
        u'createdAt': datetime.now(),
        u'id': str(uuid.uuid4()),
        u'name': name,
        u'name_ja': '',
        u'type': saketype,
        u'type_ja': '',
        u'is_fruity': False,
        u'taste': taste,
        u'maker': '',
        u'maker_ja': '',
        u'region': '',
        u'region_ja': '',
        u'url': '',
        u'description': description,
        u'description_ja': '',
        u'image': '',
    })


@app.route("/addSake", methods=['GET', 'POST'])
def addsake():
    form = AddSakeForm(request.form)
    types = ['Junmai Daiginjo', 'Daiginjo',
             'Junmai Ginjo', 'Ginjo', 'Junmai', 'Others']
    form.saketype.choices = [(type, type) for type in types]

    if request.method == 'POST':
        name = request.form['name']
        saketype = request.form['saketype']
        taste = request.form['taste']
        description = request.form['description']

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
    db.collection(u'feedbacks').document(title).set({
        u'createdAt': datetime.now(),
        u'title': title,
        u'feedback': feedback,
    })


@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm(request.form)

    if request.method == 'POST':
        title = request.form['title']
        feedback = request.form['feedback']

        if form.validate():
            write_to_feedback(title, feedback)
            flash('Thank you for your feedback!')

        else:
            flash('Error: All Fields are Required')

    return render_template('feedback.html', form=form)


class AddMakerForm(Form):
    maker = TextField('Maker:', validators=[validators.required()])
    region = SelectField('Region:', choices=[])
    url = TextField('Url:', validators=[validators.url(
        require_tld=True, message="Invalid URL")])


def write_to_makerlist(maker, region, url):
    db.collection(u'makers').document(maker).set({
        u'createdAt': datetime.now(),
        u'maker': maker,
        u'region': region,
        u'url': url,
    })


@app.route("/addMaker", methods=['GET', 'POST'])
def addmaker():
    form = AddMakerForm(request.form)
    regions = ['Tokyo', 'Osaka', 'Hokkaido', 'Fukuoka', 'Niigata', 'Fukui']
    form.region.choices = [(region, region) for region in regions]

    if request.method == 'POST':
        maker = request.form['maker']
        region = request.form['region']
        url = request.form['url']

        if form.validate():
            write_to_makerlist(maker, region, url)
            flash('Thank you for the information!')

        else:
            flash('Error: All Fields are Required')

    return render_template('addMaker.html', form=form)


# API
@app.route('/api/sakes', methods=['GET'])
def get_sakes():
    sakes_ref = db.collection(u'sakes')
    docs = sakes_ref.get()
    result = []
    for doc in docs:
        result.append({
            'name': doc.id,
            'else': doc.to_dict(),
        })

    return jsonify({'Sakes': result})


@app.route('/api/sake/<string:id>', methods=['GET'])
def get_sake(id):
    sakes_ref = db.collection(u'sakes')
    docs = sakes_ref.get()
    sake = [doc.to_dict() for doc in docs if doc.id == id]
    if len(sake) == 0:
        abort(404)
    return jsonify({'sake': sake[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/sake/<string:id>/")
def sake(id):
    sakes_ref = db.collection(u'sakes')
    docs = sakes_ref.get()
    for doc in docs:
        if doc.id == id:
            return render_template("sake.html", doc=doc)


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
    sakes_ref = db.collection(u'sakes')
    docs = sakes_ref.get()

    return render_template("sakelist.html", docs=docs)


if __name__ == '__main__':
    app.run()
