from flask import Flask, render_template, request, redirect, url_for, session
from flask.helpers import flash
from pymongo import MongoClient
from hashlib import sha256

app = Flask(__name__)
app.secret_key = b'\x8a\xf2N8\xd9\xa8\x06\xbc\x1b.\x87\xff\xa1S\x9f\xa6'

client = MongoClient('localhost', 27017)
db = client.auth_db


@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        password = request.form.get('password')
        password_retry = request.form.get('password-retry')
        username = request.form.get('username')
        
        if db.users.find_one({'username': username}) == None: 
            if password == password_retry:

                user = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': hash_password(password)
                }

                db.users.insert(user)
                session['username'] = user['username']

                return redirect(url_for('cabinet'))
            else:
                return redirect(url_for('register'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        user = find_user(username)
        if user != None:
            if check_password(user['username'], password):
                session['username'] = user['username']
                return redirect(url_for('cabinet'))
            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for('register'))

@app.route('/logout/', methods = ['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/cabinet/', methods = ['GET'])
def cabinet():
    if 'username' in session:
        user = find_user(session['username'])
        return render_template('cabinet.html', user=user)
    else:
        return redirect(url_for('register'))

def find_user(username):
    return db.users.find_one({'username': username})

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def check_password(username, password):
    hash = sha256(password.encode()).hexdigest()
    db_hash = db.users.find_one({'username': username})['password']
    return hash == db_hash

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)