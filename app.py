from flask import Flask, render_template, request, jsonify, redirect
from google import genai
from database import db, User, Pet, PetTask, HealthRecord, VetVisit, Reminder, PetGallery, GrowthRecord
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import os
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petone_new.db"
app.config["SECRET_KEY"] = "petone_secret_key"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()



client = genai.Client(
    api_key=os.environ.get("AQ.Ab8RN6JPn5AX9nP-iylYz1bJ-lMn7ykndPpAXZKDBrCfNiPClQ")
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already exists"

        hashed_password = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return redirect("/mypets")

        return "Invalid Email or Password"

    return render_template("login.html")


@app.route("/mypets")
def mypets():
    pets = Pet.query.all()
    birthday_message = ""
    today = datetime.now().strftime("%m-%d")

    for pet in pets:
        if pet.dob:
            try:
                pet_date = datetime.strptime(pet.dob, "%Y-%m-%d")
                if pet_date.strftime("%m-%d") == today:
                    birthday_message = f"🎉 Happy Birthday {pet.pet_name}!"
            except:
                pass

    return render_template(
        "mypets.html",
        pets=pets,
        birthday_message=birthday_message
    )


@app.route("/addpet", methods=["GET", "POST"])
def addpet():
    if request.method == "POST":
        filename = ""
        photo = request.files.get("photo")

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        pet = Pet(
            user_id=1,
            pet_name=request.form["pet_name"],
            pet_type=request.form["pet_type"],
            breed=request.form["breed"],
            age=request.form["age"],
            dob=request.form["dob"],
            photo=filename,
            vaccination=request.form.get("vaccination"),
            next_vaccine_date=request.form.get("next_vaccine_date")
        )

        db.session.add(pet)
        db.session.commit()

        return redirect("/mypets")

    return render_template("add_pet.html")


@app.route("/editpet/<int:id>", methods=["GET", "POST"])
def editpet(id):
    pet = Pet.query.get_or_404(id)

    if request.method == "POST":
        pet.pet_name = request.form["pet_name"]
        pet.pet_type = request.form["pet_type"]
        pet.breed = request.form["breed"]
        pet.age = request.form["age"]
        pet.dob = request.form["dob"]
        pet.vaccination = request.form.get("vaccination")
        pet.next_vaccine_date = request.form.get("next_vaccine_date")

        photo = request.files.get("photo")
        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            pet.photo = filename

        db.session.commit()
        return redirect("/mypets")

    return render_template("edit_pet.html", pet=pet)


@app.route("/deletepet/<int:id>")
def deletepet(id):
    pet = Pet.query.get_or_404(id)
    db.session.delete(pet)
    db.session.commit()
    return redirect("/mypets")


@app.route("/health")
def health():
    records = HealthRecord.query.all()
    return render_template("health.html", records=records)


@app.route("/addhealth", methods=["GET", "POST"])
def addhealth():
    pets = Pet.query.all()

    if request.method == "POST":
        record = HealthRecord(
            pet_id=request.form["pet_id"],
            weight=request.form["weight"],
            temperature=request.form["temperature"],
            allergies=request.form["allergies"],
            medicines=request.form["medicines"],
            health_status=request.form["health_status"],
            notes=request.form["notes"]
        )
        db.session.add(record)
        db.session.commit()
        return redirect("/health")

    return render_template("add_health.html", pets=pets)


@app.route("/tasks")
def tasks():
    tasks = PetTask.query.all()
    return render_template("tasks.html", tasks=tasks)


@app.route("/addtask", methods=["GET", "POST"])
def addtask():
    pets = Pet.query.all()

    if request.method == "POST":
        task = PetTask(
            pet_id=request.form["pet_id"],
            task_type=request.form["task_type"],
            title=request.form["title"],
            due_date=request.form["due_date"],
            notes=request.form["notes"],
            status="Pending"
        )
        db.session.add(task)
        db.session.commit()
        return redirect("/tasks")

    return render_template("add_task.html", pets=pets)


@app.route("/complete_task/<int:id>")
def complete_task(id):
    task = PetTask.query.get_or_404(id)
    task.status = "Completed"
    db.session.commit()
    return redirect("/tasks")


@app.route("/delete_task/<int:id>")
def delete_task(id):
    task = PetTask.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect("/tasks")




@app.route("/ask", methods=["POST"])
def ask():
    try:
        question = request.form.get("question", "").strip()
        uploaded_file = request.files.get("file")

        contents_payload = []

        if uploaded_file and uploaded_file.filename != '':
            file_bytes = uploaded_file.read()
            mime_type = uploaded_file.content_type
            contents_payload.append({
                "mime_type": mime_type,
                "data": file_bytes
            })

        # Upgraded smart prompt that detects intent
        system_prompt = f"""
        You are an expert pet-care assistant for PetOne AI.
        The user has sent the following message or image: "{question}"
        
        CRITICAL INTENT DETECTION:
        1. If the user is just introducing their pet name (e.g., "my pet name is ceasar"), saying hi, or asking a casual, non-medical question, reply strictly as a normal chat response. Do not use diagnostic cards.
        2. If the user is describing symptoms, illness, or medical concerns, use the structural diagnostic card breakdown.
        
        You MUST respond strictly as a JSON object with one of these two formats:
        
        [FORMAT A - For casual conversation / text updates]:
        {{
            "response_type": "chat",
            "message": "A friendly, warm response here. Remember names if given! Keep text clean and use emojis naturally."
        }}
        
        [FORMAT B - For health symptoms / medical questions]:
        {{
            "response_type": "diagnostic",
            "possible_causes": ["Point 1", "Point 2"],
            "home_care": ["Tip 1", "Tip 2"],
            "warning_signs": ["Sign 1", "Sign 2"],
            "vet_advice": ["Advice 1", "Advice 2"]
        }}
        
        RULES: Do not include markdown code block tags like ```json. Return raw JSON text only. Use <strong> instead of markdown stars for bolding text inside your answers.
        """
        
        contents_payload.append(system_prompt)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents_payload
        )

        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.replace("```json", "", 1)
        if clean_text.endswith("```"):
            clean_text = clean_text.rsplit("```", 1)[0]
        clean_text = clean_text.strip()

        return jsonify({"json_answer": clean_text})

    except Exception as e:
        print(f"Error in chat /ask endpoint: {str(e)}")
        return jsonify({"error": str(e)})

