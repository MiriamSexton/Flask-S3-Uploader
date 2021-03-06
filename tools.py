import boto
import os.path
from flask import current_app as app
from werkzeug import secure_filename

def s3_upload(source_file,acl='public-read', directory_val=None, force=False):
    ''' Uploads WTForm File Object to Amazon S3

        Expects following app.config attributes to be set:
            S3_KEY              :   S3 API Key
            S3_SECRET           :   S3 Secret Key
            S3_BUCKET           :   What bucket to upload to
            S3_UPLOAD_DIRECTORY :   Which S3 Directory.

        The default sets the access rights on the uploaded file to
        public-read.  It also generates a unique filename via
        the uuid4 function combined with the file extension from
        the source file.
    '''

    if directory_val == None:
        directory_val = app.config["S3_UPLOAD_DIRECTORY"]

    source_filename = secure_filename(source_file.data.filename)
    destination_filename = "/".join([directory_val,source_filename])
    url = app.config["S3_LOCATION"] + app.config["S3_BUCKET"] + '/' + destination_filename 

    ret_str = ''

    # Connect to S3 and upload file.
    conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
    b = conn.get_bucket(app.config["S3_BUCKET"])

    # Check to see if it exists
    if b.get_key(destination_filename):
        ret_str += 'A file named %s already existed at <a href="%s">%s</a>.' % (source_filename, url, url)

        if not force:
            return ret_str

    sml = b.new_key(destination_filename)
    headers = {'Content-Type': source_file.data.content_type}

    
    sml.set_contents_from_string(source_file.data.read(), headers=headers, replace=force)
    sml.set_acl(acl)

    ret_str += 'See the new file at <a href="%s">%s</a>' % (url, url)

    return ret_str
