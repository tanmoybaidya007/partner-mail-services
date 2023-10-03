from pydantic import BaseModel
from datetime import datetime

class partner_marketing_emails(BaseModel):
    mail_uid: str
    sender_email: str
    brand_name: str
    subject_name: str
    received_at: datetime
    inserted_at: datetime
    product_variant_name: str
    product_min_purchase_qty: int
    product_max_purchase_qty: int
    product_price:float
    product_discount:float