@app.route("/vet")
def vet():
    visits = VetVisit.query.all()
    return render_template("vet.html", visits=visits)


@app.route("/addvet", methods=["GET", "POST"])
def addvet():
    pets = Pet.query.all()

    if request.method == "POST":
        visit = VetVisit(
            pet_id=request.form["pet_id"],
            visit_date=request.form["visit_date"],
            doctor_name=request.form["doctor_name"],
            reason=request.form["reason"],
            treatment=request.form["treatment"],
            next_visit=request.form["next_visit"],
            vaccine_name=request.form["vaccine_name"]
        )
        db.session.add(visit)
        db.session.commit()
        return redirect("/vet")

    return render_template("add_vet.html", pets=pets)


@app.route("/reminders")
def reminders():
    reminders = Reminder.query.all()
    return render_template("reminders.html", reminders=reminders)


@app.route("/addreminder", methods=["GET", "POST"])
def addreminder():
    pets = Pet.query.all()

    if request.method == "POST":
        reminder = Reminder(
            pet_id=request.form["pet_id"],
            reminder_type=request.form["reminder_type"],
            title=request.form["title"],
            reminder_date=request.form["reminder_date"],
            notes=request.form["notes"],
            status="Pending"
        )
        db.session.add(reminder)
        db.session.commit()
        return redirect("/reminders")

    return render_template("add_reminder.html", pets=pets)


@app.route("/complete_reminder/<int:id>")
def complete_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    reminder.status = "Completed"
    db.session.commit()
    return redirect("/reminders")


