from flask import Flask, redirect, url_for, render_template, request, send_file
import pymongo
from pymongo import MongoClient
from PIL import Image
import pytesseract
import requests
import urllib.request
from bson.objectid import ObjectId
import os


connection_string = os.environ.get('Mongo_connect')

client = MongoClient(connection_string)
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


@app.route('/download/<img_id>')
def download_img(img_id):
    img_collection = db['image']
    query = {'_id': ObjectId(img_id)}
    if img_collection.count_documents(query) != 0:
        query_result = img_collection.find_one(query)
        path = './download.png'
        urllib.request.urlretrieve(query_result['url'], path)

        return send_file(path, as_attachment=True)
    else:
        return 'File not found!'


if __name__ == '__main__':
    app.run(debug=True)
