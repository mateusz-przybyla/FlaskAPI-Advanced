import os
import requests
import jinja2
from typing import Any, Optional

DOMAIN = os.getenv("MAILGUN_DOMAIN")
template_loader = jinja2.FileSystemLoader("api/templates")
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename: str, **context: Any) -> str:
    return template_env.get_template(template_filename).render(**context)

def send_mailgun_message(to: str, subject: str, body: str, html: str) -> Optional[requests.Response]:
    try:
        return requests.post(
  	    f"https://api.mailgun.net/v3/{DOMAIN}/messages",
  		auth=("api", os.getenv("MAILGUN_API_KEY")),
  		data={"from": f"Flask Template <postmaster@{DOMAIN}>",
			"to": [to],
  			"subject": subject,
  			"text": body,
            "html": html,
        },
        timeout=5,
    )
    except requests.RequestException:
        # Log the exception in a real application
        return None

def send_user_registration_email(email: str, username: str) -> Optional[requests.Response]:
    return send_mailgun_message(
        to=email,  
        subject="Successfully signed up",
        body=f"Hi {username}, you have successfully signed up for our service!",
        html=render_template("email/registration.html", username=username),
    )