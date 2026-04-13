from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from config import settings
from app.models.data_source import DataSource, SourceType
from app.models.document import Document
import os, shutil, uuid

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_STRUCTURED   = {".xlsx", ".xls", ".csv"}
ALLOWED_UNSTRUCTURED = {".pdf", ".docx", ".txt"}


# ── Request body schemas (defined here to keep it simple) ──────────
class GoogleSheetsRequest(BaseModel):
    url: str
    # Example: "https://docs.google.com/spreadsheets/d/SHEET_ID/edit"
    sheet_name: Optional[str] = None
    # Which tab/sheet inside the spreadsheet (default = first one)

class DatabaseConnectionRequest(BaseModel):
    connection_string: str
    # Example: "postgresql://user:pass@host:5432/dbname"
    table_name: str
    # Which table to read from
    query: Optional[str] = None
    # Optional custom SQL query instead of reading whole table
    # Example: "SELECT * FROM sales WHERE year = 2024"


# ── EXISTING: File Upload (keep these exactly as they are) ──────────

@router.post("/structured")
async def upload_structured_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):  
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_STRUCTURED:
        raise HTTPException(400, f"File type '{ext}' not allowed. Use: {ALLOWED_STRUCTURED}")

    uid       = str(uuid.uuid4())[:8]
    filename  = f"{uid}_{file.filename}"
    save_dir  = os.path.join(settings.UPLOAD_DIR, "structured")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    src_type = SourceType.EXCEL if ext in {".xlsx", ".xls"} else SourceType.CSV

    record = DataSource(
        name=file.filename,
        source_type=src_type,
        file_path=file_path,
        file_size=os.path.getsize(file_path)
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message":    "File uploaded successfully",
        "id":         record.id,
        "filename":   file.filename,
        "path":       file_path,
        "size_bytes": record.file_size
    }


@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):  
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_UNSTRUCTURED:
        raise HTTPException(400, f"Use: {ALLOWED_UNSTRUCTURED}")

    uid       = str(uuid.uuid4())[:8]
    filename  = f"{uid}_{file.filename}"
    save_dir  = os.path.join(settings.UPLOAD_DIR, "unstructured")
    # save_dir = uploads/unstructured
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)
    # file_path = uploads/unstructured/1234_report.pdf

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f) #copyfileobj = saves file physically

    record = Document(
        filename=file.filename,
        file_path=file_path,
        file_type=ext.lstrip("."),
        file_size=os.path.getsize(file_path)
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"message": "Document uploaded successfully", "id": record.id, "filename": file.filename}


# ── NEW: Google Sheets URL ──────────────────────────────────────────

@router.post("/google-sheets")
async def connect_google_sheets(
    request: GoogleSheetsRequest,
    db: Session = Depends(get_db)
):
    """
    How Google Sheets reading works:
    1. User gives us a public Google Sheets URL
    2. We extract the SHEET_ID from the URL
    3. We use that ID to build a CSV export URL (Google provides this for free)
    4. We read it directly with pandas — no API key needed for public sheets!

    Example URL:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit
                                           ↑ this is the SHEET_ID 
    """
    import pandas as pd
    import re

    # Step 1: Validate it's actually a Google Sheets URL
    if "docs.google.com/spreadsheets" not in request.url:
        raise HTTPException(400, "URL must be a Google Sheets link")

    # Step 2: Extract the sheet ID from the URL
    # URL format: /spreadsheets/d/{SHEET_ID}/edit
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", request.url)
    if not match:
        raise HTTPException(400, "Could not extract Sheet ID from URL. Make sure the URL is correct.")

    sheet_id = match.group(1)
    # sheet_id is now e.g. "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"

    # Step 3: Build the CSV export URL
    # Google Sheets lets you export any public sheet as CSV using this URL pattern
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if request.sheet_name:
        # If user specifies a sheet/tab name, add it as a parameter
        csv_url += f"&sheet={request.sheet_name}"

    # Step 4: Read the sheet data using pandas
    try:
        df = pd.read_csv(csv_url)
        # pd.read_csv() works with URLs directly — it downloads and parses it
    except Exception as e:
        raise HTTPException(400, f"Could not read Google Sheet. Make sure it is publicly shared. Error: {str(e)}")

    # Step 5: Save the sheet data as a local CSV file
    # (so our agents can read it the same way as uploaded files)
    uid      = str(uuid.uuid4())[:8]
    filename = f"{uid}_gsheet_{sheet_id[:8]}.csv"
    save_dir = os.path.join(settings.UPLOAD_DIR, "structured")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    df.to_csv(file_path, index=False)
    # index=False means don't write the row numbers as a column

    # Step 6: Save record to database
    record = DataSource(
        name=f"Google Sheet: {sheet_id[:12]}...",
        source_type=SourceType.GOOGLE_SHEETS,
        file_path=file_path,       # we store the LOCAL csv path
        url=request.url,           # we also store the original URL
        file_size=os.path.getsize(file_path),
        row_count=len(df),
        columns=df.columns.tolist()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message":    "Google Sheet connected successfully",
        "id":         record.id,
        "sheet_id":   sheet_id,
        "rows":       len(df),
        "columns":    df.columns.tolist(),
        "preview":    df.head(3).to_dict(orient="records")
        # preview = first 3 rows so user can verify it loaded correctly
    }


