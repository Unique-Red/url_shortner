from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_share import Share
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from .models import User, Url
import qrcode
import io
import shortuuid
from . import app, db, mail


otp = randint(100000,999999)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Password incorrect. Please try again.')
        else:
            flash('Email is not registered yet.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            flash('Email already exists.')
        elif len(username) < 2:
            flash('Username must be greater than 1 character.')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.')
        elif password != confirm_password:
            flash('Passwords don\'t match.')
        else:
            new_user = User(email=email.lower(), username=username, password=generate_password_hash(password, method='sha256'))

            try:
                msg = Message("Email Verification", sender="noah13victor@gmail.com", recipients=[email])
                msg.html = render_template('otp.html', otp=str(otp))
                mail.send(msg)
            except Exception as e:
                print(e)
                flash ("Verification failed. Please try again.")
                return redirect(url_for('signup'))

            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Please check your email for verification.')
            return redirect(url_for('validate', email=email.lower()))
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
                flash ('That custom URL already exists. Please try another one.')
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

@app.route('/delete/<short_url>')
@login_required
def delete_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        db.session.delete(url)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return 'URL not found.'

@app.route('/edit/<short_url>', methods=['GET', 'POST'])
@login_required
def edit_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        if request.method == 'POST':
            long_url = request.form['long_url']
            custom_url = request.form['custom_url']
            if custom_url:
                existing_url = Url.query.filter_by(custom_url=custom_url).first()
                if existing_url:
                    flash ('That custom URL already exists. Please try another one.')
                url.custom_url = custom_url
            elif long_url[:4] != 'http':
                long_url = 'http://' + long_url
            url.long_url = long_url
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template('edit.html', url=url)
    return 'URL not found.'


@app.route('/validate/<email>', methods=['GET', 'POST'])
def validate(email):
    user = User.query.filter_by(email=email).first()
    if user:
        if request.method == 'POST':
            otp = request.form['otp']
            if not otp:
                flash('Please enter OTP.')
                return redirect(url_for('validate', email=email))
            if otp == str(otp):
                user.confirmed = True
                db.session.commit()
                flash('Email verified successfully.')
                return redirect(url_for('login'))
            flash('Invalid OTP.')
            return redirect(url_for('validate', email=email))
        return render_template('validate.html', email=email)
    return 'Email not found.'


@app.route('/resend/<email>')
def resend(email):
    user = User.query.filter_by(email=email).first()
    if user:
        try:
            msg = Message('Email Verification', sender="noah13victor@gmail.com", recipients=[email])
            msg.html = render_template('otp.html', otp=str(otp))
            mail.send(msg)
        except:
            flash ("Verification failed. Please try again.")
            return redirect(url_for('signup'))
        flash('OTP sent successfully. Please check your email.')
        return redirect(url_for('validate', email=email))
    return 'Email not found.'

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            try:
                msg = Message('Reset Password', sender="noah13victor@gmail.com", recipients=[email])
                msg.html = render_template('reset_password.html', email=email)
                mail.send(msg)
            except:
                flash ("Reset password failed. Please try again.")
                return redirect(url_for('login'))
            flash('Reset password link sent successfully. Please check your email.')
            return redirect(url_for('login'))
        flash('Email not found.')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    user = User.query.filter_by(email=email).first()
    if user:
        if request.method == 'POST':
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            if password == confirm_password:
                user.password = generate_password_hash(password, method='sha256')
                db.session.commit()
                flash('Password reset successfully. Please login.')
                return redirect(url_for('login'))
            else:
                flash('Passwords do not match. Please try again.')
                return redirect(url_for('reset_password', email=email))
        return render_template('reset_password.html', email=email)
    return 'Email not found.'