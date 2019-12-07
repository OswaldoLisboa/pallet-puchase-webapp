from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from helper import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pallets.db"
db = SQLAlchemy(app)

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.user_id



@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        session["user"] = request.form.get("username")
        return redirect("/daily_view")

@app.route('/daily_view', methods=["GET", "POST"])
@login_required
def daily_view():
    return("Heeeeeyy")


if __name__ == "__main__":
    app.run(debug=True)
