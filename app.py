from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, send_from_directory
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
import xlsxwriter, os

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

        # Check if the user has already logged in, if positive the user
        # will be redirected to the daily view page
        if session.get("user_id") is None:
            return render_template("index.html")
        return redirect("/daily_view")

    # User reached route via POST
    else:

        # Check if there's a user with the username from the form in the database
        users = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # There's no user with that username in the database
        # or the password is incorrect
        if users == [] or not check_password_hash(users[0]["pass_hash"],
                                                 request.form.get("password")):
            return("Wrong Username or Password")

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

        # Set the date based on if there's an url parameter, if positive,
        # will use this date, otherwise, will use the current date
        if request.args.get("date"):
            reqDate = request.args.get("date")
        else:
            reqDate=date.today()

    # User reached route via POST
    else:
        # Set the date based on the form
        reqDate=request.form.get("date")

    # Query the database for all the days that had purchases
    # and store them in a variable
    dates = db.execute("""SELECT DATE(purchases.date) AS Date
                      FROM purchases
                      GROUP BY DATE(purchases.date)
                      ORDER BY DATE(purchases.date) DESC;""")

    # Query the database for the summary of purchases in a day
    # and store it in a variable
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
    # and store them in a variable
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
                          summary=summary, details=details, detLength=len(details), reqDate=reqDate)

@app.route('/detailed_view', methods=["GET"])
@login_required
def detailed_view():
    """ Show the details of a puchase """

    # Query the database for the purchase details
    # and store them in a variable
    purchase = db.execute("""SELECT purchases.customer AS Customer,
                            purchases.date AS Time,
                            SUM(pallets_in_purchase.quantity) AS Pallets,
                            SUM(pallets_in_purchase.unitary_price * pallets_in_purchase.quantity) AS Spent,
                            users.username AS User
                          FROM purchases, pallets_in_purchase, users
                          WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                            AND purchases.user = users.user_id
                            AND purchases.purchase_id = :purchase_id;""", purchase_id=request.args.get("purchase_id"))

    # Query the database to check which pallets were bought in this particular
    # purchase and store them in a variable
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
    """ Show a summary of every day in a month """

    # User reached route via GET
    if request.method == "GET":
        # Set the month based on if there's an url parameter, if positive,
        # will use this month, otherwise, will use the current month
        if request.args.get("month"):
            reqMonth = request.args.get("month")
        else:
            reqMonth=date.today().strftime("%Y-%m")

    # User reached route via POST
    else:
        # Set the month based on the form
        reqMonth=request.form.get("month")

    # Query the database for all the months that had purchases
    # and store them in a variable
    months = db.execute("""SELECT strftime('%Y-%m', date) AS Month
                       FROM purchases
                       GROUP BY strftime('%Y-%m',date)
                       ORDER BY strftime('%Y-%m',date) DESC""")

    # Query the database for the summary of purchases in a month
    # and store it in a variable
    summary = db.execute("""SELECT (SELECT COUNT(purchases.purchase_id)
                            	FROM purchases
                                WHERE strftime('%Y-%m', purchases.date) = :month) AS Purchases,
                        	SUM(pallets_in_purchase.quantity) AS Pallets,
                        	SUM(quantity *  unitary_price) AS Spent
                        FROM purchases, pallets_in_purchase
                        WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                        	AND strftime('%Y-%m', purchases.date) = :month
                        GROUP BY strftime('%Y-%m', purchases.date);""", month=reqMonth)

    # Query the database for the sum of all the purchases in a month
    # and store it in a variable
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
                          summary=summary, details=details, detLength=len(details), reqMonth=reqMonth)

