import sqlite3
import customtkinter as ctk
import tkinter.messagebox as tkmb

# Set Theme
def setup_theme():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

class Signup(ctk.CTk):
    def __init__(self):
        self.signup_success = None
        self.username = None
        self.password = None
        self.email = None

        super().__init__()
        self.title("Signup")
        self.geometry("1920x1080")
        self.grid_columnconfigure(0, weight=1)

        # Centered Frame
        self.frame = ctk.CTkFrame(self, corner_radius=10)
        self.frame.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)

        # Widgets
        ctk.CTkLabel(self.frame, text="Sign In", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=20)
        self.user = ctk.CTkEntry(self.frame, placeholder_text="Username", width=200)
        self.user.grid(row=1, column=0, pady=10)
        self.pw = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*", width=200)
        self.pw.grid(row=2, column=0, pady=10)
        self.eml = ctk.CTkEntry(self.frame, placeholder_text="Email", width=200)
        self.eml.grid(row=3, column=0, pady=10)
        ctk.CTkButton(self.frame, text="Signup", command=self.signup).grid(row=4, column=0, pady=20)

    def signup(self):
        self.username = self.user.get()
        self.password = self.pw.get()

        self.signup_success = True
        tkmb.showinfo("Success", "Signed Up")
        self.destroy()

        # if self.entered_user == self.username and self.entered_password == self.password:
        #     self.login_success = True
        #     tkmb.showinfo("Success", "Logged In")
        #     self.destroy()
        # else:
        #     self.login_success = False
        #     tkmb.showerror("Error", "Invalid Credentials")

class Login(ctk.CTk):
    def __init__(self, username, password):
        self.login_success = None
        self.username = username
        self.password = password

        super().__init__()
        self.title("Login")
        self.geometry("1920x1080")
        self.grid_columnconfigure(0, weight=1)

        # Centered Frame
        self.frame = ctk.CTkFrame(self, corner_radius=10)
        self.frame.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)

        # Widgets
        ctk.CTkLabel(self.frame, text="Sign In", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=20)
        self.user = ctk.CTkEntry(self.frame, placeholder_text="Username", width=200)
        self.user.grid(row=1, column=0, pady=10)
        self.pw = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*", width=200)
        self.pw.grid(row=2, column=0, pady=10)
        ctk.CTkButton(self.frame, text="Login", command=self.login).grid(row=3, column=0, pady=20)

    def login(self):
        self.entered_user = self.user.get()
        self.entered_password = self.pw.get()

        if self.entered_user == self.username and self.entered_password == self.password:
            self.login_success = True
            tkmb.showinfo("Success", "Logged In")
            self.destroy()
        else:
            self.login_success = False
            tkmb.showerror("Error", "Invalid Credentials")

def run_login_app(user, password):
    setup_theme()
    login = Login(user, password)
    login.mainloop()
    return login.login_success

def run_signup_app():
    setup_theme()
    signup = Signup()
    signup.mainloop()
    return [signup.user, signup.password, signup.email]