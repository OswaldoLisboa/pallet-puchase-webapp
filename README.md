## Pallet Purchase Web app

>This is made as the final project of [CS50's Introduction do Computer Science](https://www.edx.org/course/cs50s-introduction-to-computer-science) course

### Introduction

I've worked in two companies that were dedicated to buy, fix if needed and then sell wood pallets to other companies. In both companies my job consisted, among other things, in writing in a receipt the type of pallet that were purchased and its quantity as well as the client information and the total value of the purchase. At the end of the day, my superior would grab all those receipts and sum the total and write it in a Excel spreadsheet to keep a control of how much money were spent with pallets each day.

That's why I've decided to create this web app. To keep a record on every purchase and the view these by day, month and year, and to automatically export the data to a spreadsheet.

### Implementation

To keep things simple, I've decide to use the tools that were used in the Finance project in the week 8. So I created a virtual environment and installed Flask, to run the backend and the cs50's package, in order to use the database.

##### Website

The website will have seven pages with two functions: store the purchases in a database and view the data. To prevent unwanted people accessing and modifying the database, the user must be logged. There will not be an option to create a user in the website, all accounts must be created by the admin. On top of every page (except the index page and the confirmation page) there will be a navbar so the user can access every page easily.

* __Index__
 The page where the user will be logged in. After that will redirect the user to the daily view of the current day. This is also the page where the user will be redirected if he or she has not log in yet.  

* __Detailed View__
 This page will display the details of a single purchase: the time of the purchase, the customer info, the total of pallets bought, the total paid, the username of the user who registered the purchase and a table containing a row for each pallet type with the quantity, the unitary price and the total price for this individual type.  

* __Daily View__
 This page will show a table with the summary of every purchase of a day. The table must have the following columns: the link to the detailed view of the purchase, time of purchase, customer, total pallets and total price. Before the table, the page must display the total of pallets bought that day, the total money spent, the total number of purchases, a form to change the daily view to another day and a button to download a spreadsheet with that information.  

* __Monthly View__
 This page will work basically like Daily View, but instead of showing a table with every purchase of the day, will show a summary of purchases of every day in that month.  

* __Yearly View__
 Will work just like Monthly View, but instead of showing a table with every purchase of the month, will show a summary of purchases of every month in that year.  

* __Buy__
 This page will show a form containing the following fields: the customer and for each type of pallet the quantity and the unitary price. After the user finishes filling the form, he or she will be redirected to the confirmation page.

* __Confirmation Page__
 This page will look very similar to the Detailed View page. The only difference is that at the end of the page will have a confirmation button so the purchase can be recorded on the database. After the user confirms the purchase, he or she will be redirected to the daily view of the current day.

##### Database

The database should have the following tables:

* __Users__
 This table will store the users information.
 * user_id - Integer, primary key, autoincrement.
 * username - Varchar(64), non nullable.
 * pass_hash - Varchar(255), non nullable.

* __Purchases__
 This table will store all the purchases information.
 * purchase_id - Integer, primary key, autoincrement.
 * user - Integer, non nullable, foreign key references Users.
 * date - timestamp, non nullable, default=CURRENT_TIMESTAMP.
 * customer - Varchar(255), non nullable.

* __Pallets_In_Purchases__
 This table will store what type of pallet were bought in each purchase.
 * purchase_id - Integer, non nullable, foreign key references Purchases.
 * type - Varchar(64), non nullable.
 * quantity - Integer, non nullable.
 * unitary_price - Real, non nullable
