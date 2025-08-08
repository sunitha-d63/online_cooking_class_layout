from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField, SubmitField
from wtforms.validators import InputRequired, Email, Length, Regexp, Optional

class EnrollmentForm(FlaskForm):
    name = StringField('Name', validators=[
        InputRequired("Name is required"),
        Length(min=3, message="At least 3 characters")
    ])

    email = StringField('Email', validators=[
        InputRequired("Email is required"),
        Email("Invalid email format")
    ], render_kw={"type": "email"})

    mobile = StringField('Mobile Number', validators=[
        InputRequired("Mobile number is required"),
        Length(min=10, max=10, message="Must be exactly 10 digits"),
        Regexp(r'^[0-9]{10}$', message="Digits only—no letters or symbols")
    ], render_kw={"type": "tel"})

    gstin = BooleanField('Use GSTIN for claiming input tax (India)')

    coupon = StringField('Coupon Code', validators=[Optional()],
                         render_kw={"placeholder": "Enter coupon code"})

    payment = HiddenField('Payment Method', validators=[
        InputRequired("Please select a payment method")
    ])

    submit = SubmitField('Submit & Pay Now')
