from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager,login_user,logout_user,current_user, login_required
from pymongo import message
from user import User
from datetime import datetime
from dateutil.tz import gettz
from db import chat_history, get_user, new_msg, new_user, get_allusers,get_chats

app = Flask(__name__)
app.secret_key='secret key'
login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)

current_chat=''
chats=[]
@app.route('/', methods=['GET','POST'])
def login():
    message=""
    if current_user.is_authenticated:
        return redirect(url_for('chat',user=current_user.username))
    if request.method =='POST':
        username =request.form.get('username')
        input_password =request.form.get('password')
        user = get_user(username)
        if user and user.check_password(input_password):
            login_user(user)
            return redirect(url_for('chat',user=user.username))
        else:
            message="User credentials are incorrect"
    return render_template("login.html",message=message)

@app.route('/signup', methods=['GET','POST'])
def signup():
    message=""
    if request.method =='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        if username.isalnum()==False:
            message="You can only use alphanumeric characters in username"
        else:    
            try:
                new_user(username,email,password)
                return redirect(url_for('login'))
            except:
                message="User already exists"
    return render_template("signup.html",message=message)

@app.route('/chat/<user>', methods=['GET','POST'])
@login_required
def chat(user):
    global chats
    user_chats=get_chats(user)
    global current_chat
    date=[]
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%d"))
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%b"))
    date.append(datetime.now(tz=gettz('Asia/Kolkata')).strftime("%y"))
    if current_user.username!=user:
        return redirect(url_for('chat',user=current_user.username))
    if request.method =='POST' :
        try:
            request.form['action']
            if request.form['action']=='logout':
                logout_user()
                current_chat=''
                return redirect(url_for('login'))
            elif request.form['action']:
                current_chat=request.form['action']
                chats = chat_history(user,current_chat)
        except:
            try:
                request.form['sent-msg']
                msg=request.form['sent-msg']
                new_msg(user,current_chat,msg)
                chats=chat_history(user,current_chat) 
                user_chats=get_chats(user) 
            except:
                current_chat=request.form['action1']
                chats=chat_history(user,current_chat)
    return render_template("chat.html",users_name=get_allusers(),var=user,current_chat=current_chat,chats=chats,user_chats=user_chats,curr_date=date)

@login_manager.user_loader
def load_user(username): 
    return get_user(username)

if __name__=="__main__":
    app.run(debug=True)