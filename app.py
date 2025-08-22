from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
import csv, sys
import os

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from config import studio

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.secret_key = "change-this-key"

@app.context_processor
def inject_studio():
    return dict(studio=studio)

@app.route("/")
def home(): return render_template("home.html")

@app.route("/classes")
def classes(): return render_template("classes.html")

@app.route("/pricing")
def pricing(): return render_template("pricing.html")

@app.route("/trial", methods=["GET","POST"])
def trial():
    if studio.get("appointment_link") and not studio.get("use_internal_booking_form"):
        return render_template("trial.html")
    if request.method == "POST":
        name = request.form.get("name","").strip()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
