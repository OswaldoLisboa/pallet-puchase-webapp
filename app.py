from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

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

        # Check if the user has already logged in
        if session.get("user_id") is None:
            return render_template("index.html")
        return redirect("/daily_view")

    # User reached route via POST
    else:

        # Check if there's a user with the username from the form in the database
        users = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # There's no user with that username in the database or the password is incorrect
        if users == [] or not check_password_hash(users[0]["pass_hash"],
                                                 request.form.get("password")):
            # TODO
            return("WRONG USER OR PASSWORD")

        # Remember the user
        session["user_id"] = users[0]["user_id"]

        # Redirect the user to the Daily View page
        return redirect("/daily_view")


@app.route('/logout')
def logout():
    """ Log the user out """

    # Forget the user
    session.clear()

    # Redirect the user to the index page
    return redirect("/")


@app.route('/daily_view', methods=["GET", "POST"])
@login_required
def daily_view():
    """ Show all the purchases of a day """

    # User reached route via GET
    if request.method == "GET":
        reqDate=date.today()

    # User reached route via POST
    else:
        reqDate=request.form.get("date")

    # Query the database for all the days that had purchases
    dates = db.execute("""SELECT DATE(purchases.date) AS Date
                      FROM purchases
                      GROUP BY DATE(purchases.date)
                      ORDER BY DATE(purchases.date) DESC;""")

    # Query the database for the summary of purchases in a day
    summary = db.execute("""SELECT
                            (SELECT count(purchases.purchase_id)
                            FROM purchases where date(purchases.date) = date(:date)) AS Purchases,
                            SUM(pallets_in_purchase.quantity) AS Pallets,
                            SUM(quantity *  unitary_price) AS Spent
                        FROM purchases, pallets_in_purchase
                        WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                            AND date(purchases.date) = date(:date)
                        GROUP BY date(purchases.date)
                        ORDER BY pallets_in_purchase.purchase_id;""", date=reqDate)

    # Query the database for all the purchases in a day
    details = db.execute("""SELECT purchases.purchase_id AS Id,
                            purchases.customer AS Customer,
                            SUM(pallets_in_purchase.quantity) AS Pallets,
                            SUM(pallets_in_purchase.unitary_price * pallets_in_purchase.quantity) AS Total,
                            users.username AS User
                        FROM purchases, pallets_in_purchase, users
                        WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                            AND purchases.user = users.user_id
                            AND date(purchases.date) = date(:date)
                        GROUP BY date(purchases.purchase_id)
                        ORDER BY purchases.date;""", date=reqDate)

    # Render the page
    return render_template("daily_view.html", dates=dates, datLength=len(dates),
                          summary=summary, details=details, detLength=len(details))

@app.route('/detailed_view', methods=["GET"])
@login_required
def detailed_view():
    """ Show the details of a puchase """

    # Query the database for the purchase details
    purchase = db.execute("""SELECT purchases.customer AS Customer,
                            purchases.date AS Time,
                            SUM(pallets_in_purchase.quantity) AS Pallets,
                            SUM(pallets_in_purchase.unitary_price * pallets_in_purchase.quantity) AS Spent,
                            users.username AS User
                          FROM purchases, pallets_in_purchase, users
                          WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                            AND purchases.user = users.user_id
                            AND purchases.purchase_id = :purchase_id;""", purchase_id=request.args.get("purchase_id"))

    # Query the database for which pallets were bought
    pallets = db.execute("""SELECT type as Type,
                            quantity AS Quantity,
                            unitary_price AS 'Unitary Price',
                            quantity * unitary_price AS Total
                         FROM pallets_in_purchase
                         WHERE purchase_id = :purchase_id;""", purchase_id=request.args.get("purchase_id"))

    # Render the page
    return render_template("detailed_view.html", purchase=purchase, pallets=pallets, length=len(pallets))

@app.route('/monthly_view', methods=["GET", "POST"])
@login_required
def monthly_view():
    """ Show all the purchases of a month """

    # User reached route via GET
    if request.method == "GET":
        reqMonth=date.today().strftime("%Y-%m")

    # User reached route via POST
    else:
        reqMonth=request.form.get("month")

    # Query the database for all the days that had purchases
    months = db.execute("""SELECT strftime('%Y-%m', date) AS Month
                       FROM purchases
                       GROUP BY strftime('%Y-%m',date)
                       ORDER BY strftime('%Y-%m',date) DESC""")

    # Query the database for the summary of purchases in a day
    summary = db.execute("""SELECT (SELECT COUNT(purchases.purchase_id)
                            	FROM purchases
                                WHERE strftime('%Y-%m', purchases.date) = :month) AS Purchases,
                        	SUM(pallets_in_purchase.quantity) AS Pallets,
                        	SUM(quantity *  unitary_price) AS Spent
                        FROM purchases, pallets_in_purchase
                        WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                        	AND strftime('%Y-%m', purchases.date) = :month
                        GROUP BY strftime('%Y-%m', purchases.date);""", month=reqMonth)

    # Query the database for all the purchases in a day
    details = db.execute("""SELECT date(purchases.date) AS Date,
                            SUM(pallets_in_purchase.quantity) AS Pallets,
                            SUM(pallets_in_purchase.unitary_price * pallets_in_purchase.quantity) AS Total
                        FROM purchases, pallets_in_purchase, users
                        WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                            AND purchases.user = users.user_id
                            AND strftime('%Y-%m', purchases.date) = :month
                        GROUP BY date(purchases.date)
                        ORDER BY purchases.date;""", month=reqMonth)

    # Render the page
    return render_template("monthly_view.html", months=months, monLength=len(summary),
                          summary=summary, details=details, detLength=len(details))

@app.route('/yearly_view', methods=["GET", "POST"])
@login_required
def yearly_view():
    """ TODO """
    return("TODO")

@app.route('/buy', methods=["GET", "POST"])
@login_required
def buy():
    """ TODO """
    return render_template("buy.html")

@app.route('/confirmation', methods=["GET"])
@login_required
def confirmation():
    """ TODO """
    return("TODO")


if __name__ == "__main__":
    app.run(debug=True)
