import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import sqlite3
import datetime

# if not os.path.isfile('staff.db'):
#     # Staff table
#     conn = sqlite3.connect('staff.db')
#     conn.execute('''CREATE TABLE STAFF
#             (ID INTEGER PRIMARY KEY     NOT NULL UNIQUE,
#             USER           TEXT    NOT NULL UNIQUE,
#             PASSWORD       TEXT    NOT NULL);''')
#     conn.close()
#
# if not os.path.isfile('student.db'):
#     conn = sqlite3.connect("student.db")
#     conn.execute('''CREATE TABLE STUDENTS
#                 (ID INTEGER PRIMARY KEY     NOT NULL UNIQUE,
#                 USER           TEXT    NOT NULL UNIQUE,
#                 PASSWORD       TEXT    NOT NULL);''')
#
#     # Checked out books table
#     conn.execute('''CREATE TABLE STUDENTBOOKS
#         (BOOK_ID        INT     NOT NULL UNIQUE,
#         STUDENT_ID     INT     NOT NULL,
#         USER           TEXT    NOT NULL,
#         TITLE          TEXT    NOT NULL,
#         DUE_DATE       TEXT    NOT NULL,
#         USER_EMAIL     TEXT    NOT NULL);''')
#
# if not os.path.isfile('books.db'):
#
#     # Books table
#     conn = sqlite3.connect('books.db')
#     conn.execute('''CREATE TABLE BOOKS
#                 (ID INTEGER PRIMARY KEY     NOT NULL UNIQUE,
#                 TITLE          TEXT    NOT NULL,
#                 AUTHOR         TEXT    NOT NULL,
#                 AVAILABLE      INT     NOT NULL);''')
#     conn.close()

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

# import datetime
#
# now = datetime.datetime.now()
#
#
# conn = sqlite3.connect('student.db')
# cursor = conn.execute("SELECT book_id, student_id, user, title, due_date, user_email from STUDENTBOOKS")
# for row in cursor:
#     dt = datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
#     if now > dt:
#         send_email(row[5], "Notice: Book Overdue", f"Hello {row[2]}, your book {row[3]} is now overdue. Please return this book quickly.")
# conn.close()

# import schedule
# import time
#
# def job():
#     print("Running every hour")
#
# schedule.every().day.at("00:00").do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)