"""
This file defines a database table using SQLAlchemy's ORM. Instead of writing SQL like CREATE TABLE processed_documents (...), you define the table as a Python class, and SQLAlchemy maps it to a real database table.
"""

#These are the different data types your database columns can have.
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime
from sqlalchemy.sql import func

#Every ORM model inherits from this so SQLAlchemy knows it represents a database table.
from app.db.database import Base

class ProcessedDocument(Base): #Inheriting from Base --"This class should become a database table."
    """
    Stores the final extracted JSON, the validation report, and the
    rendered markdown table so the frontend can fetch any of the three
    without re-running the pipeline.
    """
    __tablename__="processed_documents" #name of the table

    id=Column(Integer, primary_key=True, index=True)
    filename=Column(String, nullable=False, index=True)

    listing_number=Column(String, default="")
    title=Column(String, default="")
    
    extracted_json = Column(JSON, nullable=False)   # full ExtractionResult as dict
    markdown_output = Column(String, nullable=False)  # rendered markdown table
    validation_json = Column(JSON, nullable=True)    # full ValidationResult as dict

    total_score=Column(Float, default=0.0)
    is_valid=Column(Boolean, default=False)

    created_at=Column(DateTime(timezone=True), server_default=func.now()) #Automatically stores when the row was inserted.
    #The database fills it in automatically using func.now()
"""
RTF File
      │
      ▼
Pipeline extracts data
      │
      ▼
Validation runs
      │
      ▼
Markdown is generated
      │
      ▼
Everything is stored in one row of
processed_documents
"""