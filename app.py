from flask import Flask, render_template, flash
from flask.ext.wtf import FileField, BooleanField, SelectField, Form
from tools import s3_upload
from basic_auth import requires_auth
import config_defaults
import os


app = Flask(__name__)

if os.environ.get('DEBUG_MODE', True):
    app.debug = True

app.config["S3_UPLOAD_DIRECTORY_CHOICES"] = os.environ.get('S3_UPLOAD_DIRECTORY_CHOICES',config_defaults.S3_UPLOAD_DIRECTORY_CHOICES)
app.config["S3_KEY"] = os.environ.get("S3_KEY", config_defaults.S3_KEY)
app.config["S3_SECRET"] = os.environ.get("S3_SECRET", config_defaults.S3_SECRET)
app.config["S3_UPLOAD_DIRECTORY"] = os.environ.get("S3_UPLOAD_DIRECTORY", config_defaults.S3_UPLOAD_DIRECTORY)
app.config["S3_BUCKET"] = os.environ.get("S3_BUCKET", config_defaults.S3_BUCKET)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", config_defaults.SECRET_KEY)
app.config["USERNAME"] = os.environ.get("USERNAME", config_defaults.USERNAME)
app.config["PASSWORD"] = os.environ.get("PASSWORD", config_defaults.PASSWORD)


class UploadForm(Form):
    file_value = FileField('File')
    in_directory = SelectField('Directory', choices=app.config["S3_UPLOAD_DIRECTORY_CHOICES"])
    over_write_existing = BooleanField('Force', default=False)

@app.route('/')
def nothing_here():
    import pdb; pdb.set_trace()
    return 'Nothing here: %s: (%s)' % (type(app.config["S3_UPLOAD_DIRECTORY_CHOICES"]), app.config["S3_UPLOAD_DIRECTORY_CHOICES"])


@app.route('/upload',methods=['POST','GET'])
@requires_auth
def upload_page():
    form = UploadForm()

    if form.validate_on_submit():
        directory = form.in_directory.data
        over_write = form.over_write_existing.data
        output = s3_upload(form.file_value, directory_val=directory, force=over_write)
        flash(output)

    return render_template('file_form.html',form=form)

if __name__ == '__main__':
    if app.debug:
        app.run(host='0.0.0.0')
    else:
        app.run()