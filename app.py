from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
import csv, sys, os

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# import config regardless of where you run from
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from config import studio

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.secret_key = "change-this-key"

@app.context_processor
def inject_studio():
    return dict(studio=studio)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/classes")
def classes():
    return render_template("classes.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/trial", methods=["GET", "POST"])
def trial():
    # External scheduler path
    if studio.get("appointment_link") and not studio.get("use_internal_booking_form"):
        return render_template("trial.html")

    # Built-in simple request form
    if request.method == "POST":
        name = request.form.get("name","").strip()
        phone = request.form.get("phone","").strip()
        email = request.form.get("email","").strip()
        level = request.form.get("level","").strip()
        preferred_class = request.form.get("preferred_class","").strip()
        notes = request.form.get("notes","").strip()
        if not name or not phone:
            flash("Please provide your name and phone number.")
            return redirect(url_for("trial"))
        with (DATA_DIR / "trial_requests.csv").open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([name, phone, email, level, preferred_class, notes])
        flash("Thanks! Your trial request was received. We’ll confirm shortly.")
        return redirect(url_for("trial"))
    return render_template("trial.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    # (Optional) Collect simple contact messages locally
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        message = request.form.get("message","").strip()
        if not name or not message:
            flash("Please include your name and a message.")
            return redirect(url_for("contact"))
        with (DATA_DIR / "messages.csv").open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([name, email, message])
        flash("Message received! We’ll get back to you soon.")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/join", methods=["GET", "POST"])
def join():
    """
    MVP 'Join' signup:
    - Renders a form with class + timeslot options from config.studio (if present)
    - Saves entries to data/join_requests.csv
    - Shows flash on success
    - Easy stubs for email/webhook later
    """
    # Example: pull classes/times from config if you have them
    classes_cfg = studio.get("classes", [])
    # Expect each item like: {"name": "Beginner MMA", "times": ["Mon 6pm", "Wed 6pm"]}
    # but this will work even if it's an empty list

    if request.method == "POST":
        name   = request.form.get("name","").strip()
        email  = request.form.get("email","").strip()
        phone  = request.form.get("phone","").strip()
        c_name = request.form.get("class_name","").strip()
        slot   = request.form.get("timeslot","").strip()
        notes  = request.form.get("notes","").strip()

        if not name or not (email or phone) or not c_name:
            flash("Please provide your name, a way to contact you, and select a class.")
            return redirect(url_for("join"))

        # Save to CSV
        csv_path = DATA_DIR / "join_requests.csv"
        is_new = not csv_path.exists()
        with csv_path.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(["name","email","phone","class","timeslot","notes"])
            w.writerow([name, email, phone, c_name, slot, notes])

        # --- Optional integrations (uncomment & implement later) ---
        # 1) Email the studio owner
        # send_owner_email(subject="New Join Request", body=f"...")
        # 2) Post to a webhook (Zapier/Make/Airtable/Sheets)
        # post_webhook({"name": name, "email": email, ...})

        flash("Thanks! We’ve received your request. We’ll confirm your spot shortly.")
        return redirect(url_for("join"))

    return render_template("join.html", classes_cfg=classes_cfg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
