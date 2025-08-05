from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, Optional

class EnrollmentForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired("Name is required"),
            Length(min=3, message="At least 3 characters")
        ],
        render_kw={"placeholder": "name"}
    )
    email = StringField(
        "Email",
        validators=[DataRequired("Email is required"), Email("Enter a valid email")],
        render_kw={"type": "email"}
    )
    mobile = StringField(
        "Mobile Number",
        validators=[DataRequired("Mobile is required"), Regexp(r'^\d{10}$', message="10‑digit number")],
        render_kw={"type": "tel"}
    )
    gstin = BooleanField("Use GSTIN for claiming input tax")
    coupon = StringField("Coupon Code", validators=[Optional()], render_kw={"placeholder": "Enter coupon code"})
    payment = RadioField(
        "Payment Method",
        choices=[("upi", "UPI"), ("card", "Credit/Debit Card")],
        validators=[DataRequired("Select a payment method")]
    )
    submit = SubmitField("Submit & Pay Now")
