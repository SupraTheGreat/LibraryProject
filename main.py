from importlib.resources import contents
from flask import Flask, jsonify, request, render_template, redirect, url_for
import sqlite3
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import datetime
import random

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(receiver, subject, content):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# os.remove('staff.db')
# os.remove('student.db')
# os.remove('books.db')
# exit()

if not os.path.isfile('staff.db'):

    # Staff table
    conn = sqlite3.connect('staff.db')
    conn.execute('''CREATE TABLE STAFF
            (ID INTEGER PRIMARY KEY     NOT NULL UNIQUE,
            USER           TEXT    NOT NULL UNIQUE,
            PASSWORD       TEXT    NOT NULL,
            EMAIL          TEXT    NOT NULL);''')
    conn.close()

if not os.path.isfile('student.db'):
    conn = sqlite3.connect("student.db")
    conn.execute('''CREATE TABLE STUDENTS
                (ID INTEGER PRIMARY KEY     NOT NULL UNIQUE,
                USER           TEXT    NOT NULL UNIQUE,
                PASSWORD       TEXT    NOT NULL,
                EMAIL          TEXT    NOT NULL);''')

    # Checked out books table
    conn.execute('''CREATE TABLE STUDENTBOOKS 
        (BOOK_ID        INT     NOT NULL UNIQUE,
        STUDENT_ID     INT     NOT NULL,
        USER           TEXT    NOT NULL,
        TITLE          TEXT    NOT NULL,
        DUE_DATE       TEXT    NOT NULL,
        USER_EMAIL     TEXT    NOT NULL);''')

if not os.path.isfile('books.db'):

    # Books table
    conn = sqlite3.connect('books.db')
    conn.execute('''CREATE TABLE BOOKS
                (ID INTEGER PRIMARY KEY     NOT NULL UNIQUE,
                TITLE          TEXT    NOT NULL,
                AUTHOR         TEXT    NOT NULL,
                AVAILABLE      INT     NOT NULL);''')
    conn.close()

list = []
studentlist = []
studentid = 0
duplicate = False
login = "none"
info = []
otp_storage = {}

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    if login != "student":
        return "Unauthorized", 401
    return render_template("dashboard.html", username=info[1])

@app.route('/staff_dashboard')
def staff_dashboard():

    conn = sqlite3.connect('books.db')
    total_books = conn.execute(
        "SELECT COUNT(*) FROM BOOKS"
    ).fetchone()[0]
    conn.close()

    conn = sqlite3.connect('student.db')
    total_students = conn.execute(
        "SELECT COUNT(*) FROM STUDENTS"
    ).fetchone()[0]
    conn.close()

    conn = sqlite3.connect('student.db')
    checked_out = conn.execute(
        "SELECT COUNT(*) FROM STUDENTBOOKS"
    ).fetchone()[0]
    conn.close()

    return render_template(
        "staff_dashboard.html",
        username=info[1],
        total_books=total_books,
        total_students=total_students,
        checked_out=checked_out
    )

@app.route('/logout')
def logout():
    global login, info

    login = "none"
    info = []

    return redirect(url_for('home'))

@app.route('/staffsignup', methods=['GET', 'POST'])
def staffsignup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        conn = sqlite3.connect("staff.db")
        try:
            conn.execute(
                "INSERT INTO STAFF (USER, PASSWORD, EMAIL) VALUES (?, ?, ?)",
                (username, password, email)
            )
            conn.commit()
        except:
            conn.close()
            return render_template("staff_signup.html", message="Username already exists"), 409

        return redirect(url_for("stafflogin"))

    return render_template("staff_signup.html"), 200

