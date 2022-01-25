from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager,login_user,logout_user,current_user, login_required
from pymongo import message
from user import User
from datetime import datetime
from dateutil.tz import gettz
from flask_socketio import SocketIO, join_room, close_room
from db import chat_history, get_user, new_msg, new_user, get_allusers,get_chats
import os

app = Flask(__name__)
socketio = SocketIO(app,transports= ['websocket'])
app.secret_key='secret key'
login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)

@app.route('/', methods=['POST'])
def login():
    message=""
    if current_user.is_authenticated:
        return redirect(url_for('chat', user=current_user.username))
    if request.method == 'POST':
        username =request.form.get('username')
        input_password =request.form.get('password')
        user = get_user(username)
        if user and user.check_password(input_password):
            login_user(user)
            return redirect(url_for('chat', user=user.username))
        else:
            message="User credentials are incorrect"
    return render_template("login.html", message=message)

@app.route('/signup', methods=['POST'])
def signup():
    message=""
    if request.method == 'POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        if username.isalnum() == False:
            message="You can only use alphanumeric characters in username"
        else:    
            try:
                new_user(username,email,password)
                return redirect(url_for('login'))
            except:
                message="User already exists"
    return render_template("signup.html", message=message)

@app.route('/chat/<user>', methods=['POST'])
@login_required
def chat(user):
    user_chats=get_chats(user)
    date=[]
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%d"))
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%b"))
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%y"))
    if current_user.username!=user:
        return redirect(url_for('chat',user=current_user.username))
    if request.method =='POST' :
        logout_user()
        return redirect(url_for('login'))
    return render_template("chat.html", users_name=get_allusers(), var=user, user_chats=user_chats,
                           curr_date=date)

@login_manager.user_loader
def load_user(username): 
    return get_user(username)

@socketio.on('change chat')
def handle_my_custom_event(data):
    user=data['user']
    current_chat=data['new_chat']
    chats = chat_history(user,current_chat)
    socketio.emit('update chat', {'chats':chats, 'current_chat':current_chat}, room=user)

@socketio.on('sentmsg')
def handle_my_custom_event(data):
    user=data['user']
    current_chat=data['curr_chat']
    msg=data['msg']
    new_msg(user,current_chat,msg)
    chats = chat_history(user,current_chat)
    user_chats=get_chats(user) 
    socketio.emit('update chat', {'chats':chats, 'current_chat':current_chat}, room=user)
    date=[]
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%d"))
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%b"))
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%y"))
    socketio.emit('update allchats', {'user_chats':user_chats, 'date':date})

@socketio.on('init')
def handle_my_custom_event(data):
    user=data
    user_chats=get_chats(user)
    date=[]
    join_room(user)
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%d"))
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%b"))
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%y"))
    socketio.emit('update allchats', {'user_chats':user_chats,'date':date}, room=user)

@socketio.on('logout')
def handle_my_custom_event(data):
    user = data
    socketio.emit('submit form', room=user)
    close_room(user)

if __name__=="__main__":
    socketio.run(app, port=int(os.environ.get('PORT', 5000)))
