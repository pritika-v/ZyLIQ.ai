"""When you run uvicorn app.main:app --reload
Uvicorn looks for:
app folder->main.py->the variable named app
Then it starts the entire backend using this file"""

"""
Whenever you create class ProcessedDocument(Base): that table gets registered under Base.
Later, Base.metadata.create_all() creates all registered tables.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware #Allow browsers to talk to your backend when frontend and backend are running on different addresses.

from app.db.database import engine, Base #Inside database.py we have engine=create_engine(...) and Base=declarative_base() This imports the database engine and SQLlchemy Base Class
from app.db import models  # noqa: F401  (import so SQLAlchemy registers the table)
from app.routers import documents #API endpoints exists here

# Create tables on startup if they don't exist yet
Base.metadata.create_all(bind=engine) #CREATE TABLE IF NOT EXISTS ...

app = FastAPI(title="Clinical Trial Data Extraction API") #This creates the backend application.
"""
Everything else attaches to this object.
FastAPI App
      │
      ├── Middleware
      ├── Routes
      ├── Docs
      ├── Exception Handlers
      └── Dependencies
This title appears in localhost:8000/docs
"""

#Middleware means "Run this before every request and after every response."
# Allow the React frontend (running on a different port/container) to call this API
"""
CORS=Cross-Origin Resource Sharing
Suppose Frontend React http://localhost:5173
Backend FastAPI http://localhost:8000

React tries fetch("http://localhost:8000/api/documents")
Browser sees 5173->8000

Different origins.Browser immediately asks "Is this allowed?"
If backend says "No" Browser blocks it. Even though Backend is perfectly working.

Without CORS Browser Console Access to fetch has been blocked by CORS policy. This is probably the most common frontend/backend error.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #Allow everyone # tighten this to your frontend's actual origin in real production
    allow_credentials=True, #Credentials include cookies, authorization headers, client certificates etc. If your app uses login, cookies need this
    allow_methods=["*"], #Allow every HTTP Method like gte, post, put, delete, patch, options etc
    allow_headers=["*"], #Headers are like Authorization, Content-Type, Accept, X-API-Key
)

app.include_router(documents.router) #Fastapi adds all the endpoints that is there in documents.py

#Health Check
#this endpoint is used by developers to verify the API is running
#"When someone sends a GET request to /, run the function below." If you visit http://localhost:8000/, youll get that ok json
@app.get("/")
def health_check():
    return {"status": "ok", "service": "clinical-trial-extraction-api"}

"""
Browser (React)
       │
       │ HTTP Request
       ▼
Uvicorn Server
       │
       ▼
main.py
       │
 ┌───────────────┐
 │Creates FastAPI│
 └───────────────┘
       │
       ▼
Adds Middleware (CORS)
       │
       ▼
Creates Database Tables
       │
       ▼
Registers Routers
       │
       ▼
API Ready
"""