import os
import requests

DOMAIN = os.getenv("MAILGUN_DOMAIN")

def send_simple_message(to, subject, body):
    return requests.post(
  	    f"https://api.mailgun.net/v3/{DOMAIN}/messages",
  		auth=("api", os.getenv("MAILGUN_API_KEY")),
  		data={"from": f"Mateusz Przybyla <postmaster@{DOMAIN}>",
			"to": [to],
  			"subject": subject,
  			"text": body})

def send_user_registration_email(email, username):
    return send_simple_message(
        to=email,  
        subject="Successfully signed up",
        body=f"Hi {username}, you have successfully signed up for our service!"
    )