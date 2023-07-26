import smtplib
import ssl
import certifi
import requests
import re

CONFIG = {
    "ssl_context": ssl.create_default_context(cafile=certifi.where()),
    "server": 'smtp.gmail.com',
    "port": 465,
    "from": 'insightfulportfolios@gmail.com',
    "password": "dooxbfadafcucdjf",
    "url": "https://api.ultramsg.com/instance55310/messages/chat",
    "token": "e4hz6eak6zxrhv0q",
    "content_type": 'application/x-www-form-urlencoded'
}

#send email notification when sucessful of registration
def send_email(subject, body, to):
    try:
        with smtplib.SMTP_SSL(CONFIG["server"], CONFIG["port"], context=CONFIG["ssl_context"]) as server:
            server.login(CONFIG["from"], CONFIG["password"])
            server.sendmail(CONFIG["from"], to, f"Subject: {subject}\n\n{body}")
    except Exception as e:
        print(f"Error while to send email notification while registration: {e}")
        return None

#send whatsapp message when sucessful of registration
def send_message(number, body):
    try:
        number_without_plus = re.sub(r'\+', '', number)
        payload = f"token={CONFIG['token']}&to=%2B{number_without_plus}&body={body}"
        payload = payload.encode('utf8').decode('iso-8859-1')
        headers = {'content-type': CONFIG["content_type"]}
        response = requests.request("POST", CONFIG["url"], data=payload, headers=headers)
        print(response)
    except Exception as e:
        print(f"Error while to send whatsapp message while registration: {e}")
        return None

#register the process of message when sucessful of registration
def registration_message(number, email):
    try:
        REG_SUBJECT = "Insightful Portfolios"
        REG_BODY = "Thanks for registering with Insightful Portfolios!"
        send_message(number, REG_BODY)
        send_email(REG_SUBJECT, REG_BODY, email)
    except Exception as e:
        print(f"Error trying to send message while registration: {e}")
        return None