# ── NEW: SQL Database Connection ────────────────────────────────────

@router.post("/database")
async def connect_database(
    request: DatabaseConnectionRequest,
    db: Session = Depends(get_db)
):
    """
    How SQL database reading works:
    1. User gives us a connection string + table name
    2. We use SQLAlchemy to connect to THEIR database (not our PostgreSQL)
    3. We read the table into a pandas DataFrame using pd.read_sql()
    4. We save it as a CSV file locally
    5. From this point it's treated exactly like an uploaded CSV

    Supported databases:
    - PostgreSQL: postgresql://user:pass@host:5432/dbname
    - MySQL:      mysql+pymysql://user:pass@host:3306/dbname
    - SQLite:     sqlite:///path/to/file.db
    - MSSQL:      mssql+pyodbc://user:pass@host/dbname?driver=ODBC+Driver+17
    """
    import pandas as pd
    from sqlalchemy import create_engine, text, inspect

    # Step 1: Connect to the user's database
    try:
        external_engine = create_engine(request.connection_string)
        # This creates a connection to THEIR database
        # We use "external_engine" to distinguish from OUR app's engine

        # Test the connection immediately
        with external_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            # If this fails, the connection string is wrong

    except Exception as e:
        raise HTTPException(400, f"Database connection failed. Check your connection string. Error: {str(e)}")

    # Step 2: Verify the table exists
    try:
        inspector   = inspect(external_engine)
        all_tables  = inspector.get_table_names()
        # inspector.get_table_names() lists all tables in the database

        if request.table_name not in all_tables:
            raise HTTPException(
                400,
                f"Table '{request.table_name}' not found. Available tables: {all_tables}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Could not inspect database: {str(e)}")

    # Step 3: Read the data
    try:
        if request.query:
            # User provided a custom SQL query
            # Example: "SELECT * FROM sales WHERE year = 2024 LIMIT 1000"
            sql = request.query
        else:
            # Read the whole table
            sql = f"SELECT * FROM {request.table_name}"

        df = pd.read_sql(sql, external_engine)
        # pd.read_sql() runs the SQL and returns a DataFrame

    except Exception as e:
        raise HTTPException(400, f"Query failed: {str(e)}")

    finally:
        external_engine.dispose()
        # Always close the connection when done
        # dispose() closes ALL connections in the pool

    # Step 4: Save as local CSV (same as Google Sheets approach)
    uid       = str(uuid.uuid4())[:8]
    filename  = f"{uid}_db_{request.table_name}.csv"
    save_dir  = os.path.join(settings.UPLOAD_DIR, "structured")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    df.to_csv(file_path, index=False)

    # Step 5: Save to our database
    # NOTE: We do NOT store the connection_string for security
    # Storing passwords in your DB is a security risk
    record = DataSource(
        name=f"DB Table: {request.table_name}",
        source_type=SourceType.DATABASE,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        row_count=len(df),
        columns=df.columns.tolist()
        # url is left None — we don't store connection strings
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message":  "Database table connected successfully",
        "id":       record.id,
        "table":    request.table_name,
        "rows":     len(df),
        "columns":  df.columns.tolist(),
        "preview":  df.head(3).to_dict(orient="records")
    }


# ── List endpoints (keep as is) ─────────────────────────────────────

@router.get("/list/structured")
async def list_structured_files(db: Session = Depends(get_db)):
    sources = db.query(DataSource).filter(
        DataSource.source_type.in_([
            SourceType.EXCEL,
            SourceType.CSV,
            SourceType.GOOGLE_SHEETS,   # now included
            SourceType.DATABASE          # now included
        ])
    ).all()
    return sources


@router.get("/list/documents")
async def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return docs