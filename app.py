from fastapi import FastAPI, Form, File, UploadFile,Depends, Query
from fastapi.responses import JSONResponse
import os
import pandas as pd
from fastapi_sqlalchemy import DBSessionMiddleware, db
from pydantic import BaseModel
from typing import Literal
from sqlalchemy import desc
import csv
import io
from fastapi.responses import StreamingResponse

from sent_email import send_email
from read_email import read_inbox,download_emails
from models import partner_marketing_emails as ModelEmails
from utils import UpdateDbRequiredSchemas,GetDbRequiredSchemas
#from schemas import partner_marketing_emails as SchemaEmails

app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])



@app.get("/")
async def root():
    return {"message": "Welcome to the Partner Marketing Email API"}


@app.post("/send_mail/")
async def send_mail(toaddr: str = Form(...), subject: str = Form(...), body: str = Form(...), attachment: UploadFile = File(...)):
    df = pd.read_csv(attachment.file)
    df.to_csv(f"Data/{attachment.filename}", index=False)
    try:
        send_email(toaddr, subject, body, attachment.filename)
        return JSONResponse(status_code=200, content={"message": "Email sent successfully"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": f"Failed to send email. Error: {e}"})


@app.post("/update_database/")
async def update_database(data: UpdateDbRequiredSchemas = Depends()):
    key_word = f"{data.brand_name} Marketing Offer"
    email_data,mail = read_inbox(key_word)
    received_mail_uids = set({d['uid'].decode('utf-8') for d in email_data if 'uid' in d})
    db_mail_uids = set({d.mail_uid for d in db.session.query(ModelEmails.mail_uid).all()})
    new_mail_uids = received_mail_uids - db_mail_uids
    new_email_data = [d for d in email_data if 'uid' in d and d['uid'].decode('utf-8') in new_mail_uids]
    if new_email_data:
        for email_data in new_email_data:
            df = download_emails(email_data,mail)
            dataframe = pd.DataFrame(df)
            #cols = [x for x in dataframe.columns if 'date' in x]
            #for col in cols:
                #dataframe[col] = pd.to_datetime(dataframe[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
            for index, row in dataframe.iterrows():
                email_entry = ModelEmails(
                    mail_uid=row['mail_uid'],
                    sender_email=row['sender_email'],
                    brand_name=row['brand_name'],
                    subject_name=row['subject_name'],
                    received_at=row['received_at'],  # Make sure this is in the correct date-time format
                    product_variant_name=row['product_variant_name'],
                    product_min_purchase_qty=row['product_min_purchase_qty'],
                    product_max_purchase_qty=row['product_max_purchase_qty'],
                    product_price=row['product_price'],
                    product_discount=row['product_discount'],
                    campaign_start_date=row['campaign_start_date'],
                    campaign_end_date=row['campaign_end_date'])
                db.session.add(email_entry)
            db.session.commit()
        mail.logout()
    #download_emails(new_email_data,mail)
        return JSONResponse(status_code=200, content={"message": f"{len(new_email_data)} new marketing emails received from {data.brand_name} and added to the database.Please use the /get_data/ endpoint to view the data"})
    else:
        mail.logout()
        return JSONResponse(status_code=200, content={"message": f"No new marketing emails received from {data.brand_name}"})

@app.get("/get_data/", response_class=StreamingResponse)
async def get_data(data: GetDbRequiredSchemas = Depends()):
    final_data = (
        db.session.query(ModelEmails)
        .filter_by(brand_name=data.brand_name)
        .order_by(desc(ModelEmails.inserted_at))
        .limit(data.no_of_emails)
        .all()
    )

    if final_data:
        # Convert the data to CSV format
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([column.name for column in ModelEmails.__table__.columns])  # writing headers

        for data_row in final_data:
            writer.writerow([getattr(data_row, column.name) for column in ModelEmails.__table__.columns])

        output.seek(0)  # go back to the beginning of the StringIO buffer

        # Return the CSV data as a stream
        return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={
            "Content-Disposition": f"attachment;filename={data.brand_name}_data.csv"
        })
    else:
        return JSONResponse(status_code=400, content={"message": f"No data found for {data.brand_name} Dairy"})    