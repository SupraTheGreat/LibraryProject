from flask import Flask, jsonify, request, render_template, redirect, url_for
import sqlite3
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import datetime

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
    if login != "staff":
        return "Unauthorized", 401
    return render_template("staff_dashboard.html", username=info[1])

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
    if login == "staff":
        global list
        list = []
        conn = sqlite3.connect('student.db')
        cursor = conn.execute("SELECT user, password from STUDENTS")
        for row in cursor:
            list.append(["Username: " + row[0], "Password: " + row[1]])
        return jsonify({"data": list}), 200
    return jsonify({"status": "Permission denied."}), 401

@app.route('/createbook', methods=['POST'])
def createbook():
    if login == "staff":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401
    data = request.get_json()
    conn = sqlite3.connect('books.db')
    # if True:
    try:
        for i in range(int(data.get("copies"))):
            conn.execute(
                "INSERT INTO BOOKS (TITLE, AUTHOR, available) VALUES (?, ?, ?)",
                (data.get("title"), data.get("author"), 1)
            )
            conn.commit()
    except:
        conn.close()
        return jsonify({"status": "ERROR: Something went wrong"}), 500
    conn.close()
    return jsonify({'status': f'Book successfully created.'}), 200

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

@app.route('/checkout', methods=['POST'])
def checkout():
    if login == "student":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401

    global info
    data = request.get_json()
    checkout_date = datetime.datetime.now()
    book_id = 0
    conn = sqlite3.connect('books.db')
    cursor = conn.execute("SELECT id, title, author, available from BOOKS")
    for row in cursor:
        if row[1] == data.get("title") and row[3] == 1:
            book_id = row[0]
    if book_id == 0:
        conn.close()
        return jsonify({'status': 'ERROR: Book not available for checkout.'}), 412

    conn = sqlite3.connect('student.db')
    if True:
    # try:
        conn.execute(f"INSERT INTO STUDENTBOOKS (BOOK_ID,STUDENT_ID, USER, TITLE, DUE_DATE, USER_EMAIL) \
                              VALUES ({book_id}, {info[0]}, '{info[1]}', '{data.get('title')}', '{checkout_date + datetime.timedelta(days=14)}', '{info[3]}')")
        conn.commit()
    # except:
    #     conn.close()
    #     return jsonify({'status': 'ERROR: Book not available for checkout.'}), 412
    conn.close()
    conn = sqlite3.connect('books.db')
    conn.execute(f"UPDATE BOOKS set AVAILABLE = 0 where ID = {book_id}")
    conn.commit()
    conn.close()
    return jsonify({'status': 'Operation complete.'}), 200

@app.route('/email', methods=['POST'])
def email():
    if login == "staff":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401
    data = request.get_json()
    send_email(data.get("email"), data.get("subject"), data.get("content"))
    return jsonify({'status': f'Email successfully sent to {data.get("email")}'}), 200

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

@app.route('/getusercheckedout', methods=['GET'])
def getusercheckedout():
    if login == "student":
        pass
    else:
        return jsonify({'status': 'Permission denied.'}), 401
    global info
    lst = []
    conn = sqlite3.connect('student.db')
    cursor = conn.execute("SELECT book_id, student_id, user, title from STUDENTBOOKS")
    for row in cursor:
        if info[0] == row[1]:
            lst.append([("ID: " + str(row[0])), ("Title: " + row[3])])
    total = len(lst)
    lst.insert(0, f"Total Number of Checked Out Books: {str(total)}")
    return jsonify({"data": lst}), 200

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
        list.append(["ID: " + str(row[0]), "Title: " + row[1], "Author: " + row[2], "Availability: " + str(row[3])])
    return jsonify({"data": list}), 200

@app.route('/allavailable', methods=['GET'])
def allavailable():
    global list
    list = []
    conn = sqlite3.connect('books.db')
    cursor = conn.execute("SELECT id, title, author, available from BOOKS")
    for row in cursor:
        if row[3] == 1:
            list.append(["ID: " + str(row[0]), "Title: " + row[1], "Author: " + row[2]])
    return jsonify({"data": list}), 200

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