import os

S3_LOCATION = 'http://your-amazon-site.amazonaws.com/'
S3_KEY = 'YOURAMAZONKEY'
S3_SECRET = 'YOURAMAZONSECRET'
S3_UPLOAD_DIRECTORY = 'what_directory_on_s3'
S3_BUCKET = 's3_bucket_name'

#[('dir_value','friendly name'), ('dir_value', 'friendlyname')]
S3_UPLOAD_DIRECTORY_CHOICES = [('','Root'),]

USERNAME = 'username'
PASSWORD = 'password'


SECRET_KEY = "FLASK_SECRET_KEY"
DEBUG = True
PORT = 5000