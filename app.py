from flask import Flask, render_template, flash
from flask.ext.wtf import FileField, BooleanField, SelectField, Form, IntegerField
from tools import s3_upload
from basic_auth import requires_auth
import config_defaults
import os
import Image


app = Flask(__name__)

if os.environ.get('DEBUG_MODE', "False") != "False":
    app.debug = True

app.config["S3_UPLOAD_DIRECTORY_CHOICES"] = os.environ.get('S3_UPLOAD_DIRECTORY_CHOICES',config_defaults.S3_UPLOAD_DIRECTORY_CHOICES)
app.config["S3_KEY"] = os.environ.get("S3_KEY", config_defaults.S3_KEY)
app.config["S3_SECRET"] = os.environ.get("S3_SECRET", config_defaults.S3_SECRET)
app.config["S3_UPLOAD_DIRECTORY"] = os.environ.get("S3_UPLOAD_DIRECTORY", config_defaults.S3_UPLOAD_DIRECTORY)
app.config["S3_BUCKET"] = os.environ.get("S3_BUCKET", config_defaults.S3_BUCKET)
app.config["S3_LOCATION"] = os.environ.get("S3_LOCATION", config_defaults.S3_LOCATION)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", config_defaults.SECRET_KEY)
app.config["USERNAME"] = os.environ.get("USERNAME", config_defaults.USERNAME)
app.config["PASSWORD"] = os.environ.get("PASSWORD", config_defaults.PASSWORD)

app.config["MAX_WIDTH"] = os.environ.get("MAX_WIDTH", config_defaults.MAX_WIDTH)
app.config["MAX_HEIGHT"] = os.environ.get("MAX_HEIGHT", config_defaults.MAX_HEIGHT)
app.config["MAX_KB"] = os.environ.get("MAX_KB", config_defaults.MAX_KB)

class UploadForm(Form):
    file_value = FileField('File')
    in_directory = SelectField('Directory', choices=app.config["S3_UPLOAD_DIRECTORY_CHOICES"])
    over_write_existing = BooleanField('Force', default=False)
    max_width = IntegerField('Max Width', default=app.config["MAX_WIDTH"])
    max_height = IntegerField('Max Height', default=app.config["MAX_HEIGHT"])
    max_size = IntegerField('Max Size (in KB)', default=app.config["MAX_KB"])



@app.route('/')
def nothing_here():
    return 'Nothing here.'

@app.route('/upload',methods=['POST','GET'])
@requires_auth
def upload_page():
    form = UploadForm()

    context = dict()
    context['form'] = form

    if form.validate_on_submit():

        new_image = Image.open(form.file_value.data)
        width, height = new_image.size


        # Check Width
        ################
        if width > app.config["MAX_WIDTH"]:
            context['show_width'] = True
        if width > form.max_width.data:
            error_msg = 'This image has a width of %d.' % width
            error_msg += 'Please change the max if you are certain this this image should be uploaded.'
            flash(error_msg, 'error')


        #Check Height
        ################
        if height > app.config["MAX_HEIGHT"]:
            context['show_height'] = True
        if height > form.max_height.data:
            error_msg = 'This image has a height of %d.' % height
            error_msg += 'Please change the max if you are certain this this image should be uploaded.'
            flash(error_msg, 'error')


        # Check filesize
        ################

        # go to end of file, so can tell position (size in bytse)
        form.file_value.data.seek(0,2)
        img_size = form.file_value.data.tell()

        # to Kb
        img_size /= 1024

        # reset location to beginning
        form.file_value.data.seek(0,0)

        if img_size > app.config["MAX_KB"]:
            context['show_size'] = True
        if img_size > form.max_size.data:
            error_msg = 'This image is %d KB.' % img_size
            error_msg += 'Please change the max if you are certain this this image should be uploaded.'
            flash(error_msg, 'error')

        #If nothing in context but form
        if len(context) == 1:
            directory = form.in_directory.data
            over_write = form.over_write_existing.data
            output = s3_upload(form.file_value, directory_val=directory, force=over_write)
            flash(output, 'message')



    return render_template('file_form.html',**context)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port)