# @app.route('/signupstaff', methods=['POST'])
# def signupstaff():
#     data = request.get_json()
#     conn = sqlite3.connect("staff.db")
#     try:
#         conn.execute(f"INSERT INTO STAFF (USER,PASSWORD,EMAIL) \
#                       VALUES ('{data.get("username")}', '{data.get("password")}', '{data.get("email")}')")
#         conn.commit()
#     except:
#         conn.close()
#         return jsonify({"status": "ERROR: Username already exists"}), 409
#     return jsonify({'status': f'Account successfully created.'}), 201

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        conn = sqlite3.connect('student.db')
        try:
            conn.execute(
                "INSERT INTO STUDENTS (USER, PASSWORD, EMAIL) VALUES (?, ?, ?)",
                (username, password, email)
            )
            conn.commit()
        except:
            conn.close()
            return "Username already exists.", 409
        return "Account successfully created. Please login.", 200
    return render_template("signup.html")

@app.route('/stafflogin', methods=['GET', 'POST'])
def stafflogin():
    global login, info

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect('staff.db')
        cursor = conn.execute("SELECT id, user, password, email FROM STAFF")

        for row in cursor:
            if row[1] == username and row[2] == password:
                login = "staff"
                info = row
                return redirect(url_for("staff_dashboard"))

        return render_template("stafflogin.html", message="Invalid credentials"), 401

    return render_template("stafflogin.html"), 200

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    global otp_storage

    if request.method == "POST":
        email = request.form["email"]
        found = False
        conn = sqlite3.connect('student.db')
        cursor = conn.execute(
            "SELECT email FROM STUDENTS"
        )

        for row in cursor:
            if row[0] == email:
                found = True
        conn.close()

        if not found:
            return render_template(
                "forgot_password.html",
                message="Email not found."
            )

        otp = str(random.randint(100000, 999999))
        otp_storage[email] = otp

        send_email(
            email,
            "Password Reset Code",
            f"Your verification code is: {otp}"
        )

        return redirect(
            url_for(
                "verifyotp",
                email=email
            )
        )

    return render_template("forgot_password.html")

@app.route('/verifyotp/<email>', methods=['GET', 'POST'])
def verifyotp(email):

    global otp_storage

    if request.method == "POST":

        otp = request.form["otp"]

        if otp_storage.get(email) == otp:

            return redirect(
                url_for(
                    "resetpassword",
                    email=email
                )
            )

        return render_template(
            "verify_otp.html",
            email=email,
            message="Incorrect OTP."
        )

    return render_template(
        "verify_otp.html",
        email=email
    )

@app.route('/resetpassword/<email>', methods=['GET', 'POST'])
def resetpassword(email):

    global otp_storage

    if request.method == "POST":

        new_password = request.form["password"]

        conn = sqlite3.connect('student.db')

        conn.execute(
            "UPDATE STUDENTS SET PASSWORD = ? WHERE EMAIL = ?",
            (new_password, email)
        )

        conn.commit()
        conn.close()

        otp_storage.pop(email, None)

        return redirect(url_for("loginstudent"))

    return render_template(
        "reset_password.html",
        email=email
    )

# @app.route('/loginstaff', methods=['POST'])
# def loginstaff():
#     global login, info
#     data = request.get_json()
#     conn = sqlite3.connect('staff.db')
#     cursor = conn.execute("SELECT id, user, password from STAFF")
#     for row in cursor:
#         if row[1] == username and row[2] == password:
#             return jsonify({'status': 'Login successful.'}), 200
#     conn.close()
#     return jsonify({'status': 'Login failed. Incorrect username/password.'}), 401

@app.route('/login', methods=['GET', 'POST'])
def loginstudent():
    global login, info

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect('student.db')
        cursor = conn.execute("SELECT id, user, password, email FROM STUDENTS")

        for row in cursor:
            if row[1] == username and row[2] == password:
                login = "student"
                info = row
                return redirect(url_for("dashboard"))

        return "Invalid username or password"

    return render_template("login.html")

@app.route('/getstaff', methods=['GET'])
def getstaff():
    if login == "staff":
        global list
        list = []
        conn = sqlite3.connect('staff.db')
        cursor = conn.execute("SELECT user, password from STAFF")
        for row in cursor:
            list.append(["Username: " + row[0], "Password: " + row[1]])
        return jsonify({"data": list}), 200
    return jsonify({"status": "Permission denied."}), 401

