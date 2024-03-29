import os
import smtplib
import imghdr
from email.message import EmailMessage

PASSWORD = os.getenv("GMAIL_WEBCAM_MESSAGE")
SENDER = os.getenv("GMAIL_EMAIL_ADDRESS")
RECEIVER = os.getenv("GMAIL_EMAIL_ADDRESS")


def send_email(image_path):
    email_message = EmailMessage()
    email_message["Subject"] = "New object show up!"
    email_message.set_content("Hey, just take a look for the object")

    with open(image_path, "rb") as file:
        content = file.read()
    email_message.add_attachment(content, maintype="image",
                                 subtype=imghdr.what(None, content))

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(SENDER, PASSWORD)
    gmail.sendmail(SENDER, RECEIVER, email_message.as_string())
    gmail.quit()

if __name__ == "__main__":
    send_email(image_path="images/19.png")
