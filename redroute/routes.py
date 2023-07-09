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
from . import app, db, mail, cache, limiter
from sqlalchemy import func


otp = randint(100000,999999)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email.lower()).first()
        if user and user.confirmed == False:
            try:
                flash('Please verify your email first. Check spam and other folders if not found in inbox.')
                msg = Message("RedRoute Email Verification", sender="admin@redr.site", recipients=[email])
                msg.html = render_template('otp.html', otp=str(otp), username=user.username)
                mail.send(msg)
            except Exception as e:
                print(e)
                flash ("Verification failed. Please try again.")
                return redirect(url_for('signup'))
            return redirect(url_for('validate', email=email.lower()))
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
                msg = Message("RedRoute Email Verification", sender="admin@redr.site", recipients=[email])
                msg.html = render_template('otp.html', otp=str(otp), username=username)
                mail.send(msg)
            except Exception as e:
                print(e)
                flash ("Verification failed. Please try again.")
                return redirect(url_for('signup'))

            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Please check your mail inbox or spam for verification.')
            return redirect(url_for('validate', email=email.lower()))
    return render_template('signup.html')


def generate_qr_code(url):
    img = qrcode.make(url)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io


@app.route('/', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def home():
    if request.method == 'POST':
        long_url = request.form['long_url']
        custom_url = request.form['custom_url'] or None
        if custom_url:
            existing_url = Url.query.filter_by(custom_url=custom_url).first()
            if existing_url:
                flash ('That custom URL already exists. Please try another one!')
                return redirect(url_for('home'))
            short_url = custom_url
        elif long_url[:4] != 'http':
            long_url = 'http://' + long_url
        else:
            short_url = shortuuid.uuid()[:6]
        url = Url(long_url=long_url, short_url=short_url, custom_url=custom_url, user_id=current_user.id)
        db.session.add(url)
        db.session.commit()
        return redirect(url_for('dashboard'))

    urls = Url.query.order_by(Url.created_at.desc()).limit(10).all()
    return render_template('index.html', urls=urls)

@app.route("/dashboard")
@login_required
@cache.cached(timeout=50)
def dashboard():
    urls = Url.query.filter_by(user_id=current_user.id).order_by(Url.created_at.desc()).all()
    host = request.host_url
    return render_template('dashboard.html', urls=urls, host=host)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route('/<short_url>')
@cache.cached(timeout=50)
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
@cache.cached(timeout=50)
def url_analytics(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        return render_template('analytics.html', url=url)
    return 'URL not found.'

@app.route('/history')
@login_required
@cache.cached(timeout=50)
def link_history():
    urls = Url.query.filter_by(user_id=current_user.id).order_by(Url.created_at.desc()).all()
    host = request.host_url
    return render_template('history.html', urls=urls, host=host)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    url = Url.query.get_or_404(id)
    if url:
        db.session.delete(url)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return 'URL not found.'

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_url(id):
    url = Url.query.get_or_404(id)
    if url:
        if request.method == 'POST':
            custom_url = request.form['custom_url']
            if custom_url:
                existing_url = Url.query.filter_by(custom_url=custom_url).first()
                if existing_url:
                    flash ('That custom URL already exists. Please try another one.')
                    return redirect(url_for('edit_url', id=id))
                url.custom_url = custom_url
                url.short_url = custom_url
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template('edit.html', url=url)
    return 'URL not found.'


@app.route('/validate/<email>', methods=['GET', 'POST'])
def validate(email):
    user = User.query.filter_by(email=email).first()
    if user:
        if request.method == 'POST':
            user_otp = request.form['otp']
            if not user_otp:
                flash('Please enter OTP.')
                return redirect(url_for('validate', email=email))
            if int(user_otp) == otp:
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
            msg = Message('Email Verification', sender="admin@redr.site", recipients=[email])
            msg.html = render_template('otp.html', otp=str(otp))
            mail.send(msg)
        except:
            flash ("Verification failed. Please try again.")
            return redirect(url_for('signup'))
        flash('OTP sent successfully. Please check your mail inbox or spam.')
        return redirect(url_for('validate', email=email))
    return 'Email not found.'

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email.lower()).first()
        link = request.host_url + "reset_password/" + email
        if user:
            try:
                msg = Message('Reset Password', sender="admin@redr.site", recipients=[email])
                msg.html = render_template('reset_mail.html', link=link)
                mail.send(msg)
            except:
                flash ("Reset password failed. Please try again.")
                return redirect(url_for('login'))
            flash('Reset password link sent successfully. Please check your mail inbox or spam.')
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

#Check number of users and links created
@app.route('/stats')
def stats():
    users = User.query.count()
    links = Url.query.count()
    clicks = Url.query.with_entities(func.sum(Url.clicks)).scalar()

    return render_template('stats.html', users=users, links=links, clicks=clicks)