@app.route("/gallery")
def gallery():
    photos = PetGallery.query.all()
    return render_template("gallery.html", photos=photos)


@app.route("/addphoto", methods=["GET", "POST"])
def addphoto():
    pets = Pet.query.all()

    if request.method == "POST":
        filename = ""
        photo = request.files.get("photo")

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        image = PetGallery(
            pet_id=request.form["pet_id"],
            image=filename,
            caption=request.form["caption"]
        )
        db.session.add(image)
        db.session.commit()
        return redirect("/gallery")

    return render_template("add_photo.html", pets=pets)


@app.route("/growth")
def growth():
    records = GrowthRecord.query.all()
    return render_template("growth.html", records=records)


@app.route("/addgrowth", methods=["GET", "POST"])
def addgrowth():
    pets = Pet.query.all()

    if request.method == "POST":
        record = GrowthRecord(
            pet_id=request.form["pet_id"],
            weight=request.form["weight"],
            height=request.form["height"],
            record_date=request.form["record_date"],
            notes=request.form["notes"]
        )
        db.session.add(record)
        db.session.commit()
        return redirect("/growth")

    return render_template("add_growth.html", pets=pets)


@app.route("/vaccines")
def vaccines():
    pets = Pet.query.all()
    today = datetime.today().date()

    for pet in pets:
        pet.vaccine_status = "Unknown"
        if pet.next_vaccine_date:
            try:
                vaccine_date = datetime.strptime(pet.next_vaccine_date, "%Y-%m-%d").date()
                if vaccine_date < today:
                    pet.vaccine_status = "Overdue"
                else:
                    pet.vaccine_status = "Upcoming"
            except:
                pass

    return render_template("vaccines.html", pets=pets)


@app.route("/timeline")
def timeline():
    growth_records = GrowthRecord.query.all()
    health_records = HealthRecord.query.all()
    vet_visits = VetVisit.query.all()
    reminders = Reminder.query.all()
    photos = PetGallery.query.all()

    return render_template(
        "timeline.html",
        growth_records=growth_records,
        health_records=health_records,
        vet_visits=vet_visits,
        reminders=reminders,
        photos=photos
    )


@app.route("/birthdays")
def birthdays():
    pets = Pet.query.all()
    today = datetime.now()

    for pet in pets:
        pet.days_left = None
        if pet.dob:
            try:
                dob = datetime.strptime(pet.dob, "%Y-%m-%d")
                next_birthday = datetime(today.year, dob.month, dob.day)

                if next_birthday.date() < today.date():
                    next_birthday = datetime(today.year + 1, dob.month, dob.day)

                pet.days_left = (next_birthday.date() - today.date()).days
            except:
                pass

    return render_template("birthdays.html", pets=pets)


@app.route("/health_ai")
def health_ai():
    return render_template("health_ai.html")


@app.route("/analyze_health", methods=["POST"])
def analyze_health():
    try:
        data = request.get_json()
        if not data or "symptoms" not in data:
            return jsonify({"answer": "⚠️ Please enter some symptoms or health questions."})

        symptoms = data["symptoms"]

        prompt = f"""
        You are an expert veterinary AI assistant for the PetOne AI platform.
        The user has asked the following about their pet:
        "{symptoms}"
        
        Please provide a clear, helpful response. 
        CRITICAL FORMATTING RULES:
        - Do NOT write a single dense paragraph.
        - Use bold headers (##) and organized bullet points or numbered lists.
        - Add generous spacing between sections so it is readable and beautiful.
        - Use relevant emojis (🐾, 🐕, 🐈, ⚠️, ❤️) naturally to break up text.
        - **Bold** key terms, medications, or important warnings.
        - Always include a small disclaimer at the end about consulting a real vet if it's an emergency.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({"answer": response.text})

    except Exception as e:
        print(f"Error in analyze_health: {str(e)}")
        return jsonify({"answer": f"❌ An error occurred: {str(e)}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)