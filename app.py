from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, SupportTicket, Enrollment
import os
from werkzeug.utils import secure_filename
from config import Config
from forms import EnrollmentForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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
        form_data = {
            'email':       request.form.get('email', '').strip(),
            'subject':     request.form.get('subject', '').strip(),
            'description': request.form.get('description', '').strip(),
            'captcha':     request.form.get('captcha'),
            'attachment':  None
        }
        if not errors:
            uploaded = request.files.get('attachment')
            if uploaded and uploaded.filename:
                if allowed_file(uploaded.filename):
                    filename = secure_filename(uploaded.filename)
                    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    uploaded.save(saved_path)
                    form_data['attachment'] = filename
                else:
                    errors['attachment'] = "Allowed types: png, jpg, pdf, txt."

        if not errors:
            ticket = SupportTicket.create_from_form(form_data)
            db.session.add(ticket)
            db.session.commit()

            flash('Your ticket was submitted successfully.', 'success')
            return redirect(url_for('ticket_success'))

        flash('Please correct the errors below and resubmit.', 'danger')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/')
@login_required
def home():
    return render_template("home.html", name=current_user.name)

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
    if request.method == 'POST':
        email = request.form.get('email')
        flash('If this email is registered, you will receive a password reset link.')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/programs')
def programs():
    return render_template('programs.html')

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

@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    form = EnrollmentForm()
    if form.validate_on_submit():
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
        flash("Enrollment successful! See you at the class.", "success")
        return redirect(url_for('enroll_success'))
    return render_template('enroll.html', form=form)

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
