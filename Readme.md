# Clinical Document Processing Pipeline

## Project Overview

This project is a full-stack AI-powered document processing system that extracts structured information from RTF documents using a Large Language Model (Mistral), validates the extracted data, stores it in PostgreSQL, and displays the results through a React frontend.

The project consists of:

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **LLM:** Mistral
- **Containerization:** Docker & Docker Compose
- **Cloud Deployment:** AWS EC2
- **CI/CD:** GitHub Actions → Docker Hub → AWS EC2 (Automatic Deployment)

---

# Backend Workflow

## Step 1 — User Uploads an RTF File

The user selects an RTF document from the React application and clicks **Upload**.

The frontend sends an HTTP POST request to:

```
POST /api/documents/upload-and-process
```

---

## Step 2 — FastAPI Starts

The entry point of the backend is:

```
app/main.py
```

### Responsibilities

- Creates the FastAPI application
- Registers all API routers
- Starts the backend server
- Waits for incoming requests

When running locally:

```bash
uvicorn app.main:app --reload
```

---

## Step 3 — API Router Receives the Request

The upload request is received by:

```
app/api/documents.py
```

### Responsibilities

- Receives uploaded file
- Validates file extension
- Saves the uploaded RTF
- Starts the document processing pipeline
- Returns the final API response

---

## Step 4 — Orchestrator Starts the Pipeline

```
app/services/orchestrator.py
```

### Responsibilities

The orchestrator controls the complete workflow.

It decides:

- what should run first
- what should run next
- what happens if validation fails
- when data should be stored

It acts as the **main controller** of the backend.

---

## Step 5 — Convert RTF to Plain Text

```
app/utils/rtf_utils.py
```

### Responsibilities

- Reads the uploaded RTF
- Removes formatting
- Converts it into plain text
- Returns clean text for processing

---

## Step 6 — Create LLM Prompt

```
app/services/extractor.py
```

### Responsibilities

- Loads the extraction prompt
- Inserts the document text
- Builds the final prompt
- Sends it to the LLM client

---

## Step 7 — Call the Mistral Model

```
app/services/llm_client.py
```

### Responsibilities

- Sends prompt to Mistral
- Waits for model response
- Returns generated output

The backend never talks directly to the model from multiple places.

All LLM communication happens here.

---

## Step 8 — Parse JSON

```
app/utils/json_parser.py
```

### Responsibilities

LLMs often return:

- extra text
- markdown
- explanations

This module extracts only the valid JSON from the response.

---

## Step 9 — Validate JSON Structure

```
app/models/
```

### Responsibilities

Pydantic models verify that:

- required fields exist
- data types are correct
- JSON follows the expected schema

This prevents invalid data from entering the system.

---

## Step 10 — Validate Extraction Quality

```
app/services/validator.py
```

### Responsibilities

Checks whether the extracted data is complete.

Examples:

- Missing fields
- Empty values
- Incorrect formatting

---

## Step 11 — Correct Invalid Data

```
app/services/corrector.py
```

### Responsibilities

If validation fails:

- regenerate missing values
- fix formatting
- improve extraction

This helps improve overall extraction quality.

---

## Step 12 — Generate Markdown

```
app/utils/markdown_renderer.py
```

### Responsibilities

Converts the extracted JSON into a clean Markdown report that is easier to read.

---

## Step 13 — Open Database Connection

```
app/database/database.py
```

### Responsibilities

- Creates PostgreSQL connection
- Creates SQLAlchemy session
- Provides database access to the application

---

## Step 14 — Store Data

```
app/database/crud.py
```

### Responsibilities

Handles all database operations.

Examples:

- Insert document
- Update document
- Retrieve document
- Delete document

---

## Step 15 — Return API Response

The router returns:

- extracted JSON
- validation results
- markdown
- status message

The React frontend receives this response and displays the processed document to the user.

---

# Complete Backend Request Flow

```
User Uploads RTF
        │
        ▼
React Frontend
        │
        ▼
POST /api/documents/upload-and-process
        │
        ▼
main.py
        │
        ▼
documents.py
        │
        ▼
Save Uploaded File
        │
        ▼
orchestrator.py
        │
        ▼
rtf_utils.py
        │
        ▼
extractor.py
        │
        ▼
llm_client.py
        │
        ▼
json_parser.py
        │
        ▼
Pydantic Validation
        │
        ▼
validator.py
        │
        ▼
corrector.py (if required)
        │
        ▼
markdown_renderer.py
        │
        ▼
database.py
        │
        ▼
crud.py
        │
        ▼
PostgreSQL
        │
        ▼
API Response
        │
        ▼
React Displays Results
```

---

# Docker Architecture

Docker packages the frontend, backend, and database into separate containers so the application runs consistently across different environments.

---

## Backend Container

The backend container is built using the backend Dockerfile.

When the container starts:

```
Container Starts
        │
        ▼
Install Python Dependencies
        │
        ▼
Run

uvicorn app.main:app --host 0.0.0.0 --port 8000

        │
        ▼
FastAPI Starts
        │
        ▼
Listening on Port 8000
        │
        ▼
Waiting for Requests
```

---

## Frontend Container

The frontend container is built using the frontend Dockerfile.

When it starts:

```
Container Starts
        │
        ▼
Install Node Modules
        │
        ▼
Start Vite Development Server
        │
        ▼
Listening on Port 5173
        │
        ▼
Waiting for User Requests
```

---

## PostgreSQL Container

Docker starts a PostgreSQL database automatically.

```
Container Starts
        │
        ▼
Initialize PostgreSQL
        │
        ▼
Create Database
        │
        ▼
Wait for Backend Connection
```

The backend connects using:

```
Host = db
Port = 5432
```

The hostname is **db** because Docker Compose allows containers to communicate using service names instead of `localhost`.

---

# Docker Compose

The `docker-compose.yml` file starts all services together.

It creates:

- Backend container
- Frontend container
- PostgreSQL container
- Shared Docker network
- Volumes for persistent database storage

Running:

```bash
docker compose up --build
```

starts the complete application with a single command.

---

# Container Communication

Docker Compose automatically creates a private network.

```
             Docker Network

+-----------------------------+
|                             |
|   React Container           |
|          │                  |
|          │ HTTP             |
|          ▼                  |
|   FastAPI Container         |
|          │                  |
|          │ SQL              |
|          ▼                  |
| PostgreSQL Container        |
|                             |
+-----------------------------+
```

Each container communicates using its service name.

---

# CI/CD Pipeline

The project uses **GitHub Actions** to automate code verification and Docker image deployment.

Workflow file:

```
.github/workflows/ci.yml
```

---

# Continuous Integration (CI)

Every push to GitHub automatically triggers the CI workflow.

### CI Steps

```
Developer Pushes Code
        │
        ▼
Checkout Repository
        │
        ▼
Set Up Python
        │
        ▼
Install Backend Dependencies
        │
        ▼
Run Backend Validation
        │
        ▼
Set Up Node.js
        │
        ▼
Install Frontend Dependencies
        │
        ▼
Build React Application
        │
        ▼
CI Completed Successfully
```

### Purpose

The CI pipeline verifies that:

- backend dependencies install successfully
- frontend dependencies install successfully
- React builds without errors
- FastAPI project is valid
- the project is safe to deploy

---

# Continuous Deployment (CD)

After the Continuous Integration (CI) checks pass successfully, GitHub Actions automatically deploys the latest version of the application to an AWS EC2 instance.

## Deployment Flow

```
Developer Pushes Code
        │
        ▼
Backend Checks
        │
        ▼
Frontend Build
        │
        ▼
Build Backend Docker Image
        │
        ▼
Build Frontend Docker Image
        │
        ▼
Push Images to Docker Hub
        │
        ▼
SSH into AWS EC2
        │
        ▼
docker compose pull
        │
        ▼
docker compose up -d
        │
        ▼
Restart Updated Containers
        │
        ▼
Application Updated Automatically
```

The EC2 instance never builds Docker images locally.

Instead, it always pulls the latest Docker images from Docker Hub and recreates the running containers using Docker Compose. This makes deployments faster, more reliable, and consistent across environments.

The deployment is fully automated using GitHub Actions and executes after every successful push to the `main` branch.

# AWS Deployment

The application has been successfully deployed to an AWS EC2 instance using Docker Compose.

The deployed architecture consists of:

```
Internet
     │
     ▼
AWS EC2
     │
     ├── React Frontend Container
     ├── FastAPI Backend Container
     └── PostgreSQL Container
```

The backend and frontend Docker images are automatically downloaded from Docker Hub during deployment.

## Public Access

During development, the application was accessible using the EC2 public IP.

Example:

```
Frontend
http://<EC2_PUBLIC_IP>:5173

Backend API
http://<EC2_PUBLIC_IP>:8000/docs
```

> **Note**
>
> To minimize AWS costs, the EC2 instance is intentionally stopped after deployment verification.
>
> Therefore, the public IP shown in screenshots or previous documentation may no longer be active.
>
> The application can be brought back online at any time by starting the EC2 instance and redeploying the latest Docker containers.


# Important Project Files

| File | Purpose |
|------|---------|
| `app/main.py` | Starts the FastAPI application |
| `app/api/documents.py` | Handles upload API requests |
| `app/services/orchestrator.py` | Controls the complete document processing pipeline |
| `app/services/extractor.py` | Creates prompts for the LLM |
| `app/services/llm_client.py` | Sends requests to the Mistral model |
| `app/services/validator.py` | Validates extracted information |
| `app/services/corrector.py` | Corrects invalid or incomplete extraction |
| `app/utils/rtf_utils.py` | Converts RTF files into plain text |
| `app/utils/json_parser.py` | Extracts valid JSON from LLM output |
| `app/utils/markdown_renderer.py` | Generates Markdown reports |
| `app/database/database.py` | Creates PostgreSQL connection |
| `app/database/crud.py` | Performs database operations |
| `docker-compose.yml` | Starts all containers together |
| `backend/Dockerfile` | Builds the FastAPI Docker image |
| `frontend/Dockerfile` | Builds the React Docker image |
| `.github/workflows/ci.yml` | GitHub Actions CI/CD workflow |

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | React, Vite |
| Backend | FastAPI, Python |
| AI Model | Mistral LLM |
| Validation | Pydantic |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |
| CI/CD | GitHub Actions |
| Container Registry | Docker Hub |
| Cloud Platform | AWS EC2 |