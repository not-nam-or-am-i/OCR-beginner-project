from flask import Flask, redirect, url_for, render_template, request
import pymongo
from pymongo import MongoClient
from PIL import Image
import pytesseract
import requests


client = MongoClient('mongodb://admin:admin%40123@103.137.4.6:27017')
db = client['ORC']
col = db['user']
pytesseract.pytesseract.tesseract_cmd = r'D:/tesseract/tesseract.exe'

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html', content='Nam', r=2)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # input data
        username = request.form['id']
        password = request.form['password']
        # save data into db
        usr_collection = db['user']
        data = {'name': username, 'password': password}
        # check if username exists
        if usr_collection.count_documents({'name': username}) != 0:
            return 'This username is already existed'
        else:
            usr_collection.insert_one(data)
            return redirect(url_for('user', usr=username, password=password))
    else:
        return render_template('register.html')


@app.route('/<usr>, <password>')
def user(usr, password):
    return f'<h1> {usr} </h1> <p> {password} </p>'


# TODO: download img
@app.route('/orc', methods=['POST', 'GET'])
def orc():
    if request.method == 'POST':
        img_url = request.form['url']
        username = request.form['username']
        usr_collection = db['user']

        # check if username exists
        if usr_collection.count_documents({'name': username}) != 0:
            # get img from url
            img = Image.open(requests.get(img_url, stream=True).raw).convert('LA')
            # orc
            text = pytesseract.image_to_string(img)
            # save into db
            img_collection = db['image']
            data = {'user': username, 'url': img_url, 'text': text}
            img_collection.insert_one(data)

            return text
        else:
            return 'User not existed'
    else:
        return render_template('upload_img.html')


# TODO: download image
@app.route('/history/<username>')
def get_history(username):
    # query
    query = {'user': username}
    img_collection = db['image']
    if img_collection.count_documents(query) != 0:
        query_result = img_collection.find(query)
        return render_template('history.html', query_result=query_result, username=username)
    else:
        return f'History for user {username} is empty!'


if __name__ == '__main__':
    app.run(debug=True)