@app.route('/getstudents', methods=['GET'])
def getstudents():
    global list
    list = []
    conn = sqlite3.connect('student.db')
    cursor = conn.execute("SELECT user, password, email from STUDENTS")
    for row in cursor:
        list.append({
            "user": row[0],
            "password": row[1],
            "email": row[2]
        })
    return render_template("getstudents.html", students=list), 200

@app.route('/getusercheckedout', methods=['GET'])
def getusercheckedout():
    global info
    list = []
    conn = sqlite3.connect('student.db')
    cursor = conn.execute("SELECT book_id, student_id, title from STUDENTBOOKS")
    for row in cursor:
        if info[0] == row[1]:
            list.append({
                "id": row[0],
                "title": row[2]
            })
    return render_template("getusercheckedout.html", books=list), 200

@app.route('/createbook', methods=['GET', 'POST'])
def createbook():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        copies = request.form["copies"]
        if login == "staff":
            pass
        else:
            return render_template("createbook.html", message="Unauthorized request"), 401
        conn = sqlite3.connect('books.db')
        # if True:
        try:
            for i in range(int(copies)):
                conn.execute(
                    "INSERT INTO BOOKS (TITLE, AUTHOR, available) VALUES (?, ?, ?)",
                    (title, author, 1)
                )
                conn.commit()
        except:
            conn.close()
            return render_template("createbook.html", message="Something went wrong"), 500
        return redirect(url_for("staff_dashboard"))
    return render_template("createbook.html"), 200

@app.route('/deletebookbytitle/<string:title>', methods=['DELETE'])
def deletebookbytitle(title):
    if login == "staff":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401
    conn = sqlite3.connect('books.db')
    conn.execute(f"DELETE from BOOKS where TITLE = {title};")
    conn.commit()
    conn.close()
    return jsonify({'status': 'Operation complete.'})

@app.route('/deletebookbyid/<string:id>', methods=['DELETE'])
def deletebookbyid(id):
    if login == "staff":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401
    conn = sqlite3.connect('books.db')
    conn.execute(f"DELETE from BOOKS where ID = {id};")
    conn.commit()
    conn.close()
    return jsonify({'status': 'Operation complete.'})

@app.route('/deletebookbyauthor/<string:author>', methods=['DELETE'])
def deletebookbyauthor(author):
    if login == "staff":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401
    conn = sqlite3.connect('books.db')
    conn.execute(f"DELETE from BOOKS where AUTHOR = {author};")
    conn.commit()
    conn.close()
    return jsonify({'status': 'Operation complete.'})

@app.route('/deletebook', methods=['GET', 'POST'])
def deletebook():
    if login != "staff":
        return "Unauthorized", 401

    if request.method == "POST":
        book_id = request.form["id"]

        conn = sqlite3.connect('books.db')

        try:
            conn.execute("DELETE FROM BOOKS WHERE ID = ?", (book_id,))
            conn.commit()
        except:
            conn.close()
            return render_template(
                "deletebook.html",
                message="Error deleting book."
            )

        conn.close()

        return render_template(
            "deletebook.html",
            message="Book deleted successfully."
        )

    return render_template("deletebook.html")

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if login != "student":
        return "Unauthorized", 401

    if request.method == "POST":

        title = request.form["title"]

        checkout_date = datetime.datetime.now()

        book_id = 0

        conn = sqlite3.connect('books.db')

        cursor = conn.execute(
            "SELECT id, title, available FROM BOOKS"
        )

        for row in cursor:
            if row[1] == title and row[2] == 1:
                book_id = row[0]

        if book_id == 0:
            conn.close()

            return render_template(
                "checkout.html",
                message="Book unavailable."
            )

        conn.close()

        conn = sqlite3.connect('student.db')

        conn.execute(
            "INSERT INTO STUDENTBOOKS (BOOK_ID, STUDENT_ID, USER, TITLE, DUE_DATE, USER_EMAIL) VALUES (?, ?, ?, ?, ?, ?)",
            (
                book_id,
                info[0],
                info[1],
                title,
                str(checkout_date + datetime.timedelta(days=14)),
                info[3]
            )
        )

        conn.commit()
        conn.close()

        conn = sqlite3.connect('books.db')

        conn.execute(
            "UPDATE BOOKS SET AVAILABLE = 0 WHERE ID = ?",
            (book_id,)
        )

        conn.commit()
        conn.close()

        return render_template(
            "checkout.html",
            message="Book checked out successfully."
        )

    return render_template("checkout.html")

