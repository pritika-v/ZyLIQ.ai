"""
User
    │
    ▼
FastAPI Endpoint
    │
    ▼
get_db()
    │
    ▼
SessionLocal()
    │
    ▼
Creates Session
    │
    ▼
Session uses Engine
    │
    ▼
Engine talks to PostgreSQL
    │
    ▼
Database returns result
    │
    ▼
Session closes

"""
"""
ORM (Object Relational Mapping) is a technique that lets you work with database tables as Python classes and rows as Python objects, instead of writing SQL queries manually.
Engine is needed for the FASTAPI to communicate with Postgresql
SessionLocal=sessionmaker() now SessionLocal can create sessions
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

engine=create_engine(DATABASE_URL, pool_pre_ping=True)

#Now SessionLocal can make sessions, bind=engine means use this engine for this session
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db #Pause FASTAPI until the endpoint finishes executing
    finally:
        db.close()

"""
# Imports the function that creates an Engine.
# An Engine is SQLAlchemy's connection manager that knows how to communicate
# with the database (PostgreSQL, MySQL, SQLite, etc.).
from sqlalchemy import create_engine

# sessionmaker -> Creates a factory that can generate new database Sessions.
# declarative_base -> Creates a parent class that all ORM models will inherit from.
from sqlalchemy.orm import sessionmaker, declarative_base

# Imports the database connection string from config.py.
# Example:
# DATABASE_URL = "postgresql://username:password@localhost:5432/mydatabase"
from app.config import DATABASE_URL


# -----------------------------------------------------------------------------
# ENGINE
# -----------------------------------------------------------------------------

# Creates the SQLAlchemy Engine.
#
# Think of the Engine as the "bridge" between your FastAPI application
# and the database.
#
# It stores:
#   • Database type (PostgreSQL/MySQL/SQLite)
#   • Username
#   • Password
#   • Host
#   • Port
#   • Connection pool
#
# pool_pre_ping=True:
# Before reusing a connection from the connection pool,
# SQLAlchemy checks whether the connection is still alive.
# If the connection has been closed by the database,
# SQLAlchemy automatically creates a new one.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# -----------------------------------------------------------------------------
# SESSION FACTORY
# -----------------------------------------------------------------------------

# Creates a Session Factory.
#
# IMPORTANT:
# This does NOT create a database session yet.
#
# Instead, it creates an object that can generate new Sessions whenever needed.
#
# Later, calling:
#
#     db = SessionLocal()
#
# creates one database session for a request.
#
# autocommit=False
# ----------------
# SQLAlchemy will NOT automatically save changes.
# You must explicitly call:
#
#     db.commit()
#
# This gives you complete control over transactions.
#
#
# autoflush=False
# ----------------
# SQLAlchemy won't automatically send pending changes
# to the database before executing queries.
# You decide when data should be flushed or committed.
#
#
# bind=engine
# -----------
# Associates every Session created by SessionLocal()
# with the Engine created above.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# -----------------------------------------------------------------------------
# BASE CLASS FOR ORM MODELS
# -----------------------------------------------------------------------------

# Creates the base class that every SQLAlchemy model will inherit from.
#
# Example:
#
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#
# By inheriting from Base, SQLAlchemy understands that
# the User class represents a database table.
Base = declarative_base()


# -----------------------------------------------------------------------------
# DATABASE SESSION DEPENDENCY
# -----------------------------------------------------------------------------

def get_db():

    FastAPI dependency that provides one database session
    for every incoming request.

    Flow:
        Request arrives
              ↓
        Create Session
              ↓
        Endpoint uses Session
              ↓
        Request finishes
              ↓
        Session is closed automatically


    # Creates a new database Session.
    #
    # A Session is the object that performs actual database operations:
    #
    # • SELECT
    # • INSERT
    # • UPDATE
    # • DELETE
    #
    # Every request gets its own Session.
    db = SessionLocal()

    try:
        # Sends the Session to the FastAPI endpoint.
        #
        # Example:
        #
        # @app.get("/users")
        # def get_users(db: Session = Depends(get_db)):
        #     ...
        #
        # FastAPI pauses here until the endpoint finishes executing.
        yield db

    finally:
        # Runs AFTER the endpoint completes
        # (whether it succeeds or raises an exception).
        #
        # Closing the Session returns the database connection
        # back to SQLAlchemy's connection pool so it can be reused
        # by future requests.
        db.close()
"""
