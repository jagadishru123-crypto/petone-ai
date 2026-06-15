from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100)
    )

    email = db.Column(
        db.String(120),
        unique=True
    )

    password = db.Column(
        db.String(200)
    )


class Pet(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer
    )

    pet_name = db.Column(
        db.String(100)
    )

    pet_type = db.Column(
        db.String(100)
    )

    breed = db.Column(
        db.String(100)
    )

    age = db.Column(
        db.String(50)
    )

    dob = db.Column(
        db.String(20)
    )

    photo = db.Column(
        db.String(300)
    )

    vaccination = db.Column(
        db.String(200)
    )

    next_vaccine_date = db.Column(
        db.String(50)
    )


class PetTask(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pet_id = db.Column(
        db.Integer
    )

    task_type = db.Column(
        db.String(50)
    )
    # Feeding
    # Medicine
    # Vaccination
    # Vet Visit

    title = db.Column(
        db.String(200)
    )

    due_date = db.Column(
        db.String(50)
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    notes = db.Column(
        db.Text
    )
class HealthRecord(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pet_id = db.Column(
        db.Integer
    )

    weight = db.Column(
        db.String(50)
    )

    temperature = db.Column(
        db.String(50)
    )

    allergies = db.Column(
        db.String(300)
    )
class GrowthRecord(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pet_id = db.Column(
        db.Integer
    )

    weight = db.Column(
        db.String(50)
    )

    height = db.Column(
        db.String(50)
    )

    record_date = db.Column(
        db.String(50)
    )

    notes = db.Column(
        db.Text
    )

    medicines = db.Column(
        db.String(300)
    )

    health_status = db.Column(
        db.String(100)
    )

    notes = db.Column(
        db.Text
    )
class VetVisit(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pet_id = db.Column(
        db.Integer
    )

    visit_date = db.Column(
        db.String(50)
    )

    doctor_name = db.Column(
        db.String(100)
    )

    reason = db.Column(
        db.String(300)
    )

    treatment = db.Column(
        db.Text
    )

    next_visit = db.Column(
        db.String(50)
    )

    vaccine_name = db.Column(
        db.String(100)
    )
class Reminder(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pet_id = db.Column(
        db.Integer
    )

    reminder_type = db.Column(
        db.String(50)
    )
    # Vaccine
    # Medicine
    # Vet Visit

    title = db.Column(
        db.String(200)
    )

    reminder_date = db.Column(
        db.String(50)
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    notes = db.Column(
        db.Text
    )
class PetGallery(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pet_id = db.Column(
        db.Integer
    )

    image = db.Column(
        db.String(300)
    )

    caption = db.Column(
        db.String(300)
    )