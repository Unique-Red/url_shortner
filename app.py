from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import shortuuid
import qrcode
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

# @app.before_first_request
# def create_tables():
#     db.create_all()

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
                return render_template('home.html', error='Custom URL already taken.')
            short_url = custom_url
        else:
            short_url = shortuuid.uuid()[:6]
        url = Url(long_url=long_url, short_url=short_url, custom_url=custom_url)
        db.session.add(url)
        db.session.commit()
        return redirect('/')

    urls = Url.query.order_by(Url.created_at.desc()).limit(10).all()
    return render_template('index.html', urls=urls)

@app.route('/<short_url>')
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
def url_analytics(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        return render_template('analytics.html', url=url)
    return 'URL not found.'

@app.route('/history')
def link_history():
    urls = Url.query.order_by(Url.created_at.desc()).all()
    return render_template('history.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)


# from flask import Flask, render_template, request, redirect, url_for, flash
# import random
# import string

# app = Flask(__name__)

# urls = {}

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         url = request.form['url']
#         if url[:4] != 'http':
#             url = 'http://' + url
#         short_url = generate_short_url()
#         urls[short_url] = url
#         return redirect (url_for('url', short_url=short_url))
#     return render_template('home.html')

# @app.route('/url/<string:short_url>')
# def url(short_url):
#     return render_template('url.html', short_url=short_url)

# @app.route('/<string:short_url>')
# def redirect_to_url(short_url):
#     original_url = urls.get(short_url)
#     if original_url:
#         return redirect(original_url)
#     else:
#         flash('That short URL does not exist!')
#         return redirect(url_for('home'))
    
# def generate_short_url():
#     characters = string.digits + string.ascii_letters
#     while True:
#         short_url = ''.join(random.choices(characters, k=3))
#         if short_url not in urls:
#             return short_url
#         elif len(urls) == len(characters) ** 3:
#             raise Exception("Cannot generate a short URL")
#         else:
#             return short_url
        
# if __name__ == '__main__':
#     app.run(debug=True)