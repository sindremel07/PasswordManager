import tkinter as tk
from tkinter import messagebox
import requests
import os
import json

# Define the URLs for the server endpoints
LOGIN_URL = 'https://localhost:5000/login'
VERIFY_OTP_URL = 'https://localhost:5000/verify-otp'
GET_USERNAME_URL = 'https://localhost:5000/get-username'
REGISTER_URL = 'https://localhost:5000/register-user'
ADDTO_INFODB_URL = 'https://localhost:5000/addto-infodb'
REMOVEFROM_INFODB_URL = 'https://localhost:5000/removefrom-infodb'
UPDATE_INFODB_URL = 'https://localhost:5000/update-infodb'
GETDATA_INFODB_URL = 'https://localhost:5000/getdata-infodb'
VERIFY_ACCOUNT_URL = 'https://localhost:5000/verify-account'

passhidden = True


# To create session files in appdata
appdata_path = os.getenv('APPDATA')
folder_path = os.path.join(appdata_path, 'PasswordManager')

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

SESSION_FILE = os.path.join(folder_path, 'session.json')


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        window_width = 400
        window_height = 500
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.resizable(0, 0)

        self.username = None

        self.load_session() 

        if not self.username:
            self.create_login_widgets()

    def load_session(self):
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as file:
                session_data = json.load(file)
                self.session_id = session_data.get('session_id')
                response = requests.post(GET_USERNAME_URL, json={'session_id': self.session_id}, verify=False)
                self.username = response.json().get('name')

                if self.username:
                    self.password_manager_main()  # Auto-login if session exists

    def save_session(self, session_id):
        with open(SESSION_FILE, 'w') as file:
            json.dump({'session_id': session_id}, file)

    def clear_session(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

    def create_login_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("400x500")

        tk.Label(self.root, text="Log In", font=("",25,"underline")).place(x=75, y=65)
            
        tk.Label(self.root, text="Name").place(x=75, y=125)
        tk.Label(self.root, text="Password").place(x=75, y=155)

        self.name_entry = tk.Entry(self.root)
        self.name_entry.place(x=185, y=125)

        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.place(x=185, y=155)

        tk.Button(self.root, text="Login", command=self.login).place(x=185, y=205)
        tk.Label(self.root, text="Don't have an account?").place(x=140, y=270)
        tk.Button(self.root, text="Register Here", command=self.create_signup_widgets).place(x=165, y=295)

    def create_signup_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Register", font=("",25,"underline")).place(x=75, y=35)
        self.root.geometry("400x500")


        tk.Label(self.root, text="Name").place(x=75, y=95)
        tk.Label(self.root, text="Password").place(x=75, y=125)
        tk.Label(self.root, text="Email").place(x=75, y=155)

        self.name_entry = tk.Entry(self.root)
        self.name_entry.place(x=185, y=95)

        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.place(x=185, y=125)

        self.email_entry = tk.Entry(self.root)
        self.email_entry.place(x=185, y=155)

        tk.Button(self.root, text="Signup", command=self.register).place(x=185, y=205)
        tk.Button(self.root, text="Back to Login", command=self.create_login_widgets).place(x=165, y=295)

    def login(self):
        name = self.name_entry.get()
        password = self.password_entry.get()

        if not name or not password:
            messagebox.showwarning("Input Error", "Name and password are required")
            return

        response = requests.post(LOGIN_URL, json={'name': name, 'password': password}, verify=False)
        if response.status_code == 200:
            self.username = name  # Save the username for OTP verification
            self.create_otp_widgets()
        else:
            messagebox.showerror("Login Failed", response.json().get('message', 'Login failed'))

    def register(self):
        name = self.name_entry.get()
        password = self.password_entry.get()
        self.email = self.email_entry.get()

        if not name or not password or not self.email:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        response = requests.post(REGISTER_URL, json={'name': f'{name}', 'email': f'{self.email}', 'password': f'{password}'}, verify=False)
        if response.status_code == 200:
            self.root.destroy()

            self.create_verification_widget()
        else:
            messagebox.showerror("Login Failed", response.json().get('message', 'Login failed'))

    def create_verification_widget(self):
        self.root = tk.Tk()
        self.root.title("Verify Account")

        self.root.geometry("300x300")

        window_width = 300
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(0, 0)

        label = tk.Label(self.root, text="Verification Key:", font=("Arial", 12))
        label.pack(pady=10)

        self.verification_entry = tk.Entry(self.root)
        self.verification_entry.pack(pady=20)
        

        tk.Button(self.root, text="Verify", command=self.verify_func).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.create_login_widgets).pack(pady=5)

    def verify_func(self):
        verification_key = self.verification_entry.get()
        response = requests.post(VERIFY_ACCOUNT_URL, json={'verification_key': f'{verification_key}', 'email': f'{self.email}'}, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            self.databasekey = data['databasekey']

            self.root.destroy()

            self.create_databasekey_widget()
        else:
            messagebox.showerror("Verification Failed", response.json().get('message', 'Verification failed'))
            
    def create_databasekey_widget(self):
        self.root = tk.Tk()
        self.root.title("Database Key")

        self.root.geometry("300x150")

        window_width = 300
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(0, 0)

        label = tk.Label(self.root, text="Database Key:", font=("Arial", 12))
        label.pack(pady=10)

        self.entry = tk.Entry(self.root, width=40)
        self.entry.insert(0, self.databasekey)
        self.entry.configure(state='readonly')  
        self.entry.pack(pady=10)

        copy_button = tk.Button(self.root, text="Copy", command=self.copy_to_clipboard)
        copy_button.pack(pady=10)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()  
        self.root.clipboard_append(self.databasekey)  
        self.root.destroy()
        main()

    def create_otp_widgets(self):
        # Clear the existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Enter OTP").grid(row=0, column=0, padx=10, pady=10)

        self.otp_entry = tk.Entry(self.root)
        self.otp_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Submit OTP", command=self.verify_otp).grid(row=1, columnspan=2, pady=10)

    def verify_otp(self):
        otp = self.otp_entry.get()

        if not otp:
            messagebox.showwarning("Input Error", "OTP is required")
            return

        response = requests.post(VERIFY_OTP_URL, json={'name': self.username, 'otp': otp}, verify=False)
        if response.status_code == 200:
            data = response.json()  
            fetched_session_id = data['session_id']    
            self.save_session(fetched_session_id)  
            self.session_id = fetched_session_id
            self.password_manager_main()
        else:
            messagebox.showerror("Verification Failed", response.json().get('message', 'OTP verification failed'))

    def hide_show(self):
        global passhidden

        if passhidden == True:
            passhidden = False
            self.passwordEntry.config(show="", text="Hide")
        elif passhidden == False:
            passhidden = True
            self.passwordEntry.config(show="*", text="Show")

    def delete_data(self):
        requests.post(REMOVEFROM_INFODB_URL, json={'session_id': f'{self.session_id}', 'id': f'{self.id}'}, verify=False)

        # To refresh/add new data
        for widget in self.root.winfo_children():
            widget.destroy()
        self.password_manager_main()

    def update_data(self):
        nameValue = self.nameEntry.get()
        passValue = self.passwordEntry.get()
        emailValue = self.emailEntry.get()
        descriptionValue = self.descriptionText.get("1.0", tk.END).strip()       
        websiteValue = self.websiteEntry.get()

        requests.post(UPDATE_INFODB_URL, json={'name': nameValue, 'password': passValue, 'email': emailValue, 'description': descriptionValue, 'title': '', 'website': websiteValue, 'id': self.id, 'session_id': self.session_id}, verify=False)
        

        # To refresh/add new data
        for widget in self.root.winfo_children():
            widget.destroy()
        self.password_manager_main()

    def save_title(self):
        titleValue = self.titleEntry.get()

        requests.post(UPDATE_INFODB_URL, json={'title': titleValue, 'id': self.id, 'session_id': self.session_id}, verify=False)
        
        # To refresh/add new data
        for widget in self.root.winfo_children():
            widget.destroy()

        self.editTitle.destroy()

        self.password_manager_main()

    def edit_title(self):
        titleValue = self.titleLabel.cget("text")

        self.editTitle = tk.Tk()
        self.editTitle.title("Update Title")

        self.editTitle.geometry("300x150")

        window_width = 300
        window_height = 150
        screen_width = self.editTitle.winfo_screenwidth()
        screen_height = self.editTitle.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.editTitle.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.editTitle.resizable(0, 0)

        label = tk.Label(self.editTitle, text="Title:", font=("Arial", 12))
        label.pack(pady=10)

        self.titleEntry = tk.Entry(self.editTitle, width=40)
        self.titleEntry.insert(0, titleValue) 
        self.titleEntry.pack(pady=10)

        save_button = tk.Button(self.editTitle, text="Save", command=self.save_title)
        save_button.pack(pady=10)

    def show_more(self,title, name, password, email, description, infoid, website):
        global passhidden
        passhidden = True

        self.id = infoid

        for widget in self.infoFrame.winfo_children():
            widget.destroy()

        self.titleLabel = tk.Label(self.infoFrame, text=f"{title}", bg="#424242", fg="white")
        self.titleLabel.config(font=("Helvetica", 20, "bold"))
        self.titleLabel.place(relx=0.5, y=20, anchor="center")

        editButton = tk.Button(self.infoFrame,text="Edit Title", command=self.edit_title)
        editButton.place(relx=0.5, y=50, anchor="center")
        
        innerFrame = tk.Frame(self.infoFrame, bg="#5C5C5C", width=320, height=300)
        innerFrame.place(x=15, y=70)  
        
        nameLabel = tk.Label(innerFrame, text="Name", bg="#5C5C5C", fg="white", font=("Helvetica", 10))
        nameLabel.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            
        self.nameEntry = tk.Entry(innerFrame)
        self.nameEntry.insert(0, f"{name}")
        self.nameEntry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        passwordLabel = tk.Label(innerFrame, text="Password", bg="#5C5C5C", fg="white", font=("Helvetica", 10))
        passwordLabel.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            
        self.passwordEntry = tk.Entry(innerFrame, show="*")
        self.passwordEntry.insert(0, f"{password}")
        self.passwordEntry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        showButton = tk.Button(innerFrame,text="Show", command=self.hide_show)
        showButton.grid(row=3, column=4, padx=5, pady=5, sticky="ew")

        emailLabel = tk.Label(innerFrame, text="Email", bg="#5C5C5C", fg="white", font=("Helvetica", 10))
        emailLabel.grid(row=4, column=0, padx=5, pady=5, sticky="w")
            
        self.emailEntry = tk.Entry(innerFrame)
        self.emailEntry.insert(0, f"{email}")
        self.emailEntry.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        websiteLabel = tk.Label(innerFrame, text="Website", bg="#5C5C5C", fg="white", font=("Helvetica", 10))
        websiteLabel.grid(row=5, column=0, padx=5, pady=5, sticky="w")
            
        self.websiteEntry = tk.Entry(innerFrame)
        self.websiteEntry.insert(0, f"{website}")
        self.websiteEntry.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        descriptionFrame = tk.Frame(innerFrame, bg="#5C5C5C")
        descriptionFrame.grid(row=6, column=1, columnspan=3, padx=5, pady=(10, 10), sticky="ew")

        websiteLabel = tk.Label(innerFrame, text="Description", bg="#5C5C5C", fg="white", font=("Helvetica", 10))
        websiteLabel.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        descriptionFrame.grid_columnconfigure(0, weight=1)
        descriptionFrame.grid_rowconfigure(0, weight=1)

        self.descriptionText = tk.Text(descriptionFrame, width=21, height=5, font=("Helvetica", 10), wrap=tk.WORD)
        self.descriptionText.insert(tk.END, f"{description}")
        self.descriptionText.grid(row=0, column=0, sticky="ew")

        scrollbar = tk.Scrollbar(descriptionFrame, command=self.descriptionText.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.descriptionText.config(yscrollcommand=scrollbar.set)

        saveButton = tk.Button(self.infoFrame,text="Save", command=self.update_data)
        saveButton.place(x=270, y=335)

        deleteButton = tk.Button(self.infoFrame,text="Delete", command=self.delete_data)
        deleteButton.place(relx=0.5, anchor="center", y=410)
        
        innerFrame.grid_propagate(False)

    def add_new_save(self):
        infoname = self.name_entry.get()
        infotitle = self.title_entry.get()
        infopass = self.password_entry.get()
        infomail = self.email_entry.get()
        infodesc = self.descriptionText.get("1.0", tk.END).strip()       
        website = self.website_entry.get()
        session_id = self.session_id

        requests.post(ADDTO_INFODB_URL, json={'session_id': f'{session_id}', 'infotitle': f'{infotitle}', 'infoname': f'{infoname}', 'infopass': f'{infopass}', 'infomail': f'{infomail}', 'infodesc': f'{infodesc}', 'website': f'{website}'}, verify=False)
        
        # To refresh/add new data
        for widget in self.root.winfo_children():
            widget.destroy()

        self.addnew.destroy()

        self.password_manager_main()
    def add_new(self):
        self.addnew = tk.Tk()
        self.addnew.title("Add New")

        window_width = 400
        window_height = 500
        screen_width = self.addnew.winfo_screenwidth()
        screen_height = self.addnew.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.addnew.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.addnew.resizable(0, 0)

        tk.Label(self.addnew, text="Add New", font=("",25,"underline")).place(relx=0.5, y=35, anchor="center")

        tk.Label(self.addnew, text="Title").place(x=75, y=95)
        tk.Label(self.addnew, text="Name").place(x=75, y=125)
        tk.Label(self.addnew, text="Password").place(x=75, y=155)
        tk.Label(self.addnew, text="Email").place(x=75, y=185)
        tk.Label(self.addnew, text="Website").place(x=75, y=215)
        tk.Label(self.addnew, text="Description").place(x=75, y=273)

        self.title_entry = tk.Entry(self.addnew)
        self.title_entry.place(x=185, y=95)

        self.name_entry = tk.Entry(self.addnew)
        self.name_entry.place(x=185, y=125)

        self.password_entry = tk.Entry(self.addnew)
        self.password_entry.place(x=185, y=155)

        self.email_entry = tk.Entry(self.addnew)
        self.email_entry.place(x=185, y=185)

        self.website_entry = tk.Entry(self.addnew)
        self.website_entry.place(x=185, y=215)

        descriptionFrame = tk.Frame(self.addnew)
        descriptionFrame.place(x=185, y=245)

        descriptionFrame.grid_columnconfigure(0, weight=1)
        descriptionFrame.grid_rowconfigure(0, weight=1)

        self.descriptionText = tk.Text(descriptionFrame, width=21, height=5, font=("Helvetica", 10), wrap=tk.WORD)
        self.descriptionText.grid(row=0, column=0, sticky="ew")

        scrollbar = tk.Scrollbar(descriptionFrame, command=self.descriptionText.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.descriptionText.config(yscrollcommand=scrollbar.set)

        tk.Button(self.addnew, text="Add", command=self.add_new_save).place(relx=0.5, anchor="center", y=365)


    def password_manager_main(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        window_width = 900
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        response = requests.post(GETDATA_INFODB_URL, json={'session_id': f'{self.session_id}'}, verify=False)

        tk.Label(self.root, text=f"Hello {self.username}").place(x=15, y=15)

        tk.Button(self.root, text="Log Out", command=self.logout).place(x=15, y=35)

        tk.Button(self.root, text="Add New", command=self.add_new).place(x=15, y=75)
        
        canvas = tk.Canvas(self.root, width=300, height=450)
        canvas.place(x=230, y=5)
        
        mainframe = tk.Frame(canvas)

        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.place(x=480, y=5, height=430)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=mainframe, anchor="nw")

        self.infoFrame = tk.Frame(self.root, bg="#424242", width=350, height=430)
        self.infoFrame.place(x=530, y=15)

        if response.status_code == 200:
            data = response.json()
            data_string = data['data']
            data_string = data_string.replace("'", '"')
            data_list = json.loads(data_string)

            for item in data_list:

                frame = tk.Frame(mainframe, bg="#424242", width=250, height=70, cursor="hand2")
                frame.pack(padx=10, pady=10)

                # Prevent the frame from resizing to fit the children
                frame.pack_propagate(False)

                frame.bind("<Button-1>", lambda event, title=item['title'], name=item['name'], password=item['password'], email=item['email'], description=item['description'], infoid=item['id'], website=item['website']: self.show_more(title, name, password, email, description, infoid, website))

                label_account = tk.Label(frame, text=f"{item['title']}", fg="White", bg="#424242", font=("Arial", 12))
                label_account.config(font=("Helvetica", 12, "bold"))
                label_account.pack(pady=(10, 0), padx=50)

                label_email = tk.Label(frame, text=f"{item['email']}", fg="White", bg="#424242", font=("Arial", 10))
                label_email.pack(pady=(5, 10), padx=50)

                # Bind both labels to the event
                label_account.bind("<Button-1>", lambda event, title=item['title'], name=item['name'], password=item['password'], email=item['email'], description=item['description'], infoid=item['id'], website=item['website']: self.show_more(title, name, password, email, description, infoid, website))
                label_email.bind("<Button-1>", lambda event, title=item['title'], name=item['name'], password=item['password'], email=item['email'], description=item['description'], infoid=item['id'], website=item['website']: self.show_more(title, name, password, email, description, infoid, website))

    def logout(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.clear_session()  # Clear session on logout
        self.username = None
        # Return to login screen
        self.create_login_widgets()

def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()