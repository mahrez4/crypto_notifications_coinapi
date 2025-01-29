import requests
import json
from plyer import notification
import time
import resend
import threading
from datetime import datetime, date

API_KEY = 'fceff4f8-c486-4a17-ae1f-312abd7a9858'
DATE_FORMAT = "%Y-%m-%d,%H:%M:%S"
RESEND_KEY_API = "re_RjkWuduU_68yv585WfkYWQvWrySVwrpQa"

class Alert:
    def __init__(self, type, symbol, condition, value, email = None):
        self.type = type # basic or percentage_change
        self.symbol = symbol
        self.condition = condition
        self.value = value
        self.email = email
        self.date = datetime.now().strftime(DATE_FORMAT)
        self.initial_price = CoinAPI(API_KEY).get_price(self.symbol)

    def to_dict(self):
        return {
            "type": self.type,
            "symbol": self.symbol,
            "condition": self.condition,
            "value": self.value,
            "email": self.email,
            "date": self.date,
            "initial_price": self.initial_price
        }

# Manage alerts (add, remove, list, edit)

class AlertManager:

    def __init__(self, path):
        self.path = path
        self.alerts = self._load_alerts()

    def _load_alerts(self):
        try:
            with open(self.path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        
    def save_alerts(self):
        with open(self.path, 'w') as file:
            json.dump(self.alerts, file, indent = 4)

    def create_alert(self, alert: Alert):
        if alert.to_dict() not in self.alerts:
            self.alerts.append(alert.to_dict())
            self.save_alerts()
        else:
            print(f"Alert already exists.")

    def modify_alert(self, index, alert: Alert):
        if 0 <= index < len(self.alerts):
            self.alerts[index]["symbol"] = alert.symbol
            self.alerts[index]["condition"] = alert.condition
            self.alerts[index]["value"] = alert.value
            self.alerts[index]["email"] = alert.email
            self.save_alerts()
    
    def list_alerts(self):
        return self.alerts
    
    def get_alert_by_index(self, index):
        if 0 <= index < len(self.alerts):
            return Alert(self.alerts[index]["type"],self.alerts[index]["symbol"],self.alerts[index]["condition"],self.alerts[index]["value"],self.alerts[index]["email"])

    def delete_alert(self, index):
        if 0 <= index < len(self.alerts):
            del self.alerts[index]
            self.save_alerts()


# CoinAPI Class

class CoinAPI:
    BASE_URL = "https://rest.coinapi.io/v1"
    
    def __init__(self, api_key):
        self.api_key = api_key

    def get_price(self, symbol):
        url = f"{self.BASE_URL}/exchangerate/{symbol}/USD"
        headers = {"X-CoinAPI-Key": self.api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['rate']


# Notification functions

def send_notification_by_email(to_email, symbol, msg):
    r = resend.Emails.send({
        "from": "coinapi_notifs@resend.dev",
        "to": to_email,
        "subject": f"Crypto Alert: {symbol} Price Update",
        "html": msg 
    })

def send_visual_notification(symbol, msg):
    notification.notify(
        title=f"Crypto Alert: {symbol}",
        message=msg,
        timeout=10
    )


## Monitoring

def monitor_prices(api, manager):
    old_prices = {}
    for alert in manager.list_alerts():
        symbol = alert['symbol']
        old_prices[symbol] = api.get_price(symbol)

    time.sleep(2)
    while True:
        for i,alert in enumerate(manager.list_alerts()):
            symbol = alert['symbol']
            condition = alert['condition']
            threshold = float(alert['value'])
            alert_type = alert['type']
            initial_price = float(alert['initial_price'])
            email = alert.get('email')
            try:
                price = api.get_price(symbol)

                if alert_type == "basic":
                    if (condition == "above" and price > threshold and old_prices[symbol] < threshold) or (condition == "below" and price < threshold and old_prices[symbol] > threshold):
                        print(f"Alert triggered for {symbol}: {price} USD")
                        msg = f"Alert: {symbol} is now {condition} the value of {threshold}! The current price is: {price} USD"
                        send_visual_notification(symbol, msg)
                        if email:
                            send_notification_by_email(email, symbol, msg)

                elif alert_type == 'percentage_change':
                    if price > initial_price:
                        percent_change = ((price - initial_price) / initial_price) * 100
                        if (condition == "increase" and percent_change >= threshold):
                            print(f"Percentage change alert triggered for {symbol}: {condition} by {percent_change:.2f}%")
                            msg = f"Alert: {threshold} {condition} of {symbol} from alert creation date."
                            send_visual_notification(symbol, msg)
                            if email:
                                send_notification_by_email(email, symbol, msg)
                            manager.delete_alert(i)
                    else:
                        percent_change = ((initial_price - price) / initial_price) * 100
                        if (condition == "decrease" and percent_change >= threshold):
                            print(f"Percentage change alert triggered for {symbol}: {condition} by {percent_change:.2f}%")
                            msg = f"Alert: {threshold} {condition} of {symbol} from alert creation date."
                            send_visual_notification(symbol, msg)
                            if email:
                                send_notification_by_email(email, symbol, msg)
                            manager.delete_alert(i)
                            
                old_prices[symbol] = price

            except Exception as e:
                if symbol not in old_prices:
                    old_prices[symbol] = api.get_price(symbol)
                else:
                    print(api.api_key)
                    print(old_prices)
                    print(f"Error monitoring {symbol}: {e}")
        
        time.sleep(5)


def user_input(manager):
    """Thread to handle user input for alert creation while monitorning is happening."""
    while True:
        print("\nOptions: ")
        print("1. Create Alert")
        print("2. List Alerts")
        print("3. Delete Alert")
        print("4. Modify Alert")
        print("5. List alerts of specfic cryptocurrency")
        print("6. Get price of cryptocurrency")
        print("0. Exit")

        choice = input("Select an option: ")
        
        if choice == '1':
            type = input("Enter alert type: (basic / percentage_change): ")
            symbol = input("Enter cryptocurrency symbol (e.g., BTC): ")
            if type == "basic":
                condition = input("Enter condition (above/below): ")
                threshold = input("Enter price threshold: ")
            
            elif type == "percentage_change":
                condition = input("Enter condition (increase/decrease): ")
                threshold = input("Enter price change percentage (0-100): ") 
                
            
            email = input("Enter email for notifications (leave blank for none): ") or None
            alert = Alert(type,symbol, condition, threshold, email)
            manager.create_alert(alert)
            print(f"Alert created for {symbol} {condition} {threshold}")

        elif choice == '2':
            alerts = manager.list_alerts()
            for i, alert in enumerate(alerts):
                print(f"{i}: {alert}")

        elif choice == '3':
            index = int(input("Enter alert index to delete: "))
            manager.delete_alert(index)
            print("Alert deleted.")

        elif choice == '4':
            index = int(input("Enter alert index to modify: "))  
            alert = manager.list_alerts()[index]
            type = alert['type']
            old_sym = alert["symbol"]
            old_cond = alert["condition"]
            old_val = alert["value"]
            old_email = alert["email"]

            
            if type == 'basic':
                symbol = input(f"Enter cryptocurrency symbol (current = {old_sym}): ")
                condition = input(f"Enter condition (above/below) (current = {old_cond}): ")
                threshold = input(f"Enter price threshold (current = {old_val}): ")
            elif type == 'percentage_change':
                symbol = old_sym
                condition = input(f"Enter condition (increase/decrease) (current = {old_cond}): ")
                threshold = input(f"Enter price change percentage (0 - 100) (current = {old_val}): ")

            email = input(f"Enter email for notifications (current = {old_email}): ") or None
            alert = Alert(type, symbol, condition, threshold, email)
            manager.modify_alert(index,alert)
            print("Alert modified.")

        elif choice == '5':
            alerts = manager.list_alerts()
            symbol = input("Enter cryptocurrency symbol (e.g., BTC): ")
            for i, alert in enumerate(alerts):
                if alert['symbol'] == symbol:
                    print(f"{i}: {alert}")

        elif choice == '6':
            symbol = input("Enter cryptocurrency symbol (e.g., BTC): ")
            price = coin_api.get_price(symbol)
            print(f"The price of {symbol} is {price}.")

        elif choice == '0':
            print("Exiting...")
            break

        else:
            print("Invalid option. Try again.")



if __name__ == "__main__":
    # Instantiation
    coin_api = CoinAPI(API_KEY)

    #Mailing service API
    resend.api_key = RESEND_KEY_API

    # Instantiate alert manager
    # Loads up existing alerts from alerts.json or is empty if there are no alerts
    manager = AlertManager("mahrez_alerts.json")

    # Start monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_prices, args=(coin_api, manager), daemon=True)
    monitor_thread.start()

    # Handle user input in the main thread
    user_input(manager)