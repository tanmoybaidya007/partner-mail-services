import smtplib
import os
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
load_dotenv()

def send_email(toaddr,subject,body,filename):
    # Sender and recipient email addresses
    fromaddr = os.getenv('SENT_EMAIL_ID')

    password = os.getenv('SENT_EMAIL_PASSWORD')

    # Path to the file you want to attach
    filepath = f"Data/{filename}"

    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    # Attach the body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Open the file to be sent and attach it to the email
    with open(filepath, "rb") as attachment_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= {}".format(filename))
        msg.attach(part)

    # Connect to the Gmail SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, password)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")