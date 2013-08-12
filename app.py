from flask import Flask, render_template, flash
from flask.ext.wtf import FileField, BooleanField, SelectField, Form, IntegerField, file_required
from tempfile import TemporaryFile
from PIL import Image
from basic_auth import requires_auth
from tools import s3_upload
import config_defaults
import os


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
    file_value = FileField('Choose file', validators=[file_required()])
    in_directory = SelectField('Choose where it goes', choices=app.config["S3_UPLOAD_DIRECTORY_CHOICES"])
    over_write_existing = BooleanField('Force', default=False)
    max_width = IntegerField('Max Width (in pixels)', default=app.config["MAX_WIDTH"])
    max_height = IntegerField('Max Height (in pixels)', default=app.config["MAX_HEIGHT"])
    max_size = IntegerField('Max Size (in KB)', default=app.config["MAX_KB"])

    resize = BooleanField('Resize the image for me', default=False)
    resize_height = IntegerField('New Height (leave blank to adjsut perportionality to the new width)', default=10)
    resize_width = IntegerField('New Width (leave blank to adjsut perportionality to the new height)', default=100)

    save_as_png = BooleanField('Save the image in PNG format (recommended)', default=True)


@app.route('/')
def nothing_here():
    return 'Nothing here.'

@app.route('/upload',methods=['POST','GET'])
@requires_auth
def upload_page():
    form = UploadForm()
    errors = list()
    context = dict()
    context['form'] = form

    if form.validate_on_submit():

        new_image = Image.open(form.file_value.data)
        width, height = new_image.size

        output_type = ''
        new_filename = form.file_value.data.filename
        content_type = form.file_value.data.content_type.lower()
        temp_file = TemporaryFile()


        old_filetype = os.path.splitext(new_filename)[1]
        output_type = old_filetype.upper()[1:]

        if output_type == 'JPG':
            output_type = 'JPEG'

        if form.save_as_png.data:
            new_filename = os.path.splitext(new_filename)[0] + ".png"
            content_type = "image/png"
            output_type = "PNG"


        # Handle the resizing
        if form.resize.data:
            new_width = form.resize_width.data
            new_height = form.resize_height.data

            if new_height and new_width:
                new_size = (new_width, new_height)
                new_image = new_image.resize(new_size, Image.ANTIALIAS)
            else:
                # If only 1 size is given, need to make a thumbnail that is maximum that size on
                # that axis
                if new_height:
                    new_size = (width, new_height)
                elif new_width:
                    new_size = (new_width, height)
            
                new_image = new_image.thumbnail(new_size, Image.ANTIALIAS)
        # Or check the sizes to make sure they are acceptable
        else: 
            # Check Width
            ################
            if width > app.config["MAX_WIDTH"]:
                context['show_width'] = True
            if width > form.max_width.data:
                error_msg = 'This image has a width of %d.' % width
                error_msg += 'Please change the max if you are certain this this image should be uploaded.'
                flash(error_msg, 'error')
                errors.append(error_msg)

            #Check Height
            ################
            if height > app.config["MAX_HEIGHT"]:
                context['show_height'] = True
            if height > form.max_height.data:
                error_msg = 'This image has a height of %d.' % height
                error_msg += 'Please change the max if you are certain this this image should be uploaded.'
                flash(error_msg, 'error')
                errors.append(error_msg)


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
                errors.append(error_msg)

        # If no errors, then we can process
        if len(errors) == 0:
            new_image.save(temp_file, format=output_type)
            directory = form.in_directory.data
            over_write = form.over_write_existing.data

            output = s3_upload(temp_file, new_filename, content_type, directory_val=directory, force=over_write)
            
            flash(output, 'message') 

    return render_template('file_form.html', **context)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port)

