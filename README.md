
# Description

A cryptocurrency notifications system based on CoinAPI, allowing users to create alerts for when a cryptocurrency goes above or below a certain value, as well as if it changes by a certain percentage.

Can be used through a CLI or GUI.

# Requirements

Tested on win11 only.

## Resend API setup:
1 - This project uses the resend api to send mail notifications, therefore the user has to create a [Resend](https://resend.com) account to get an API key, the free plan allows the user to send 100 emails daily and 3000 per month. (Preferably open an account with the mail where you wish to receive notifications)

2 - The variable for this is ``RESEND_KEY_API`` which is at the start of the cli_app.py file.

3 - It is important to note that initially you can only use resend to send emails to the mail address with which you have signed up with, but you can add permitted recipients if you have multiple mails where you wish to receive notifications.

## Packages

pip install requests

pip install tkinter

pip install customtkinter

pip install resend

pip install plyer

or use requirements.txt

# Usage
## CLI

```python cli_app.py```

The CLI uses the alerts.json file to store the alerts, with no users or login system.

The user is then presented with a bunch of options

1. Create Alert
2. List Alerts
3. Delete Alert
4. Modify Alert
5. List alerts of specfic cryptocurrency
6. Get price of cryptocurrency
0. Exit
   
## GUI

```python ui_app.py```


The UI app uses a different json file for each user to store user specific alerts, when you login, only your alerts are active.

You can then create alerts, visualize your alerts and eventually select an alert to either modify or delete from this list.