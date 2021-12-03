from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from user import User
from datetime import datetime
from dateutil.tz import gettz
import os

URL = os.environ.get('url') 
client = MongoClient(URL)
db = client.get_database('Chat')
users=db.get_collection('users')
chats=client.get_database('conversations')

def get_allusers():
    usernames=[]
    for i in users.find():
        usernames.append(i['_id'])
    usernames = sorted(usernames, key=str.casefold)
    return usernames

def new_user(username,email,password):
    password=generate_password_hash(password)
    if users.find_one({'email':email})==None:
        users.insert_one({'_id':username, 'email':email,'password':password})
    else:
        raise ValueError("User already exists")

def get_user(username):
    user_data= users.find_one({'_id':username})
    if user_data==None:
        user_data =users.find_one({'email':username})
    if user_data==None:
        return None
    return User(user_data['_id'],user_data['email'],user_data['password'])

def new_msg(sender,receiver,msg):
    time=datetime.now(tz=gettz('Asia/Kolkata')).strftime("%I:%M %p")
    date=datetime.now(tz=gettz('Asia/Kolkata')).strftime("%d %b")
    year=datetime.now(tz=gettz('Asia/Kolkata')).strftime("%y")
    if sender<receiver:
        index=sender+"-"+receiver
    else:
        index=receiver+'-'+sender
    chats[index].insert_one({'sender':sender,'reciever':receiver,'message':msg,'time':time,'date':date,'year':year})

def chat_history(sender,receiver):
    if sender<receiver:
        index=sender+"-"+receiver
    else:
        index=receiver+'-'+sender
    chat_data=chats[index].find()
    msgs=[]
    for i in chat_data:
        msgs.append([i['sender'],i['message'],i['time'],i['date'],i['year']])
    msgs.reverse()
    return msgs 

def get_chats(curr_user):
    allchats=chats.list_collection_names()
    userchats=[]
    for i in allchats:
        names=i.split('-')
        other_user=''
        if names[0]==curr_user:
            other_user= names[1]
        elif names[1]==curr_user:
            other_user= names[0]
        if other_user!='':
            for j in chats[i].find().limit(1).sort([('$natural',-1)]):
                userchats.append([other_user,j['message'],j['time'],j['date'],j['year']])
    months={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}        
    tmpchats=[]
    for i in userchats:
        a=1
        if i[2].split()[1]=='AM':
            a=0
        tmpchats.append([i[4],months[i[3].split()[1]],i[3].split()[0],a,i[2].split()[0].split(':')[0],i[2].split()[0].split(':')[1],i[1],i[0]])
    userchats=[]
    tmpchats.sort(reverse=True)
    months={1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}  
    for i in tmpchats:
        a='PM'
        if i[3]==0:
            a='AM'
        userchats.append([i[7],i[6],i[4]+':'+i[5]+' '+a,i[2],months[i[1]],i[0]])
    return userchats