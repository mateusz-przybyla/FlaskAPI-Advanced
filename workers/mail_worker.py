import os
import requests
import jinja2

DOMAIN = os.getenv("MAILGUN_DOMAIN")
template_loader = jinja2.FileSystemLoader("api/templates")
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename, **context):
    return template_env.get_template(template_filename).render(**context)

def send_mailgun_message(to, subject, body, html):
    return requests.post(
  	    f"https://api.mailgun.net/v3/{DOMAIN}/messages",
  		auth=("api", os.getenv("MAILGUN_API_KEY")),
  		data={"from": f"Mateusz Przybyla <postmaster@{DOMAIN}>",
			"to": [to],
  			"subject": subject,
  			"text": body,
            "html": html 
        }
    )

def send_user_registration_email(email, username):
    return send_mailgun_message(
        to=email,  
        subject="Successfully signed up",
        body=f"Hi {username}, you have successfully signed up for our service!",
        html=render_template("email/registration.html", username=username),
    )