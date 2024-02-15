# Use a base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /url_shortner

# Copy the application files to the container
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

COPY . .

# Define the command to run the application
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
