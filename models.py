from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, RadioField, SubmitField
from wtforms.validators import InputRequired, Email, Length, Regexp, Optional
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(150), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    mobile        = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"<User {self.email or self.mobile}>"


class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email       = db.Column(db.String(254), nullable=False)
    subject     = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_robot    = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    status      = db.Column(db.String(30), default='Open')
    attachment  = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref='tickets')

    @staticmethod
    def create_from_form(form_data,user_id=None):
        return SupportTicket(
            user_id     = user_id,
            email       = form_data['email'],
            subject     = form_data['subject'],
            description = form_data['description'],
            is_robot    = form_data.get('captcha') == 'on',
            attachment  = form_data.get('attachment')
        )

class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, index=True)
    mobile = db.Column(db.String(10), nullable=False)
    gstin = db.Column(db.Boolean, nullable=False, default=False)
    coupon = db.Column(db.String(64), nullable=True)
    payment = db.Column(db.String(10), nullable=False)

    created_at = db.Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Enrollment {self.email} ({self.payment})>"

class EnrollmentForm(FlaskForm):
    name = StringField('Name', default='')
    email = StringField('Email', default='')
    mobile = StringField('Mobile', default='')
