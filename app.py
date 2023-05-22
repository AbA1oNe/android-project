from flask import Flask, request, jsonify, url_for, redirect
from flask_login import login_user, logout_user, login_required
from flask_login import current_user
import numpy as np
import pickle
from initiate import app, db
from initiate.login_models import User
import json

model = pickle.load(open('model.pkl','rb'))

@app.route('/')
def index():
    return "Hello world"

@app.route('/login',methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None:
        redirect(url_for('register'))
        return f"no such username {username}"
    if user.check_password(password) and user is not None:
        login_user(user, remember=True)
        next = request.args.get('next')
        if next == None or not next[0]=='/':
            next = url_for('index')
    else:
        redirect(url_for('login'))
        return "wrong password"
    
    print(f"User {current_user.username} has logged in")
    return redirect(next)

@app.route('/logout',methods=['POST'])
@login_required
def logout():
    print(f'User {current_user.username} has logged out')
    logout_user()
    
    return redirect(url_for('index'))

@app.route('/register',methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if User.query.filter_by(username=username).count() < 1:
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
    else:
        redirect(url_for('register'))
        return f"username {username} already exist"
    
    print(f'User {username} registered')
    return redirect(url_for('index'))


@app.route('/receive', methods=['POST'])
@login_required
def receiveData():
    #username = current_user.username
    if (request.is_json):
        data = request.get_json()
        username = data['account']
        with open('./data.json', 'r+') as file:
            fileData = json.load(file)
            if (username in fileData):
                fileData[username].append(data['value'])
                file.seek(0)
                json.dump(fileData, file, indent=2)
            else:
                fileData[username] = []
                fileData[username].append(data['value'])
                file.seek(0)
                json.dump(fileData, file, indent=2)
    
    print(f"User {current_user.username} sends {data['value']}")
    return f"User {current_user.username} sends {data['value']}"
    #return redirect(url_for('index'))
    

@app.route('/predict',methods=['POST'])
def predict():
    cgpa = request.form.get('cgpa')
    iq = request.form.get('iq')
    profile_score = request.form.get('profile_score')

    input_query = np.array([[cgpa,iq,profile_score]], dtype=float)

    result = model.predict(input_query)[0]

    return jsonify({'placement':str(result)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)