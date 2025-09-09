import os
from flask import Flask, render_template, request, flash
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- Configuration ---
# It's crucial to set these as environment variables in Render
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-secret-key-for-dev')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

mail = Mail(app)

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        recipient = request.form.get('recipient')
        subject = request.form.get('subject')
        body = request.form.get('body')
        image = request.files.get('image')

        # Basic validation
        if not recipient or not subject or not body:
            flash('Recipient, subject, and body are required!', 'danger')
            return render_template('index.html')

        try:
            msg = Message(subject=subject,
                          recipients=[recipient],
                          body=body)

            # Handle file attachment
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

                with app.open_resource(image_path) as fp:
                    msg.attach(filename, image.mimetype, fp.read())

                # Clean up the saved file
                os.remove(image_path)

            elif image:
                flash('Invalid image format. Allowed formats are png, jpg, jpeg, gif.', 'warning')
                return render_template('index.html')


            mail.send(msg)
            flash('Email sent successfully!', 'success')

        except Exception as e:
            # Log the exception for debugging on Render
            print(f"Error sending email: {e}")
            flash(f'An error occurred: {e}', 'danger')

    return render_template('index.html')

if __name__ == '__main__':
    # Use 0.0.0.0 to be accessible in a container
    app.run(host='0.0.0.0', port=5000)