@app.route('/yearly_view', methods=["GET", "POST"])
@login_required
def yearly_view():
    """ Show a summary of every month in a year """

    # User reached route via GET
    if request.method == "GET":
        # Set the year to the current year
        reqYear=date.today().strftime("%Y")

    # User reached route via POST
    else:
        # Set the year base on the form
        reqYear=request.form.get("year")

    # Query the database for all the years that had purchases
    # and store them in a variable
    years = db.execute("""SELECT strftime('%Y', date) AS Year
                       FROM purchases
                       GROUP BY strftime('%Y',date)
                       ORDER BY strftime('%Y',date) DESC""")

    # Query the database for the summary of purchases in a year
    # and store it in a variable
    summary = db.execute("""SELECT (SELECT COUNT(purchases.purchase_id)
                            	FROM purchases
                                WHERE strftime('%Y', purchases.date) = :year) AS Purchases,
                        	SUM(pallets_in_purchase.quantity) AS Pallets,
                        	SUM(quantity *  unitary_price) AS Spent
                        FROM purchases, pallets_in_purchase
                        WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                        	AND strftime('%Y', purchases.date) = :year
                        GROUP BY strftime('%Y', purchases.date);""", year=reqYear)

    # Query the database for the sum of all the purchases in a year
    # and store it in a variable
    details = db.execute("""SELECT strftime('%Y-%m', purchases.date) AS Month,
                            SUM(pallets_in_purchase.quantity) AS Pallets,
                            SUM(pallets_in_purchase.unitary_price * pallets_in_purchase.quantity) AS Total
                        FROM purchases, pallets_in_purchase, users
                        WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                            AND purchases.user = users.user_id
                            AND strftime('%Y', purchases.date) = :year
                        GROUP BY strftime('%Y-%m', purchases.date)
                        ORDER BY strftime('%Y-%m', purchases.date);""", year=reqYear)
    # Render the page
    return render_template("yearly_view.html", years=years, yeaLength=len(summary),
                          summary=summary, details=details, detLength=len(details), reqYear=reqYear)

@app.route('/download', methods=["GET"])
@login_required
def download():
    """ Download a spreadsheet file with the details of a day, month or year """

    period = request.args.get("period")

    # Create and/or open the spreadsheet
    workbook = xlsxwriter.Workbook("static/spreadsheets/" + period +".xlsx")
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})

    # If the period selected is day, it will show a summary of every purchase of the day
    if request.args.get("type") == "day":

        # Query the database for the details
        details = db.execute("""SELECT purchases.date AS Date,
                            purchases.customer AS Customer,
                            SUM(pallets_in_purchase.quantity) AS Pallets,
                            SUM(pallets_in_purchase.unitary_price * pallets_in_purchase.quantity) AS Total,
                            users.username AS User
                        FROM purchases, pallets_in_purchase, users
                        WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                            AND purchases.user = users.user_id
                            AND date(purchases.date) = date(:date)
                        GROUP BY date(purchases.purchase_id)
                        ORDER BY purchases.date;""", date=period)

        # Write the headers
        worksheet.write("A1", "Date", bold)
        worksheet.write("B1", "Customer", bold)
        worksheet.write("C1", "Pallets", bold)
        worksheet.write("D1", "Total", bold)
        worksheet.write("E1", "User", bold)

        # Write the actual details
        for i in range(len(details)):
            worksheet.write("A"+str(i+2), details[i]["Date"])
            worksheet.write("B"+str(i+2), details[i]["Customer"])
            worksheet.write("C"+str(i+2), details[i]["Pallets"])
            worksheet.write("D"+str(i+2), details[i]["Total"])
            worksheet.write("E"+str(i+2), details[i]["User"])

    # If the period selected is month, it will show the total spent in every day of that month
    elif request.args.get("type") == "month":

        # Query the database for the details
        details = db.execute("""SELECT date(purchases.date) AS Period,
                        SUM(pallets_in_purchase.quantity) AS Pallets,
                        SUM(pallets_in_purchase.unitary_price * pallets_in_purchase.quantity) AS Total
                    FROM purchases, pallets_in_purchase, users
                    WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                        AND purchases.user = users.user_id
                        AND strftime('%Y-%m', purchases.date) = :month
                    GROUP BY date(purchases.date)
                    ORDER BY purchases.date;""", month=period)

        # Write the headers
        worksheet.write("A1", "Date", bold)
        worksheet.write("B1", "Pallets", bold)
        worksheet.write("C1", "Total", bold)

        # Write the actual details
        for i in range(len(details)):
            worksheet.write("A"+str(i+2), details[i]["Period"])
            worksheet.write("B"+str(i+2), details[i]["Pallets"])
            worksheet.write("C"+str(i+2), details[i]["Total"])

    # If the period selected is year, it will show the total spent in every month of that year
    elif request.args.get("type") == "year":

        # Query the database for the details
        details = db.execute("""SELECT strftime('%Y-%m', purchases.date) AS Period,
                        SUM(pallets_in_purchase.quantity) AS Pallets,
                        SUM(pallets_in_purchase.unitary_price * pallets_in_purchase.quantity) AS Total
                    FROM purchases, pallets_in_purchase, users
                    WHERE purchases.purchase_id = pallets_in_purchase.purchase_id
                        AND purchases.user = users.user_id
                        AND strftime('%Y', purchases.date) = :year
                    GROUP BY strftime('%Y-%m', purchases.date)
                    ORDER BY strftime('%Y-%m', purchases.date);""", year=period)

        # Write the headers
        worksheet.write("A1", "Month", bold)
        worksheet.write("B1", "Pallets", bold)
        worksheet.write("C1", "Total", bold)

        # Write the actual details
        for i in range(len(details)):
            worksheet.write("A"+str(i+2), details[i]["Period"])
            worksheet.write("B"+str(i+2), details[i]["Pallets"])
            worksheet.write("C"+str(i+2), details[i]["Total"])

    # Close the spreadsheet
    workbook.close()

    # Send the file to the user's device
    spreadsheet_folder = os.path.join(app.root_path, "static/spreadsheets/")
    filename = period +".xlsx"
    return send_from_directory(directory=spreadsheet_folder, filename=filename, as_attachment=True)

