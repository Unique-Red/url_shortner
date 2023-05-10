from flask import Flask, render_template, request, redirect, url_for, flash
import random
import string
import qrcode
from datetime import datetime
from flask_caching import Cache

app = Flask(__name__)
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 3000})


link_history = {}
urls = {}

@app.route('/', methods=['GET','POST'])
@cache.cached(timeout=3000)
def home():
    if request.method == "POST":
        long_url = request.form['long_url']
        custom_url = request.form['custom_url']
        if long_url[:4] != 'http':
            long_url = 'http://' + long_url
        elif custom_url in cache:
            flash ('Custom URL already exists', category='error')
        elif not custom_url:
            custom_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        elif len(custom_url) < 6:
            flash ('Custom URL must be at least 6 characters long', category='error')
        short_url = custom_url
        


        with cache:
            cache.set(short_url, long_url)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(short_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save('static/' + custom_url + '.png')

        return redirect (url_for('short_url', short_url=short_url))

    return render_template('index.html')

@app.route('/short_url/<string:short_url>')
def short_url(short_url):
    return render_template('short_url.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_to_url(short_url):
    url = cache.get(short_url)
    if url:
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        if short_url in link_history:
            link_history[short_url].append(date_time)
        else:
            link_history[short_url] = [date_time]
        return redirect(url)
    else:
        return render_template('404.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html', link_history=link_history)

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