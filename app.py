from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, SupportTicket, Enrollment
import os
from werkzeug.utils import secure_filename
from config import Config
from forms import EnrollmentForm
from flask import session
import re

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next', None)

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Both email and password are required.", "danger")
            return redirect(url_for('login', next=next_url))

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(next_url or url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login', next=next_url))

    return render_template('login.html', next=next_url)

default_replies = [
    { 'id': 1, 'sender': 'S', 'text': 'Hello there! Thank you for reaching out to us.' },
    { 'id': 2, 'sender': 'S', 'text': 'How can I help you today?' },
    { 'id': 3, 'sender': 'S', 'text': 'We offer courses for all skill levels.' },
    { 'id': 4, 'sender': 'S', 'text': 'Our classes are available both online and offline.' },
    { 'id': 5, 'sender': 'S', 'text': 'Feel free to browse our course catalog!' },
    { 'id': 6, 'sender': 'S', 'text': 'You can reach support via email or this chat.' },
    { 'id': 7, 'sender': 'S', 'text': 'Want a recommendation? Just ask!' },
    { 'id': 8, 'sender': 'S', 'text': 'All our chefs are certified and experienced.' },
    { 'id': 9, 'sender': 'S', 'text': 'We also offer weekend batches.' },
    { 'id': 10, 'sender': 'S', 'text': 'Let me know if you want a callback.' },
    ]

@app.context_processor
def inject_default_replies():
    return dict(default_replies=default_replies)

@app.route('/')
@login_required
def home():
   return render_template("home.html", name=current_user.name)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 

if not os.path.isdir(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route('/support', methods=['GET', 'POST'])
def support():
    errors = {}
    form_data = {}

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        captcha = request.form.get('captcha')
        uploaded_file = request.files.get('attachment')

        form_data = {
            'email': email,
            'subject': subject,
            'description': description,
            'captcha': captcha,
            'attachment': None
        }

        if not email:
            errors['email'] = "Email is required."
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            errors['email'] = "Enter a valid email address."

        if not subject:
            errors['subject'] = "Subject is required."

        if not description:
            errors['description'] = "Description is required."

        if captcha != 'on':
            errors['captcha'] = "Please confirm you are not a robot."

        if uploaded_file and uploaded_file.filename:
            if allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                try:
                    uploaded_file.save(filepath)
                    form_data['attachment'] = filename
                except Exception as e:
                    errors['attachment'] = "Failed to save file. Try again."
            else:
                errors['attachment'] = "Allowed file types: png, jpg, jpeg, pdf, txt."

        if not errors:
            ticket = SupportTicket.create_from_form(
                form_data,
                user_id=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(ticket)
            db.session.commit()
            flash("Your ticket was submitted successfully.", "success")
            return redirect(url_for('ticket_success'))

        flash("Please correct the errors below and resubmit.", "danger")

    return render_template('contact.html', form=form_data, errors=errors)

@app.route('/support/success', methods=['GET'])
def ticket_success():
    return render_template('ticket_success.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/signup', methods=['POST'])
def api_signup():
    json = request.get_json() or {}
    name     = json.get('name', '').strip()
    email    = json.get('email', '').strip().lower()
    mobile   = json.get('mobile', '').strip()
    password = json.get('password', '')

    if not (name and email and mobile and password):
        return jsonify(error="All four fields required"), 400
    if len(password) < 6:
        return jsonify(error="Password too short — min 6 chars"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered"), 400
    if User.query.filter_by(mobile=mobile).first():
        return jsonify(error="Mobile already registered"), 400

    new_user = User(
        name=name,
        email=email,
        mobile=mobile,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    from flask_login import login_user
    login_user(new_user) 

    return jsonify(message="User created successfully"), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)
    return jsonify({"message": "Login successful"}), 200

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET'])
def signup():
    return render_template("sign_up.html")

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    session.pop('_flashes', None) 

    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('login'))
        else:
            flash('No account found with this email.', 'danger')
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/programs')
def programs():
    return render_template('program.html', program_id='bakery')


@app.route('/courses')
def courses():
    courses_data = [
        {
            "title": "THE GOOD GUT PROGRAM",
            "desc": "In Just 4 Weeks, Say Goodbye To Bloating, Constipation, Inflammation & Acidity. Plus Gain More Energy & Boost Immunity",
            "offer": "Get 70% OFF",
            "original_price": "4999",
            "discounted_price": "1499",
            "bg_url": url_for('static', filename='images/card.png'),
            "link": url_for('course_des')
        },
        {
            "title": "LOOK GOOD COURSE",
            "desc": "In Just 30 Days, Discover Time Tested & Science Backed Insights, Remedies And Recipes",
            "offer": "New Launch Offer | Get 88% OFF",
            "original_price": "42,995",
            "discounted_price": "4,999",
            "bg_url": url_for('static', filename='images/card.png'),
            "link": url_for('course_des')
        },
        {
            "title": "Start Your Food Business From Home",
            "desc": "Learn How To Start Your Food Business From Home, And Run A Successful Home",
            "offer": "New Launch Offer | Get 70% OFF",
            "original_price": "4999",
            "discounted_price": "1,499",
            "bg_url": url_for('static', filename='images/card.png'),
            "link": url_for('course_des')
        }
    ]
    return render_template('courses.html', courses=courses_data)
testimonials = [
    {'image': 'images/Ellipse5.png', 'quote': 'CHEF MADE IT FUN, EVEN FOR A TOTAL BEGINNER LIKE ME!', 'author': 'CARLOS D'},
    {'image': 'images/Ellipse6.png', 'quote': 'I LEFT WITH NEW SKILLS AND A FULL BELLY. HIGHLY RECOMMEND!', 'author': 'JASON R'},
    {'image': 'images/Ellipse7.png', 'quote': 'LEARNED SO MUCH IN A SHORT TIME, LOVED EVERY MINUTE!', 'author': 'EMILY T'},
    {'image': 'images/Ellipse8.png', 'quote': 'PERFECT FOR BEGINNERS AND FOOD LOVERS!', 'author': 'SANDRA M'},
]


@app.route("/course-des", endpoint="course_des")
def course_des():
    return render_template("course_description.html",testimonials=testimonials)

programs = [
    ("BAKERY BUSINESS ACCELERATOR","bakery"),
    ("CLOUD KITCHEN ACCELERATOR", "cloud")
]

@app.context_processor
def inject_programs():
    return dict(programs=programs)

@app.route("/", defaults={"program_id": None})
@app.route("/<program_id>")
def program(program_id):
    name_map = {pid: name for name, pid in programs}
    if program_id and program_id not in name_map:
        abort(404)
    return render_template(
        "program.html",
        program_id=program_id,
        program_name=name_map.get(program_id),
    )

@app.errorhandler(404)
def handle_404(e):
    return render_template("404.html"), 404

@app.route('/bakery')
def bakery():
    return render_template('program.html', program_id='bakery')

@app.route('/cloud')
def cloud():
    return render_template('program.html', program_id='cloud')
from flask import session

@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    form = EnrollmentForm()
    subtotal = 36000
    discount = 0
    total = subtotal * 1

    if request.method == 'POST':
        form.payment.data = request.form.get('payment')

        if form.validate_on_submit():
            if form.coupon.data:
                discount = 1000
                flash(f"Coupon applied! Discount: INR {discount}", "success")
                total = (subtotal - discount) * 1

            new = Enrollment(
                name=form.name.data.strip(),
                email=form.email.data.strip(),
                mobile=form.mobile.data.strip(),
                gstin=form.gstin.data,
                coupon=form.coupon.data.strip() or None,
                payment=form.payment.data
            )
            db.session.add(new)
            db.session.commit()
            session['form_submitted'] = True

            flash("Enrollment successful! See you at the class.", "success")
            return redirect(url_for('enroll_success'))

    elif request.method == 'GET':
        if not session.get('form_submitted'):
            if current_user.is_authenticated:
                form.name.data = current_user.name
                form.email.data = current_user.email
                form.mobile.data = current_user.mobile
        else:
            session.pop('form_submitted', None)

    return render_template('enroll.html',
                           form=form,
                           subtotal=subtotal,
                           discount=discount,
                           total=total)

@app.route('/enrollsuccess')
def enroll_success():
    return render_template('enroll_success.html')

@app.route('/reset-db')
def reset_db():
    db.drop_all()
    db.create_all()
    return "Database tables recreated"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