@app.route('/buy', methods=["GET", "POST"])
@login_required
def buy():
    """ Buy the pallets and display a table with the details of the purchase"""

    # User reached route via GET
    if request.method == "GET":

        # Render the page with the form to buy the pallets
        return render_template("buy.html")

    # User reached route via POST
    else:

        # Extract the data from the form
        palletsPurchased, moneySpent = 0, 0
        pallets = []
        for i in range(10):
            if (request.form.get("type"+str(i))
                    and request.form.get("quantity"+str(i))
                    and request.form.get("price"+str(i))):
                pallet = {}
                pallet["Type"] = request.form.get("type"+str(i))
                pallet["Quantity"] = int(request.form.get("quantity"+str(i)))
                pallet["Unitary Price"] = float(request.form.get("price"+str(i)))
                pallet["Total"] = pallet["Quantity"] * pallet["Unitary Price"]
                pallets.append(pallet)
                palletsPurchased += pallet["Quantity"]
                moneySpent += pallet["Quantity"] * pallet["Unitary Price"]
        purchase = {}
        purchase["Customer"] = request.form.get("customer")
        purchase["Pallets"] = palletsPurchased
        purchase["Spent"] = moneySpent

        # Insert the purchase summary into the database
        db.execute("""INSERT INTO purchases ('user', 'date', 'customer')
                   VALUES (:user, :date, :customer)""",
                   user=session["user_id"],
                   date=datetime.utcnow(),
                   customer=purchase["Customer"])

        # Check for the id of the most recent insertion in the purchases table
        id = db.execute("""SELECT purchase_id AS Id
                        FROM purchases
                        WHERE purchase_id =
                            (SELECT max(purchase_id) from purchases);""")[0]["Id"]

        # Insert each pallet with it's correspondent quantity and price into
        # the pallets_in_purchase table
        for i in pallets:
            db.execute("""INSERT INTO pallets_in_purchase
                       VALUES (:id, :type, :quantity, :price)""",
                       id=id, type=i["Type"],
                       quantity=i["Quantity"], price=i["Unitary Price"])

        # Render the page with the detail of the purchase
        return render_template("confirmation.html", purchase=purchase, pallets=pallets, length=len(pallets))

if __name__ == "__main__":
    app.run(debug=True)
