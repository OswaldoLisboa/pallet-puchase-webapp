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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        if rows == []:
            return("WRONG USER")

        if not check_password_hash(rows[0]["pass_hash"], request.form.get("password")):
            return("WRONG PASSWORD")

        session["user_id"] = rows[0]["user_id"]
        return redirect("/daily_view")

@app.route('/daily_view', methods=["GET", "POST"])
@login_required
def daily_view():
    """ TODO """
    return("TODO")

@app.route('/detailed_view', methods=["GET"])
@login_required
def detailed_view():
    """ TODO """
    return("TODO")

@app.route('/monthly_view', methods=["GET", "POST"])
@login_required
def monthly_view():
    """ TODO """
    return("TODO")

@app.route('/yearly_view', methods=["GET", "POST"])
@login_required
def yearly_view():
    """ TODO """
    return("TODO")

@app.route('/buy', methods=["GET", "POST"])
@login_required
def buy():
    """ TODO """
    return("TODO")

@app.route('/confirmation', methods=["GET"])
@login_required
def confirmation():
    """ TODO """
    return("TODO")


if __name__ == "__main__":
    app.run(debug=True)
