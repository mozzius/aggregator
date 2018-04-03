from flask import Flask, render_template, url_for, redirect, session, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import hashlib
import db

app = Flask(__name__)
login = LoginManager(app)

def sha256(msg):
    return hashlib.sha256(msg).digest()

class User():
    def __init__(self,username):
        self.username = username
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

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
    if sort == 'hot':
        posts = db.hot(subname)
    elif sort == 'new':
        posts = db.new(subname)
    elif sort == 'top':
        posts = db.top(subname)
    elif sort == 'top':
        posts = db.top(subname)
    elif sort == 'controversial':
        posts = db.controversial(subname)
    else:
        posts = False
    return render_template('roddit.html',page=page,posts=posts,type='sub',user={'name':'mozzius'})

@app.route('/r/<subname>/submit')
@login_required
def submit(subname,methods=['GET','POST']):
    page = db.getSub(subname)
    if request.method == 'POST':
        post = request.form
        fail = db.addPost(post)
        if fail:
            return render_template('roddit.html',page=page,type='submit',fail=True)
    else:
        return render_template('roddit.html',page=page,type='submit',fail=False)

@login.unauthorized_handler
def unauthHandler():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        form = request.form
        if db.checkLogin(form['email'],form['password']):
            session['loggedin'] = True
            session['name'] = db.user['name']
            session['email'] = db.user['email']
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
    # doesn't work in the slightest
    if request.method == 'POST':
        form = request.form
        success = db.addUser(form)
        if success:
            session['loggedin'] = True
            session['name'] = db.user['name']
            session['email'] = db.user['email']
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
    flask_login.logout_user()
    return redirect('/')

@app.route('/u/<user>')
def user(user):
    user = db.getUser(user)
    posts = []
    if user:
        posts = db.getUserPosts(user['_id'])
    return render_template('roddit.html',page=user,posts=posts,type='user')

if __name__ == '__main__':
    app.run(port=80,debug=True,host='0.0.0.0')