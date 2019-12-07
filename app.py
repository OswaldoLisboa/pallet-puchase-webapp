from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from helper import login_required

# Configure application
app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pallets.db")

@app.route('/', methods=["GET", "POST"])
def index():
    """Log the user in"""

    # User reached route via GET
    if request.method == "GET":
        return render_template("index.html")

    # User reached route via POST
    else:
        session["user"] = request.form.get("username")
        return redirect("/daily_view")

@app.route('/daily_view', methods=["GET", "POST"])
@login_required
def daily_view():
    return("Heeeeeyy")


if __name__ == "__main__":
    app.run(debug=True)
