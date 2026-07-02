"""
This file is called the CRUD layer (Create, Read, Update, Delete). Its job is only to interact with the database. It should not contain FastAPI routes or business logic—it simply performs database operations using the SQLAlchemy Session.
Remember:
Engine → Knows how to connect to the database.
Session → Actually performs database operations (INSERT, SELECT, UPDATE, DELETE).
"""
#Every CRUD function receives a Session object so it can communicate with the database.


from sqlalchemy.orm import Session
from app.db.models import ProcessedDocument #Imports your ORM Model
"""
class ProcessedDocument(Base):
This class represents the processed_documents table in the database.
"""


#This function creates a new row in the database.
def create_processed_document(db:Session, filename:str, extracted_json:dict, markdown_output:str, validation_json:dict | None, total_score:float, is_valid:bool)-> ProcessedDocument:
    record=ProcessedDocument(
        filename=filename,
        listing_number=extracted_json.get("listing_number",""),
        title=extracted_json.get("title",""),
        extracted_json=extracted_json,
        markdown_output=markdown_output,
        validation_json=validation_json,
        total_score=total_score,
        is_valid=is_valid,
    )
    db.add(record) #"I want this object to be inserted into the database."-- nothing has been written permanently
    db.commit() #SQLAlchemy generates SQL and Record is permanently saved
    db.refresh(record) #Python object doesnt know the id and the time it was created at -->"Give me the latest version of this row."
    return record #The caller can now access record.id, record.filename etc

def get_all_documents(db:Session):
    return db.query(ProcessedDocument).order_by(ProcessedDocument.created_at.desc()).all()
#Equivalent SQL:SELECT *FROM processed_documents; Sorts rows by creation time in descending order.

def get_document_by_id(db:Session, doc_id:int):
    return db.query(ProcessedDocument).filter(ProcessedDocument.id==doc_id).first()

"""
RTF File
      │
      ▼
Extraction Pipeline
      │
      ▼
Produces:
  filename
  extracted_json
  markdown_output
  validation_json
  total_score
  is_valid
      │
      ▼
create_processed_document()
      │
      ▼
Creates a ProcessedDocument object
      │
      ▼
db.add()
      │
      ▼
db.commit()
      │
      ▼
Row saved in processed_documents table

Later, when the frontend wants to display previous results:

Frontend
      │
      ▼
GET /documents
      │
      ▼
get_all_documents()
      │
      ▼
Returns every row from processed_documents

Or, if the frontend requests a specific document:

Frontend
      │
      ▼
GET /documents/5
      │
      ▼
get_document_by_id(db, 5)
      │
      ▼
Returns only the row with id = 5
"""