from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, SelectField, IntegerField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# ── Database configuration ─────────────────────────────────────────────
# Option A: SQLite (recommended for local dev & small sites)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/site.db'
# Option B: PostgreSQL (uncomment when ready - replace with real credentials)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/luxjet'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False  # set True temporarily to see SQL queries

db = SQLAlchemy(app)

# ── Flask-Mail configuration ───────────────────────────────────────────
app.config['MAIL_SERVER']      = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT']        = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS']     = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME']    = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']    = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# ── Booking Request Model ──────────────────────────────────────────────
class BookingRequest(db.Model):
    __tablename__ = 'booking_requests'
    
    id              = db.Column(db.Integer, primary_key=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    full_name       = db.Column(db.String(120), nullable=False)
    email           = db.Column(db.String(120), nullable=False, index=True)
    phone           = db.Column(db.String(30), nullable=False)
    jet_category    = db.Column(db.String(50), nullable=False)
    departure       = db.Column(db.String(150), nullable=False)
    arrival         = db.Column(db.String(150), nullable=False)
    departure_date  = db.Column(db.Date, nullable=False)
    passengers      = db.Column(db.Integer, nullable=False)
    special_requests= db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<BookingRequest {self.full_name} → {self.departure} to {self.arrival}>"

# ── Booking Form (same as before) ──────────────────────────────────────
class BookingForm(FlaskForm):
    full_name         = StringField('Full Name', validators=[DataRequired()])
    email             = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone             = TelField('Phone Number', validators=[DataRequired()])
    
    jet_category      = SelectField('Jet Category', 
                                     choices=[
                                         ('', 'Select jet category'),
                                         ('Light Jet', 'Light Jet'),
                                         ('Midsize Jet', 'Midsize Jet'),
                                         ('Super Midsize', 'Super Midsize'),
                                         ('Heavy / Long Range', 'Heavy / Long Range')
                                     ],
                                     validators=[DataRequired()])
    
    departure         = StringField('Departure City / Airport', validators=[DataRequired()])
    arrival           = StringField('Arrival City / Airport', validators=[DataRequired()])
    
    departure_date    = DateField('Departure Date', validators=[DataRequired()], format='%Y-%m-%d')
    
    passengers        = IntegerField('Number of Passengers', 
                                      validators=[DataRequired(), NumberRange(min=1, max=19)])
    
    special_requests  = TextAreaField('Special Requests (pets, catering, etc.)')
    
    submit            = SubmitField('Get My Quote →')


# ── Routes ─────────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def index():
    form = BookingForm()

    if form.validate_on_submit():
        # Create new booking record
        new_booking = BookingRequest(
            full_name        = form.full_name.data,
            email            = form.email.data,
            phone            = form.phone.data,
            jet_category     = form.jet_category.data,
            departure        = form.departure.data,
            arrival          = form.arrival.data,
            departure_date   = form.departure_date.data,
            passengers       = form.passengers.data,
            special_requests = form.special_requests.data or None
        )
@app.route('/admin/requests')
def list_requests():
    requests = BookingRequest.query.order_by(BookingRequest.created_at.desc()).all()
    return render_template_string("""
    <h1>Booking Requests</h1>
    <table border="1" style="border-collapse: collapse; width:100%;">
        <tr style="background:#334155;">
            <th>ID</th><th>Date</th><th>Name</th><th>Email</th><th>From → To</th><th>Jet</th><th>Passengers</th><th>Date</th>
        </tr>
        {% for r in requests %}
        <tr>
            <td>{{ r.id }}</td>
            <td>{{ r.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
            <td>{{ r.full_name }}</td>
            <td>{{ r.email }}</td>
            <td>{{ r.departure }} → {{ r.arrival }}</td>
            <td>{{ r.jet_category }}</td>
            <td>{{ r.passengers }}</td>
            <td>{{ r.departure_date }}</td>
        </tr>
        {% endfor %}
    </table>
    <p><a href="/">Back to home</a></p>
    """, requests=requests)
  @app.route('/some_endpoint', methods=['POST'])
def create_booking():
    # ... form validation, etc.
    new_booking = Booking(
        user_id=current_user.id,
        flight_id=...,
        # etc.
    )
    db.session.add(new_booking)          # ← indented once (4 spaces) under the function
    db.session.commit()                  # ← same level
    flash('Booking created!', 'success')
    return redirect(url_for('dashboard'))
            db.session.add(new_booking)
            db.session.commit()

            # Send email notification
            subject = f"New Quote Request – {form.departure.data} → {form.arrival.data}"
            body = f"""
New Private Jet Quote Request #{new_booking.id}
──────────────────────────────
Name:          {new_booking.full_name}
Email:         {new_booking.email}
Phone:         {new_booking.phone}
Jet Category:  {new_booking.jet_category}
Passengers:    {new_booking.passengers}
Departure:     {new_booking.departure}
Arrival:       {new_booking.arrival}
Date:          {new_booking.departure_date.strftime('%Y-%m-%d')}
            
Special requests:
{new_booking.special_requests or 'None'}
Created:       {new_booking.created_at.strftime('%Y-%m-%d %H:%M UTC')}
            """.strip()

            msg = Message(subject=subject,
                          recipients=[os.getenv('ADMIN_EMAIL')],
                          body=body)
            mail.send(msg)

            flash('Thank you! Your quote request has been received and saved. We’ll contact you shortly.', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while processing your request. Please try again. ({str(e)})', 'error')

    return render_template('index.html', form=form)


# ── Initialize DB (run once or when models change) ─────────────────────
def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created (if not already present).")

if __name__ == '__main__':
    init_db()               # creates tables automatically on first run
    app.run(debug=True)
    # yourapp/admin.py
from django.contrib import admin
from .models import Jet, Booking, Inquiry  # add your models

@admin.register(Jet)
class JetAdmin(admin.ModelAdmin):
    list_display = ('model', 'seats', 'price_per_hour', 'is_available')
    list_filter = ('is_available', 'location')
    search_fields = ('model', 'registration')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('jet', 'customer', 'start_date', 'status', 'total_price')
    list_filter = ('status',)
    date_hierarchy = 'start_date'

# Similarly for other models