@app.route('/returnbook', methods=['GET', 'POST'])
def returnbook():

    if login != "student":
        return "Unauthorized", 401

    if request.method == "POST":

        title = request.form["title"]

        book_id = 0

        conn = sqlite3.connect('student.db')

        cursor = conn.execute(
            "SELECT book_id, title FROM STUDENTBOOKS"
        )

        for row in cursor:
            if row[1] == title:
                book_id = row[0]

        if book_id == 0:
            conn.close()

            return render_template(
                "returnbook.html",
                message="Book not checked out."
            )

        conn.execute(
            "DELETE FROM STUDENTBOOKS WHERE BOOK_ID = ?",
            (book_id,)
        )

        conn.commit()
        conn.close()

        conn = sqlite3.connect('books.db')

        conn.execute(
            "UPDATE BOOKS SET AVAILABLE = 1 WHERE ID = ?",
            (book_id,)
        )

        conn.commit()
        conn.close()

        return render_template(
            "returnbook.html",
            message="Book returned successfully."
        )

    return render_template("returnbook.html")

@app.route('/emaild', methods=['POST'])
def emaild():
    if request.method == "POST":

        title = request.form["title"]
    data = request.get_json()
    send_email(data.get("email"), data.get("subject"), data.get("content"))
    return jsonify({'status': f'Email successfully sent to {data.get("email")}'}), 200

@app.route('/sendemail', methods=['GET', 'POST'])
def sendemail():
    if login != "staff":
        return "Unauthorized", 401
    print("test")
    if request.method == "POST":
        emailid = request.form["email"]
        subject = request.form["subject"]
        content = request.form["content"]
        send_email(emailid, subject, content)
        return render_template(
            "sendemail.0.html",
            message="Email sent successfully."
        )

    return render_template("sendemail.html")

@app.route('/checkin', methods=['DELETE'])
def checkin():
    if login == "student":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401

    global info
    data = request.get_json()

    book_id = 0
    conn = sqlite3.connect('student.db')
    cursor = conn.execute("SELECT book_id, student_id, user, title from STUDENTBOOKS")
    for row in cursor:
        if row[3] == data.get("title"):
            book_id = row[0]
    if book_id == 0:
        conn.close()
        print("ERROR1")
        return jsonify({'status': "ERROR: You cannot return a book that isn't checked out."}), 412

    conn = sqlite3.connect('student.db')
    # if True:
    try:
        conn.execute(f"DELETE from STUDENTBOOKS where BOOK_ID = {book_id};")
        conn.commit()
    except:
       conn.close()
       print("ERROR2")
       return jsonify({'status': "ERROR: You cannot return a book that isn't checked out."}), 412
    conn.close()
    conn = sqlite3.connect('books.db')
    conn.execute(f"UPDATE BOOKS set AVAILABLE = 1 where ID = {book_id}")
    conn.commit()
    conn.close()
    return jsonify({'status': 'Operation complete.'}), 200

@app.route('/getcheckedout', methods=['GET'])
def getcheckedout():
    if login == "staff":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401
    global info
    lst = []
    conn = sqlite3.connect('student.db')
    cursor = conn.execute("SELECT book_id, student_id, user, title, due_date from STUDENTBOOKS")
    for row in cursor:
        lst.append([("Book ID: " + str(row[0])), ("Book Title: " + row[3]), ("Borrower Username: " + row[2]), ("Borrower ID: " + str(row[1])), ("Book Due Date: " + row[4])])
    total = len(lst)
    lst.insert(0, "Total Number of Checked Out Books: " + str(total))
    return jsonify({"data": lst}), 200

