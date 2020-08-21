from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://shaikhmudassir:asma19131pawmysql@shaikhmudassir.mysql.pythonanywhere-services.com/shaikhmudassir$default'
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = app.root_path + '/static/img/'
app.secret_key = 'silent'
db = SQLAlchemy(app)

class Login(db.Model):
  Id = db.Column(db.Integer,primary_key=True)
  username = db.Column(db.String(100),unique=False,nullable=False)
  password = db.Column(db.String(100),unique=False,nullable=False)

class Contact(db.Model):
  Id = db.Column(db.Integer,primary_key=True)
  sender = db.Column(db.String(100),unique=False,nullable=False)
  reciver = db.Column(db.String(100),unique=False,nullable=False)


class Message(db.Model):
  Id = db.Column(db.Integer,primary_key=True)
  sender = db.Column(db.String(100),unique=False,nullable=False)
  msg = db.Column(db.String(100),unique=False,nullable=False)
  reciver = db.Column(db.String(100),unique=False,nullable=False)
  dateTime = db.Column(db.String(100),unique=False,nullable=False)


@app.route('/', methods=['GET','POST'])
def index():
  if 'user_session' in session:
    pass
  else:
    return redirect('/login')
  print(os.path.isdir(app.config['UPLOAD_FOLDER']))
  print(app.root_path)
  if request.method == 'POST':
    newFriend = request.form.get('newFriend').lower().strip()

    select = Contact.query.filter_by(sender=session['user_session'],reciver=newFriend).first()
    if select != None or newFriend == session['user_session']:
      errorMsg = newFriend + ' is already in your contact list.'
      return render_template('error.html',errorMsg=errorMsg)#('<h1>Error</h1>')

    select = Login.query.filter_by(username=newFriend).first()
    if select == None:
      errorMsg = 'No user available. Kindly check your friends username.'
      return render_template('error.html',errorMsg=errorMsg)#('<h1>Error</h1>')

    entry = Contact(
      sender=session['user_session'],
      reciver=newFriend
    )
    entry1 = Contact(
      sender=newFriend,
      reciver=session['user_session']
    )

    db.session.add(entry)
    db.session.add(entry1)
    db.session.commit()

  checkImg = os.path.isfile('./static/img/' + session['user_session'] + '.jpg')
  select = Contact.query.filter_by(sender=session['user_session']).all()
  if not checkImg:
    return render_template('contact.html',select=select,user=session['user_session'],checkImg=checkImg)

  return render_template('contact.html',select=select,user=session['user_session'])


@app.route('/<string:sender>-<string:reciver>', methods=['GET','POST'])
def chat(sender,reciver):
  if 'user_session' in session:
    pass
  else:
    return redirect('/login')

  if request.method == 'POST':
    msg = request.form.get('msg')

    DateTime = datetime.now().strftime("%d.%m.%y %H:%M")
    entry = Message(
      sender=session['user_session'],
      msg=msg,
      reciver=reciver,
      dateTime=DateTime
    )
    db.session.add(entry)
    db.session.commit()

  select = Contact.query.filter_by(sender=session['user_session']).all()
  selectMsg = Message.query.filter(
    sender==session['user_session'] or sender==reciver,
    reciver==reciver or reciver==session['user_session'],
  ).all()

  return render_template(
    'chat.html',
    select=select,
    selectMsg=selectMsg,
    sender=sender,
    reciver=reciver
  )


@app.route('/@<string:sender>-<string:reciver>')
def dataProvider(sender,reciver):
  selectMsg = Message.query.filter(
    sender==session['user_session'] or sender==reciver,
    reciver==reciver or reciver==session['user_session'],
  ).all()
  senderD = []
  msgD = []
  reciverD = []
  dateTimeD = []
  jsonP = {}
  for n in selectMsg:
    if n.reciver in [sender,reciver] and n.sender in [sender,reciver]:
      senderD.append(n.sender)
      msgD.append(n.msg)
      reciverD.append(n.reciver)
      dateTimeD.append(n.dateTime)
  jsonP['sender'] = senderD
  jsonP['msg'] = msgD
  jsonP['reciver'] = reciverD
  jsonP['dateTime'] = dateTimeD
  return json.dumps(jsonP)


@app.route('/<string:sender>',methods=['GET','POST'])
def edit(sender):
  if 'user_session' in session:
    pass
  else:
    return redirect('/login')

  if request.method == 'POST':
    fileImg = request.files['fileImg']
    fileImg.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(session['user_session']+'.jpg')))
    select = Login.query.filter_by(username=session['user_session']).first()
    return render_template("edit.html",user=select)

  select = Login.query.filter_by(username=session['user_session']).first()
  return render_template("edit.html",user=select)

@app.route('/view-<string:reciver>')
def view(reciver):
  select = Login.query.filter_by(username=reciver).first()
  return render_template("view.html",user=select)


@app.route('/login',methods=['GET','POST'])
def login():
  return render_template('login.html')


@app.route('/login/<string:var>',methods=['GET','POST'])
def loginCheck(var):

  if var == '0':
    if request.method == 'POST':
      username = request.form.get('username').lower().strip()
      password = request.form.get('password')
      confirmPassword = request.form.get('confirmPassword')

      if password != confirmPassword:
        errorMsg = 'Confirm Password is not match.'
        return render_template('error.html',errorMsg=errorMsg)#('<h1>Error</h1>')

      # Unique username
      select = Login.query.filter_by(username=username).first()

      if select != None:
          errorMsg = 'Username is already exist.'
          return render_template('error.html',errorMsg=errorMsg)#('<h1>Error</h1>')

      if select != None and not check_password_hash(select.password, password):
        errorMsg = 'Username is already exist.'
        return render_template('error.html',errorMsg=errorMsg)#('<h1>Error</h1>')

      entry = Login(
        username = username,
        password = generate_password_hash(password),
      )

      db.session.add(entry)
      db.session.commit()

      session['user_session'] = username
      return redirect('/')

  else:

    if request.method == 'POST':
      username = request.form.get('username').lower().strip()
      password = request.form.get('password')
      select = Login.query.filter_by(username=username).first()

      if select == None or not check_password_hash(select.password, password):
        errorMsg = 'Username or password is wrong.'
        return render_template('error.html',errorMsg=errorMsg)#('<h1>Error</h1>')


      session['user_session'] = select.username
      return redirect('/')

  return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_session')
    return redirect('/login')


@app.route('/error')
def error():
    return redirect('/login')





