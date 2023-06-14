# Project Description: RedRoute URL Shortener

The RedRoute URL Shortener project aims to develop a user-friendly and efficient URL shortening service. The application will allow users to convert long, complex URLs into shorter, more manageable ones. The project will utilize cutting-edge technologies to ensure fast and reliable redirection, while also providing additional features such as link analytics and QR code generation.

## Key Features:

1. URL Shortening: Users can input lengthy URLs and generate shortened versions that are easier to share and remember.

2. Customizable URLs: Users have the option to customize the shortened URLs to reflect their brand or preferred keywords, making them more recognizable and memorable.

3. Link Analytics: The application will track and provide insightful analytics on the usage and performance of the shortened URLs, including click-through rates, geographic data, and referral sources.

4. QR Code Generation: The system will generate QR codes for each shortened URL, allowing users to easily share them in printed materials or mobile devices.

5. Link History: Users will have access to a comprehensive history of their shortened URLs, including creation dates, original URLs, and usage statistics.

6. Secure and Scalable: The application will prioritize data security, implement proper authentication mechanisms, and ensure scalability to handle a large volume of requests.

7. User Management: The system will provide user registration and authentication functionalities, allowing users to manage their shortened URLs and access personalized features.

## Brand Name: RedRoute

The brand name "RedRoute" reflects the core essence of the project. The color red signifies energy, speed, and action, aligning with the fast and efficient nature of URL shortening. "Route" suggests navigation and directing users to their desired destinations, emphasizing the primary purpose of the application. The combination of "Red" and "Route" creates a memorable and impactful brand name that resonates with the project's goals.
<br/>
The RedRoute URL Shortener project aims to revolutionize URL management, offering users a reliable and feature-rich platform to create shorter, customized URLs. With its advanced features and user-centric design, RedRoute will provide an exceptional URL shortening experience.

## Built with:
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## Get a copy
It is believed that you have python installed already. Open CMD or terminal
1. Clone this repo
```sh
git clone https://github.com/Unique-Red/url_shortner.git
```
2. Open the directory
```sh
cd url_shortner
```
3. Create Virtual Environment
```sh
python -m venv <your-venv-name>
```
4. Activate virtual environment on CMD or Powershell
```sh
<your-venv-name>\Scripts\activate.bat
```
On gitbash terminal
```sh
source <your-venv-name>/Scripts/activate.csh
```
5. Install project packages
```sh
pip install -r requirements.txt
```
6. Set environment variable
```sh
set FLASK_APP=app.py
```
On gitbash terminal
```sh
export FLASK_APP=run.py
```
7. Create database
```sh
flask shell
```
```sh
db.create_all()
quit()
```
8. Run program
```sh
python app.py
```
<hr>


<br/>
Live link: <a href="https://www.redr.site/">RedRoute</a>