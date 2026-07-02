import os
"""
configuration management—telling the application
where everything is located without hardcoding 
values throughout the project.
"""
"""
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
Create this folder if it doesn't already exist.
exist_ok=True---"That's okay. If the folder already exists, do nothing."
"""

#os.path
#Instead of manually writing
#C:\Users\Pritika\Documents
#you let Python build paths correctly for the operating system.


"""
os.path.dirname(__file__)
It gives the folder containing the current file.
"""

"""
os.path.join("project","prompts")
On Windows it becomes
project\prompts
folder = "project"
file = "data.txt"
path = os.path.join(folder, file)---> project\data.txt
"""
"""
RTF_FOLDER = os.getenv(
    "RTF_FOLDER",
    "/data/rtf_files"
)

Again,
check environment variable.
Otherwise
/data/rtf_files
This is where input RTF files will be stored.
"""
# ── Same config as the notebook (Cell 3) ──
"""
An environment variable is simply
a variable stored by the operating system that programs can read.
"""

LLM_URL=os.getenv("LLM_URL", "http://13.203.166.127:8672/api/mixlarge/generate/config")
#"Check whether there is an environment variable called LLM_URL." If yes, use that. else use the url that is pasted

PROMPTS_DIR=os.path.join(os.path.dirname(__file__),"prompts")
EXTRACTION_PROMPT_DOC=os.path.join(PROMPTS_DIR, "extractor_prompt.txt")
CORRECTION_PROMPT_DOC=os.path.join(PROMPTS_DIR, "correction_prompt.txt")
REVIEW_PROMPT_DOC = os.path.join(PROMPTS_DIR, "review_prompt.txt")


RTF_FOLDER=os.getenv("RTF_FOLDER","/data/rtf_files")
OUTPUT_FOLDER=os.getenv("OUTPUT_FOLDER","/data/output")
os.makedirs(OUTPUT_FOLDER,exist_ok=True)
os.makedirs(RTF_FOLDER,exist_ok=True)

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3")) # max correction loop attempts

# Database connection 
#format -postgresql://username:password@hostname:port/database

DATABASE_URL=os.getenv("DATABASE_URL","postgresql://postgres:postgres@db:5432/clinical_pipeline")
"""
Now suppose you never install PostgreSQL.
Instead, you write
services:
  db:
    image: postgres:17
Docker sees this and says
"I know what postgres:17 is."
It downloads the official PostgreSQL image.

Docker Hub
↓
postgres:17 Image
↓
Contains

• Ubuntu/Linux
• PostgreSQL installed
• Startup scripts

Nothing is installed on Windows.
Instead, Docker creates a container.
When docker starts the container, all tables, users, database is all created, we dont have to manull do it in postgresql

So where are you actually connecting?

There are two different perspectives:
Inside Docker (container to container)
Your FastAPI application connects to
db:5432
because both containers are on the same Docker network.

From your laptop
Your database client (pgAdmin, DBeaver, etc.) connects to
localhost:5432
because Docker forwards your laptop's port to the PostgreSQL container.

So you're not connecting to a PostgreSQL installation on Windows.
You're connecting to a PostgreSQL server running inside its
own Docker container, and Docker manages the networking and
initialization for you. This is one of the main reasons Docker
is so popular: every developer gets the same PostgreSQL version 
and configuration without installing it directly on their
operating system.
"""