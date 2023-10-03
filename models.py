from sqlalchemy import Column, DateTime, ForeignKey, Integer, String,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class partner_marketing_emails(Base):
    __tablename__ = "partner_marketing_emails"
    id = Column(Integer, primary_key=True, index=True)
    mail_uid = Column(String)
    sender_email = Column(String)
    brand_name = Column(String)
    subject_name = Column(String)
    received_at = Column(DateTime(timezone=True))
    inserted_at = Column(DateTime(timezone=True), server_default=func.now())
    campaign_start_date = Column(DateTime(timezone=True))
    campaign_end_date = Column(DateTime(timezone=True))
    product_variant_name = Column(String)
    product_min_purchase_qty = Column(Integer)
    product_max_purchase_qty = Column(Integer)
    product_price = Column(Float)
    product_discount = Column(Float)
    last_updated_at = Column(DateTime(timezone=True), onupdate=func.now())