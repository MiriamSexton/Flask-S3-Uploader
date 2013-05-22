from flask import Flask, render_template, flash
from flask.ext.wtf import FileField, BooleanField, SelectField, Form
from tools import s3_upload
from basic_auth import requires_auth

app = Flask(__name__)
app.config.from_object('config')

class UploadForm(Form):
    file_value = FileField('File')
    in_directory = SelectField('Directory', choices=app.config["S3_UPLOAD_DIRECTORY_CHOICES"])
    over_write_existing = BooleanField('Force', default=False)

@app.route('/')
def nothing_here():
    return 'Nothing here.'


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
    if app.config["DEBUG"]:
        app.run(host='0.0.0.0')
    else:
        app.run()