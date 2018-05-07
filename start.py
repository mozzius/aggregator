#!/usr/bin/env python3
from flask import Flask, render_template, url_for, redirect, session, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
import hashlib
import db

app = Flask(__name__)
login = LoginManager(app)

def sha256(msg):
    return hashlib.sha256(msg.encode('utf-8')).digest()

class User(UserMixin):
    def __init__(self,name,id,active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        return self.active

    @staticmethod
    def validate_login(pw_hash, password):
        return pw_hash == sha256(password)

@login.user_loader
def loadUser(userid):
    user = db.getUser(userid,'_id')
    if user:
        return User(userid)
    else:
        return None

@app.route('/')
@app.route('/r/<subname>')
@app.route('/r/<subname>/<sort>')
def sub(subname='frontpage',sort='hot'):
    page = db.getSub(subname)
    posts = db.getPosts(subname,sort)
    newposts = posts
    for i in range(len(posts)):
        newposts[i]['user_name'] = db.getUser(posts[i]['user_id'],'_id')['name']
    return render_template('roddit.html',page=page,posts=posts,type='sub')

@app.route('/r/<subname>/submit',methods=['GET','POST'])
@login_required
def submit(subname):
    page = db.getSub(subname)
    if request.method == 'POST':
        post = request.form
        fail = db.addPost(post)
        if fail:
            return render_template('roddit.html',page=page,type='submit',fail=True)
    else:
        return render_template('roddit.html',page=page,type='submit',fail=False)

@app.route('/createsub',methods=['GET','POST'])
@login_required
def createsub():
    page = db.getSub(subname)
    if request.method == 'POST':
        sub = request.form
        fail = db.createSub(sub)
        if fail:
            return render_template('roddit.html',page=page,type='makesub',fail=True)
        else:
            return redirect('/'+sub['sub'])
    else:
        return render_template('roddit.html',page=page,type='makesub',fail=False)

@login.unauthorized_handler
def unauthHandler():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        form = request.form
        if db.verifyUser(form['email'],form['password']):
            user = db.getUser(form['email'],'email')
            session['loggedin'] = True
            session['name'] = user['name']
            session['email'] = user['email']
            return redirect('/')
        else:
            return render_template('roddit.html',type='login',fail=True)
    else:
        if 'loggedin' in session and session['loggedin'] == True:
            return redirect('/')
        else:
            return render_template('roddit.html',type='login',fail=False)

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        form = request.form
        if db.addUser(form['username'],form['email'],form['password']):
            session['loggedin'] = True
            session['name'] = form['name']
            session['email'] = form['email']
            return redirect('/')
        else:
            return render_template('roddit.html',type='signup',fail=True)
    else:
        if 'loggedin' in session and session['loggedin'] == True:
            return redirect('/')
        else:
            return render_template('roddit.html',type='signup',fail=False)

@app.route('/logout')
def logout():
    session['loggedin'] = False
    session['name'] = ''
    session['email'] = ''
    return redirect('/')

@app.route('/u/<user>')
def user(user):
    user = db.getUser(user)
    posts = []
    if user:
        posts = db.getUserPosts(user['_id'])
    return render_template('roddit.html',page=user,posts=posts,type='user')

if __name__ == '__main__':
    app.secret_key = 'localhost'
    app.run(port=80,debug=True,host='0.0.0.0')