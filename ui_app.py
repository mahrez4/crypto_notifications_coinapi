import customtkinter as ctk
import tkinter as tk
import threading
from tkinter import messagebox
from ui_user_handling import UserManager
from cli_app import *

API_KEY = 'fceff4f8-c486-4a17-ae1f-312abd7a9858'

class CryptoAlertApp:
    def __init__(self):
        ctk.set_appearance_mode("dark") 
        ctk.set_default_color_theme("blue")  
        self.root = ctk.CTk()
        self.root.title("Crypto notifications System")
        self.root.geometry("1024x768")
        self.user_manager = UserManager()
        self.api = CoinAPI(API_KEY)
        self.current_user = None
        self.manager = None
        self.create_login_screen()

    def start_monitoring(self):
        """Start monitoring prices in the background."""
        self.monitoring_thread = threading.Thread(target=monitor_prices, args=(self.api, self.manager), daemon=True)
        self.monitoring_thread.start()

    def create_login_screen(self):
        self.clear_window()
        ctk.CTkLabel(self.root, text="Login", font=("Arial", 20)).pack(pady=10)

        self.username_entry = ctk.CTkEntry(self.root, placeholder_text="Username")
        self.password_entry = ctk.CTkEntry(self.root, placeholder_text="Password", show="*")

        self.username_entry.pack(pady=5)
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self.root, text="Login", command=self.login).pack(pady=5)
        ctk.CTkButton(self.root, text="Sign Up", command=self.create_signup_screen).pack(pady=5)

        self.root.mainloop()

    def create_signup_screen(self):
        self.clear_window()
        ctk.CTkLabel(self.root, text="Sign Up", font=("Arial", 20)).pack(pady=10)

        self.signup_username = ctk.CTkEntry(self.root, placeholder_text="Username")
        self.signup_password = ctk.CTkEntry(self.root, placeholder_text="Password", show="*")

        self.signup_username.pack(pady=5)
        self.signup_password.pack(pady=5)

        ctk.CTkButton(self.root, text="Sign Up", command=self.sign_up).pack(pady=5)
        ctk.CTkButton(self.root, text="Back", command=self.create_login_screen).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = self.user_manager.login(username, password)
        if success:
            self.current_user = username
            self.create_alert_screen()
            file_path = username+"_alerts.json"
            print(file_path)
            self.manager = AlertManager(file_path)
            self.start_monitoring()
        else:
            messagebox.showerror("Login Failed", message)

    def sign_up(self):
        username = self.signup_username.get()
        password = self.signup_password.get()
        success, message = self.user_manager.sign_up(username, password)
        if success:
            messagebox.showinfo("Sign-Up Success", message)
            self.create_login_screen()
        else:
            messagebox.showerror("Sign-Up Failed", message)

    def create_alert_screen(self):
        self.clear_window()
        ctk.CTkLabel(self.root, text=f"Welcome {self.current_user}!", font=("Arial", 20)).pack(pady=10)

        ctk.CTkButton(self.root, text="Create Alert", command=self.create_alert_form).pack(pady=5)
        ctk.CTkButton(self.root, text="List Alerts", command=self.list_alerts).pack(pady=5)
        ctk.CTkButton(self.root, text="Exit", command=self.root.quit).pack(pady=5)

    def create_alert_form(self):
        self.clear_window()
        ctk.CTkLabel(self.root, text="Create Alert", font=("Arial", 20)).pack(pady=10)

        self.alert_type = ctk.CTkEntry(self.root, placeholder_text="Type (basic/percentage_change)", width=400)
        self.symbol_entry = ctk.CTkEntry(self.root, placeholder_text="Symbol (e.g., BTC)", width=400)
        self.condition_entry = ctk.CTkEntry(self.root, placeholder_text="Condition (above/below or increase/decrease)", width=400)
        self.value_entry = ctk.CTkEntry(self.root, placeholder_text="Value (USD or Percentage)", width=400)
        self.email_entry = ctk.CTkEntry(self.root, placeholder_text="Email", width=400)

        self.alert_type.pack(pady=5)
        self.symbol_entry.pack(pady=5)
        self.condition_entry.pack(pady=5)
        self.value_entry.pack(pady=5)
        self.email_entry.pack(pady=5)

        ctk.CTkButton(self.root, text="Save", command=self.save_alert).pack(pady=5)
        ctk.CTkButton(self.root, text="Back", command=self.create_alert_screen).pack(pady=5)

    def save_alert(self):
        alert_type = self.alert_type.get()
        symbol = self.symbol_entry.get()
        condition = self.condition_entry.get()
        value = self.value_entry.get()
        email = self.email_entry.get() or None
        alert = Alert(alert_type, symbol, condition, value, email)
        self.manager.create_alert(alert)
        messagebox.showinfo("Success", "Alert created successfully!")
        self.create_alert_screen()

    def list_alerts(self):
        self.clear_window()
        ctk.CTkLabel(self.root, text="Alerts List", font=("Arial", 20)).pack(pady=10)

        alerts = self.manager.list_alerts()
        for i, alert in enumerate(alerts):
            ctk.CTkLabel(self.root, text=f"{i}: {alert}").pack(pady=2)
            ctk.CTkButton(self.root, text="Delete", command=lambda i=i: self.delete_alert(i)).pack(pady=2)
            ctk.CTkButton(self.root, text="Modify", command=lambda i=i: self.modify_alert(i)).pack(pady=2)

        ctk.CTkButton(self.root, text="Back", command=self.create_alert_screen).pack(pady=5)

    def delete_alert(self, index):
        self.manager.delete_alert(index)
        messagebox.showinfo("Success", "Alert deleted successfully!")
        self.list_alerts()

    def modify_alert(self, index):
        alert = self.manager.get_alert_by_index(index)
        self.clear_window()
        ctk.CTkLabel(self.root, text="Modify Alert", font=("Arial", 20)).pack(pady=10)

        self.condition_entry = ctk.CTkEntry(self.root, placeholder_text="Condition", textvariable=tk.StringVar(value=alert.condition))
        self.value_entry = ctk.CTkEntry(self.root, placeholder_text="Value", textvariable=tk.StringVar(value=alert.value))
        self.email_entry = ctk.CTkEntry(self.root, placeholder_text="Email (Optional)", textvariable=tk.StringVar(value=alert.email))

        self.condition_entry.pack(pady=5)
        self.value_entry.pack(pady=5)
        self.email_entry.pack(pady=5)

        ctk.CTkButton(self.root, text="Save", command=lambda: self.save_modified_alert(index)).pack(pady=5)
        ctk.CTkButton(self.root, text="Back", command=self.list_alerts).pack(pady=5)

    def save_modified_alert(self, index):
        condition = self.condition_entry.get()
        value = self.value_entry.get()
        email = self.email_entry.get() or None
        alert = self.manager.get_alert_by_index(index)
        modified_alert = Alert(alert.type, alert.symbol, condition, value, email)
        self.manager.modify_alert(index, modified_alert)
        messagebox.showinfo("Success", "Alert modified successfully!")
        self.list_alerts()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    resend.api_key = RESEND_KEY_API
    app = CryptoAlertApp()
