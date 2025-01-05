from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
import bcrypt
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  #Uesd for session (secrect key)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/realestate_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a Model for User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define a Model for Property
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    bhk_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    selected_city = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)  # Store multiple image URLs as a comma-separated string
    city = db.Column(db.String(100), nullable=True)  


# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to check if the user is logged in
def is_logged_in():
    return 'user_id' in session



@app.route('/', methods=['GET'])
def index():
    # Fetch all properties and pass them to the index page
    properties = Property.query.all()
    return render_template('index.html', properties=properties)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get login credentials
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the user from the database
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Login successful, redirect to the property page or another page
            session['user_id'] = user.id 
            session['username'] = user.username
            return redirect(url_for('property'))
        else:
            # If login fails, return an error
            return "Invalid credentials. Please try again."

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get signup form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Hash the password before saving it to the database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create a new user record
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/property', methods=['GET', 'POST'])
def property():
    if request.method == 'POST':
        # Get form data for property submission
        name = request.form.get('name')
        whatsapp = request.form.get('whatsapp')
        email = request.form.get('email')
        selected_city = request.form.get('selected_city')
        property_type = request.form.get('property_type')
        bhk_type = request.form.get('bhk_type')
        address = request.form.get('address')
        message = request.form.get('message')

        # Handle image file upload (multiple images)
        image_urls = []
        if 'property_images' in request.files:
            images = request.files.getlist('property_images')  # Get all selected files
            for image in images:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    image_urls.append(f'uploads/{filename}')  # Add image URL to list

        # Create a new property record
        new_property = Property(
            name=name, 
            whatsapp=whatsapp, 
            email=email, 
            property_type=property_type, 
            bhk_type=bhk_type, 
            address=address, 
            selected_city=selected_city, 
            message=message,
            image_url=', '.join(image_urls)  # Save image URLs as a comma-separated string
        )
        db.session.add(new_property)
        db.session.commit()

        # Redirect to the property page after submission
        return redirect(url_for('property'))

    # Render property page with only the form (no properties)
    return render_template('property.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