@app.route('/allbooks', methods=['GET'])
def allbooks():
    global list
    list = []
    conn = sqlite3.connect('books.db')
    cursor = conn.execute("SELECT id, title, author, available from BOOKS")
    for row in cursor:
        availability = "Available" if row[3] == 1 else "Checked Out"

        list.append({
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "availability": availability
        })
    return render_template("allbooks.html", books=list)

@app.route('/allbooksstaff', methods=['GET'])
def allbooksstaff():
    global list
    list = []
    conn = sqlite3.connect('books.db')
    cursor = conn.execute("SELECT id, title, author, available from BOOKS")
    for row in cursor:
        checkedoutby = "N/A"
        checkedoutbyid = "N/A"
        if row[3] == 1:
            availability = "Available"
        else:
            availability = "Checked Out"
            conn2 = sqlite3.connect('student.db')
            cursor2 = conn2.execute(f"SELECT student_id, user FROM STUDENTBOOKS WHERE BOOK_ID = {row[0]}")
            for row2 in cursor2:
                checkedoutby = row2[1]
                checkedoutbyid = row2[0]

        list.append({
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "availability": availability,
            "checked_out_by": checkedoutby,
            "checked_out_by_id": checkedoutbyid
        })
    return render_template("allbooksstaff.html", books=list)

@app.route('/availablebooks')
def availablebooks():

    books = []

    conn = sqlite3.connect('books.db')
    cursor = conn.execute(
        "SELECT id, title, author FROM BOOKS WHERE AVAILABLE = 1"
    )

    for row in cursor:
        books.append({
            "id": row[0],
            "title": row[1],
            "author": row[2]
        })

    conn.close()

    return render_template("availablebooks.html", books=books)

@app.route('/getbookbyid/<int:id>', methods=['GET'])
def getbookbyid(id):
    global list
    list = []
    conn = sqlite3.connect('books.db')
    cursor = conn.execute(f"SELECT id, title, author, available from BOOKS where ID = {id};")
    for row in cursor:
        list.append(["ID: " + str(row[0]), "Title: " + row[1], "Author: " + row[2], "Availability: " + str(row[3])])
    return jsonify({"data": list}), 200

@app.route('/getbookbytitle/<string:title>', methods=['GET'])
def getbookbytitle(title):
    global list
    list = []
    conn = sqlite3.connect('books.db')
    cursor = conn.execute(f"SELECT id, title, author, available from BOOKS where TITLE = {title};")
    for row in cursor:
        list.append(["ID: " + str(row[0]), "Title: " + row[1], "Author: " + row[2], "Availability: " + str(row[3])])
    return jsonify({"data": list}), 200

@app.route('/getbookbyauthor/<string:author>', methods=['GET'])
def getbookbyauthor(author):
    global list
    list = []
    conn = sqlite3.connect('books.db')
    cursor = conn.execute(f"SELECT id, title, author, available from BOOKS where AUTHOR = {author};")
    for row in cursor:
        list.append(["ID: " + str(row[0]), "Title: " + row[1], "Author: " + row[2], "Availability: " + str(row[3])])
    return jsonify({"data": list}), 200

@app.route('/update', methods=['PUT'])
def update():
    data = request.get_json()

    conn = sqlite3.connect('test.db')
    conn.execute(f"UPDATE SCHOOL set NAME = '{data.get('name')}' where ID = {data.get('id')}")
    conn.execute(f"UPDATE SCHOOL set EMAIL = '{data.get('email')}' where ID = {data.get('id')}")
    conn.execute(f"UPDATE SCHOOL set PHONE = '{data.get('phone')}' where ID = {data.get('id')}")
    conn.commit()
    conn.close()

    return jsonify({'status': 'Operation complete.'})

@app.route('/delete/<string:id>', methods=['DELETE'])
def delete(id):
    conn = sqlite3.connect('test.db')
    conn.execute(f"DELETE from SCHOOL where ID = {id};")
    conn.commit()
    conn.close()
    return jsonify({'status': 'Operation complete.'})

if __name__ == '__main__':
    app.run(debug=True)