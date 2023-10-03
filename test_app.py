from fastapi import FastAPI, File, UploadFile, Depends,HTTPException
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import db,DBSessionMiddleware
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

# Import your model and any other necessary things
from models import partner_marketing_emails as ModelEmails

app = FastAPI()
app.add_middleware(DBSessionMiddleware,db_url=os.environ["DATABASE_URL"])

@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    if file.filename.endswith('.csv'):
        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file.file)
            
            # Iterate over DataFrame rows and insert them into the database
            for index, row in df.iterrows():
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
                    product_discount=row['product_discount']
                )
                db.session.add(email_entry)  
            db.session.commit() 
            return JSONResponse(status_code=200, content={"message": "Data added successfully"})
        
        except Exception as e:
            db.session.rollback()  # Rollback the transaction in case of error
            return JSONResponse(status_code=400, content={"message": f"Error occurred: {e}"})
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
