import config_nonsecret

# This is all stuff that should be set in the env:
S3_LOCATION = 'http://your-amazon-site.amazonaws.com/'
S3_KEY = 'YOURAMAZONKEY'
S3_SECRET = 'YOURAMAZONSECRET'
S3_UPLOAD_DIRECTORY = 'what_directory_on_s3'
S3_BUCKET = 's3_bucket_name'

USERNAME = 'username'
PASSWORD = 'password'


SECRET_KEY = "FLASK_SECRET_KEY"
DEBUG = True
PORT = 5000


if config_nonsecret.S3_UPLOAD_DIRECTORY_CHOICES and type(config_nonsecret.S3_UPLOAD_DIRECTORY_CHOICES) == type(list()):
    S3_UPLOAD_DIRECTORY_CHOICES = config_nonsecret.S3_UPLOAD_DIRECTORY_CHOICES
else:
    S3_UPLOAD_DIRECTORY_CHOICES = [('','Root'),('','Same root')]
