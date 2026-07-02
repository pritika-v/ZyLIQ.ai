"""   Client (React/Postman)
        │
        │ POST /api/documents/upload-and-process
        ▼
FastAPI Router (documents.py)
        │
        ├── Validate file extension (.rtf)
        │
        ├── Save uploaded file to RTF_FOLDER
        │
        ├── Call process_document(rtf_path)
        │       │
        │       ├── Extract text from RTF
        │       ├── Chunk the document
        │       ├── Send chunks to the LLM
        │       ├── Validate extracted data
        │       └── Return best_json + validation
        │
        ├── Compute score and validity
        │
        ├── Save JSON/Markdown/Validation files
        │
        ├── Save everything to PostgreSQL
        │
        └── Return JSON response
                │
                ▼
Frontend displays the processed document
this file does not do the extraction, it simply coordinates everything
"""
"""
This file is your Documents API. Its job is to expose endpoints (URLs) that let a frontend or another application interact with your document-processing pipeline.
Think of it as a receptionist.
Your actual processing logic lives elsewhere (process_document, crud, render_markdown, etc.). This file simply accepts requests, calls the appropriate functions, and returns responses.
"""

import os #used for file paths
import shutil #used for copying files

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session #the endpoint needs a session to save into PostgreSQL

#UploadFile represents the uploaded rtf. FastAPI receives it as "file" which is an UploadFile object
#File(...)-->This tells FastAPI "Expect a file from the request." Without it FastAPI wouldn't know this parameter is a file upload.


#db = Depends(get_db) means Before running this endpoint, create a database session and pass it to me. You never manually create sessions. FastAPI does it.
#HTTPException helps you return proper HTTP errors

from app.config import RTF_FOLDER, OUTPUT_FOLDER
from app.db.database import get_db #which creates database sessions.
from app.db import crud
from app.models.pydantic_models import ValidationResult
from app.pipeline.orchestrator import process_document #Entire extract->validate->correct->validate again pipelines lives in process_document()
from app.pipeline.io_utils import save_results
from app.pipeline.markdown_renderer import render_markdown #Converts extracted json to markdown table

#Instead of putting every endpoint inside one huge main.py, 
#FastAPI allows main.py->documents.py->users.py->auth.py Each router contains related endpoints.

router = APIRouter(prefix="/api/documents", tags=["documents"]) #"Everything in this file belongs together."

"""
Every endpoint automatically starts with this prefix.
@router.post("/upload") becomes /api/documents/upload
@router.get("/") actually becomes GET /api/documents/

when ther are multiple endpoints and having all of them in main.py can get messy
Each router owns one group of endpoints.
So in this documents.py, this @router.post endpoint belongs to the router and not yet to the application
Then main.py will combine all the routers-"Take all the endpoints inside this router and attach them to my application."
"""
"""
db: Session = Depends(get_db)
This is Dependency Injection.
Instead of writing
db = SessionLocal()

inside every endpoint,
FastAPI does it automatically.

It is almost equivalent to
db = get_db()
"""

@router.post("/upload-and-process") #Client-->POST-->upload_and_process()
async def upload_and_process(file: UploadFile = File(...), db: Session = Depends(get_db)): #2 inputs: "I expect the client to upload a file." and every request gets a database session
    """
    Single endpoint that mirrors what you did manually in the notebook's
    'TEST RUN' cell (Cell 16): save the uploaded RTF, run process_document()
    (extract -> validate -> correct loop), save outputs, persist to Postgres,
    and return everything the frontend needs in one response.
    """
    if not file.filename.lower().endswith(".rtf"):
        raise HTTPException(status_code=400, detail="Only .rtf files are supported")

    # Save the uploaded file into RTF_FOLDER, same role as ./rtf_files in the notebook
    rtf_path = os.path.join(RTF_FOLDER, file.filename)
    with open(rtf_path, "wb") as f: 
        shutil.copyfileobj(file.file, f) #this copies uploaded file to uploads/report.rtf

    # ── Run the exact same pipeline as the notebook ──
    best_json, best_validation = process_document(rtf_path)

    #If extraction failed
    if best_json is None:
        raise HTTPException(status_code=500, detail="Pipeline failed: extraction returned nothing. Check backend logs.")

    #Converting best_validation (pydantic model) to dict (like ValidationResult) using model_dump
    val_dict = best_validation.model_dump() if isinstance(best_validation, ValidationResult) else best_validation
    total_score = best_validation.total_score() if isinstance(best_validation, ValidationResult) else 0.0
    is_valid = val_dict.get("is_valid", False) if val_dict else False

    # Save to disk exactly like the notebook did (json + markdown + validation files)
    base_name = os.path.splitext(os.path.basename(rtf_path))[0]
    save_results(best_json, val_dict, base_name) #report.json, report_validation.json and report.md is created

    # Build the markdown string for the API response / DB row
    markdown_output = render_markdown(best_json)

    # Save to Postgres so the result survives container restarts
    record = crud.create_processed_document(
        db=db,
        filename=file.filename,
        extracted_json=best_json,
        markdown_output=markdown_output,
        validation_json=val_dict,
        total_score=total_score,
        is_valid=is_valid,
    )

    return {
        "id": record.id,
        "filename": record.filename,
        "extracted_json": record.extracted_json,
        "markdown_output": record.markdown_output,
        "validation_json": record.validation_json,
        "total_score": record.total_score,
        "is_valid": record.is_valid,
    }

#Give me every processed document.
@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    """List all previously processed documents (for a history sidebar)."""
    records = crud.get_all_documents(db)
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "listing_number": r.listing_number,
            "title": r.title,
            "total_score": r.total_score,
            "is_valid": r.is_valid,
            "created_at": r.created_at,
        }
        for r in records
    ]
"""
Third endpoint is dynamic URL
GET

/api/documents/7

/api/documents/10

/api/documents/99
"""

@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Fetch one previously processed document's full JSON/Markdown/Validation."""
    record = crud.get_document_by_id(db, doc_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": record.id,
        "filename": record.filename,
        "extracted_json": record.extracted_json,
        "markdown_output": record.markdown_output,
        "validation_json": record.validation_json,
        "total_score": record.total_score,
        "is_valid": record.is_valid,
    }
