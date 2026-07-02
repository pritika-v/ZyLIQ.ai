#every docker image starts from another image. Here youre saying start with the official python image=linus+python 3.11
#Slim= use a smaller version of linux
FROM python:3.11-slim 

#This sets the current working directory inside the container.-- cd/app-- now copy .. would copy files into /app and not / (root folder)
WORKDIR /app

#apt-get install is for linus commands
# System deps (psycopg2(data driver) needs libpq to communicate with PostgresSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/* 
    #last line deleting unwanted stuff

#copies requirements.txt into /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Dcoker now copies the whole project
#why copy .. after copy requirements.txt This is intentional.Docker caches layers. If you only change Python code, Docker doesn't reinstall every package again. Only your code is recopied.
COPY . .

#creates folder inside the container -p means create parent folder if needed
# Where uploaded RTFs and pipeline outputs live (mounted as a volume in compose)
RUN mkdir -p /data/rtf_files /data/output

#This application listens on port 8000.
EXPOSE 8000

#uvicorn app.main:app --host 0.0.0.0 --port 8000 (0.0.0.0 means listen on every network interface)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

#http://127.0.0.1:8000 127.0.0.1 means: "Only accept requests from inside this machine." therefore we make it 0.0.0.0