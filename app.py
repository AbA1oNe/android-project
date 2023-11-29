from flask import request, url_for, redirect, send_from_directory, make_response, send_file
from flask_login import login_user, logout_user
from flask_login import current_user
from initiate import app, db
from initiate.login_models import User
import json
import base64


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
#@login_required
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
#@login_required
def receiveData():
    #username = current_user.username
    if (request.is_json):
        data = request.get_json()
        username = data['account']
        with open('./temp.json', 'r+') as file:
            fileData = json.load(file)
            data['value']["label"] = 0
            if (username in fileData):
                fileData[username].append(data['value'])
                file.seek(0)
                json.dump(fileData, file, indent=2)
            else:
                fileData[username] = []
                fileData[username].append(data['value'])
                file.seek(0)
                json.dump(fileData, file, indent=2)
            print(f"User {username} sends {data['value']}")
            return f"User {username} sends {data['value']}"
        
    return "receive failed"

@app.route('/send-model', methods=['POST'])
def sendModel():
    try:
        username = request.form.get('username')
        with open('data.json', 'r') as jsonFile:
            data = json.load(jsonFile)
            i=0
            filename = ""
            for user in data: 
                if username == user:
                    filename = f'model{i}.onnx'
                    break
                i+=1
              
            #res = send_from_directory("C:\\Users\\louis\\OneDrive\\桌面\\11\\android-project\\models", filename)
            res = send_from_directory("C:\\Main\\Code\\ml-app\\models\\SMOTERF-newData", filename)
            print(f"{filename} sends to {username}")
            return res
                    
    except Exception as e:
        print(f"send model failed {e}")
        return f"send model failed {e}"
    
@app.route('/recv-evaluation', methods=['POST'])
def receiveEvaluation():
    username = request.form.get('account')
    value = int(request.form.get('value'))
    with open('./evaluationData.json', 'r+') as file:
        fileData = json.load(file)

        if (username in fileData):
            if value == 1:
                fileData[username]["predict_1"] += 1
            elif value == 0:
                fileData[username]["predict_0"] += 1
                
            file.seek(0)
            json.dump(fileData, file, indent=2)
        else:
            fileData[username] = {"predict_0":0, "predict_1":0}
            if value == 1:
                fileData[username]["predict_1"] += 1
            elif value == 0:
                fileData[username]["predict_0"] += 1
            
            file.seek(0)
            json.dump(fileData, file, indent=2)
            
        print(f"User {username} evaluation sends {value}")
        return f"User {username} evaluation sends {value}"
        
    return "receive evaluation failed"

@app.route('/receiveSafty', methods=['POST'])
#@login_required
def receiveSafetyQuestion():
    username = request.form.get('username')
    quesiton1 = request.form.get('question1')
    ans1 = request.form.get('answer1')
    quesiton2 = request.form.get('question2')
    ans2 = request.form.get('answer2')

    with open('./safetyQuestion.json', 'r+', encoding='utf8') as file:
        fileData = json.load(file)
        fileData[username] = {}
        fileData[username]["question1"] = str(quesiton1)
        fileData[username]["answer1"] = str(ans1)
        fileData[username]["question2"] = str(quesiton2)
        fileData[username]["answer2"] = str(ans2)
        file.seek(0)
        json.dump(fileData, file, indent=2, ensure_ascii=False)

        return "receive safety question"
        
@app.route('/sendSafty', methods=['POST'])
#@login_required
def sendSafetyQuestion():
    username = request.form.get('username')
    
    with open('./safetyQuestion.json', 'r', encoding='utf8') as file:
        fileData = json.load(file)
        QAList = []
        QAList.append({fileData[username]["question1"]: fileData[username]["answer1"]})
        QAList.append({fileData[username]["question2"]: fileData[username]["answer2"]})
        return QAList
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',port=5000, debug=True) #192.168.1.103 or 0.0.0.0 will also work
    #port 80 in school because can't port forward 80 to 5000 port.
    #but in home it's okay to use default 5000 port because there's port forwarding.