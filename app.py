from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import shortuuid
import qrcode
import io
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500))
    short_url = db.Column(db.String(10), unique=True)
    custom_url = db.Column(db.String(50), unique=True)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return '<Url %r>' % self.short_url
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String)
    password = db.Column(db.String)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Password incorrect. Please try again.', 'danger')
        else:
            flash('Email does not exist.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            flash('Email already exists.', 'danger')
        elif len(username) < 2:
            flash('Username must be greater than 1 character.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        elif password != confirm_password:
            flash('Passwords don\'t match.', 'danger')
        else:
            new_user = User(email=email.lower(), username=username, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
    return render_template('signup.html')


def generate_qr_code(url):
    img = qrcode.make(url)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        long_url = request.form['long_url']
        custom_url = request.form['custom_url']
        if custom_url:
            existing_url = Url.query.filter_by(custom_url=custom_url).first()
            if existing_url:
                flash ('That custom URL already exists. Please try another one.', 'danger')
            short_url = custom_url
        elif long_url[:4] != 'http':
            long_url = 'http://' + long_url
        else:
            short_url = shortuuid.uuid()[:6]
        url = Url(long_url=long_url, short_url=short_url, custom_url=custom_url)
        db.session.add(url)
        db.session.commit()
        return redirect(url_for('dashboard'))

    urls = Url.query.order_by(Url.created_at.desc()).limit(10).all()
    return render_template('index.html', urls=urls)

@app.route("/dashboard")
@login_required
def dashboard():
    urls = Url.query.order_by(Url.created_at.desc()).all()
    return render_template('dashboard.html', urls=urls)

@app.route('/<short_url>')
@login_required
def redirect_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        url.clicks += 1
        db.session.commit()
        return redirect(url.long_url)
    return 'URL not found.'

@app.route('/qr_code/<short_url>')
def generate_qr_code_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        img_io = generate_qr_code(request.host_url + url.short_url)
        return img_io.getvalue(), 200, {'Content-Type': 'image/png'}
    return 'URL not found.'

@app.route('/analytics/<short_url>')
@login_required
def url_analytics(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        return render_template('analytics.html', url=url)
    return 'URL not found.'

@app.route('/history')
@login_required
def link_history():
    urls = Url.query.order_by(Url.created_at.desc()).all()
    return render_template('history.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)
