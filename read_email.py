import imaplib
import email
import pandas as pd
import os
from email.header import decode_header
from dotenv import load_dotenv
from email.utils import parsedate_to_datetime
from utils import login,extract_ids

load_dotenv()


def read_inbox(keyword):
    mail = login()
    search_criterion = f'(SUBJECT "{keyword}")'

    # Search for emails with specific words in the subject line
    status, messages = mail.uid('search', None, search_criterion)
    #status, messages = mail.search(None, '(SUBJECT "Amul Dairy Marketing Offer")')

    # Extract the list of email UIDs
    email_uids = messages[0].split()

    # Iterate through the email IDs and process each email
    email_data = []
    for e_uid in email_uids:
        _, msg = mail.uid('fetch', e_uid, '(RFC822)')
        for response_part in msg:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                #print(e_uid)
                # Extract the received date and time and the email UID
                received_date = parsedate_to_datetime(msg['Date'])
                email_data.append({'uid': e_uid, 'received_date': received_date})

    # Sort the emails by the latest received time
    email_data.sort(key=lambda x: x['received_date'], reverse=True)
    return email_data,mail



def download_emails(email_data,mail):
    #for email_data in email_data:
    e_uid = email_data['uid']
    _, msg = mail.uid('fetch', e_uid, '(RFC822)')
    for response_part in msg:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if encoding:
                subject = subject.decode(encoding)
            print("Subject:", subject)
            print("UID:", e_uid.decode('utf-8'))  # UID is in bytes, so decode it to string
            print("Received Date:", email_data['received_date'].strftime('%Y-%m-%d %H:%M:%S'))
            
            # If the email message is multipart, extract the attachments
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if filename:
                        folder_name = "downloaded_attachments"
                        if not os.path.isdir(folder_name):
                            os.mkdir(folder_name)
                        filepath = os.path.join(folder_name, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Attachment {filename} downloaded.")
                        
                        # Read the downloaded CSV file as a pandas DataFrame
                        if filename.endswith('.csv'):
                            df = pd.read_csv(filepath)
                            df['mail_uid'] = e_uid.decode('utf-8')
                            df['received_at'] = email_data['received_date'].strftime('%Y-%m-%d %H:%M:%S')
                            df['subject_name'] = subject
                            df['sender_email'] = msg['From']
                            print(df.head())  # Display the first 5 rows of the dataframe
                            return df.to_dict(orient='records')
    
if __name__ == '__main__':
    email_data,mail = read_inbox('Amul Dairy Marketing Offer')
    set_ids = set({d['uid'].decode('utf-8') for d in email_data if 'uid' in d})
    print(set_ids)
    download_emails(email_data,mail)