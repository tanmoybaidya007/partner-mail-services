import imaplib
import email
import pandas as pd
import os
from email.header import decode_header
from dotenv import load_dotenv
from email.utils import parsedate_to_datetime
from pydantic import BaseModel
from typing import Literal
from fastapi import FastAPI, Depends, Query

# Load environment variables
load_dotenv()

def login():
    password = os.getenv('READ_EMAIL_PASSWORD')
    readaddr= os.getenv('READ_EMAIL_ID')
    # Connect to the server and select the inbox
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(readaddr,password)
    mail.select('inbox')
    return mail


class UpdateDbRequiredSchemas(BaseModel):
    brand_name: Literal['AMUL','Taj Mahal','Bisleri','Coca-Cola','Red Bull','Thumbs Up'] = 'AMUL'

class GetDbRequiredSchemas(BaseModel):
    brand_name: Literal['AMUL','Taj Mahal','Bisleri','Coca-Cola','Red Bull','Thumbs Up'] = 'AMUL'
    no_of_emails: int = Query(..., ge=1, le=10)

def extract_ids(input_dict, id_set=None):
    if id_set is None:
        id_set = set()
        
    for key, value in input_dict.items():
        if key == 'uid':
            id_set.add(value)
        elif isinstance(value, dict):
            extract_ids(value, id_set)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    extract_ids(item, id_set)
    return id_set
