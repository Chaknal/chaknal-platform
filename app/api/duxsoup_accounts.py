from fastapi import APIRouter, HTTPException, Depends, Query, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import List, Optional, Dict, Any
import uuid
import csv
import json
import io
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from database.database import get_session
from app.models.duxsoup_user import DuxSoupUser
from app.models.user import User

router = APIRouter(prefix="/api/duxsoup-accounts", tags=["DuxSoup Accounts"])

# =============================================================================
# SCHEMAS
# =============================================================================

class DuxSoupAccountCreate(BaseModel):
    """DuxSoup account creation request"""
    dux_soup_user_id: str = Field(..., min_length=1, description="DuxSoup user ID")
    dux_soup_auth_key: str = Field(..., min_length=1, description="DuxSoup authentication key")
    email: EmailStr = Field(..., description="Email address")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    user_id: Optional[str] = Field(None, description="Link to existing user")

class DuxSoupAccountUpdate(BaseModel):
    """DuxSoup account update request"""
    dux_soup_user_id: Optional[str] = Field(None, min_length=1)
    dux_soup_auth_key: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    user_id: Optional[str] = None

class DuxSoupAccountResponse(BaseModel):
    """DuxSoup account response"""
    id: str
    dux_soup_user_id: str
    dux_soup_auth_key: str
    email: str
    first_name: str
    last_name: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

class DuxSoupAccountListResponse(BaseModel):
    """DuxSoup account list response"""
    accounts: List[DuxSoupAccountResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class BulkDuxSoupAccountRequest(BaseModel):
    """Bulk DuxSoup account creation request"""
    accounts: List[DuxSoupAccountCreate]

class BulkDuxSoupAccountResponse(BaseModel):
    """Bulk DuxSoup account creation response"""
    success: bool
    created_count: int
    skipped_count: int
    errors: List[str]
    created_accounts: List[str]
    skipped_accounts: List[str]

class FilePreviewResponse(BaseModel):
    """File preview response"""
    columns: List[str]
    sample_data: List[Dict[str, Any]]
    total_rows: int
    file_type: str

class BulkImportResponse(BaseModel):
    """Bulk import response"""
    success: bool
    imported_count: int
    skipped_count: int
    errors: List[str]

# =============================================================================
# DUXSOUP ACCOUNT MANAGEMENT
# =============================================================================

@router.post("/", response_model=DuxSoupAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_duxsoup_account(
    account_data: DuxSoupAccountCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new DuxSoup account"""
    try:
        # Check if account already exists
        result = await session.execute(
            select(DuxSoupUser).where(
                (DuxSoupUser.dux_soup_user_id == account_data.dux_soup_user_id) |
                (DuxSoupUser.email == account_data.email)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DuxSoup account with this ID or email already exists"
            )
        
        # Verify user exists if user_id is provided
        if account_data.user_id:
            user_result = await session.execute(
                select(User).where(User.id == account_data.user_id)
            )
            if not user_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User not found"
                )
        
        # Create DuxSoup account
        account = DuxSoupUser(
            id=str(uuid.uuid4()),
            dux_soup_user_id=account_data.dux_soup_user_id,
            dux_soup_auth_key=account_data.dux_soup_auth_key,
            email=account_data.email,
            first_name=account_data.first_name,
            last_name=account_data.last_name,
            user_id=account_data.user_id,
            created_at=datetime.utcnow()
        )
        
        session.add(account)
        await session.commit()
        await session.refresh(account)
        
        return DuxSoupAccountResponse(
            id=account.id,
            dux_soup_user_id=account.dux_soup_user_id,
            dux_soup_auth_key=account.dux_soup_auth_key,
            email=account.email,
            first_name=account.first_name,
            last_name=account.last_name,
            user_id=account.user_id,
            created_at=account.created_at,
            updated_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create DuxSoup account: {str(e)}"
        )

@router.get("/", response_model=DuxSoupAccountListResponse)
async def list_duxsoup_accounts(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Accounts per page"),
    search: Optional[str] = Query(None, description="Search by name, email, or DuxSoup ID"),
    session: AsyncSession = Depends(get_session)
):
    """List all DuxSoup accounts"""
    try:
        # Build query
        query = select(DuxSoupUser)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (DuxSoupUser.first_name.ilike(search_term)) |
                (DuxSoupUser.last_name.ilike(search_term)) |
                (DuxSoupUser.email.ilike(search_term)) |
                (DuxSoupUser.dux_soup_user_id.ilike(search_term))
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(query)
        accounts = result.scalars().all()
        
        # Convert to response models
        account_responses = []
        for account in accounts:
            account_responses.append(DuxSoupAccountResponse(
                id=account.id,
                dux_soup_user_id=account.dux_soup_user_id,
                dux_soup_auth_key=account.dux_soup_auth_key,
                email=account.email,
                first_name=account.first_name,
                last_name=account.last_name,
                user_id=account.user_id,
                created_at=account.created_at,
                updated_at=None
            ))
        
        total_pages = (total + per_page - 1) // per_page
        
        return DuxSoupAccountListResponse(
            accounts=account_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list DuxSoup accounts: {str(e)}"
        )

@router.get("/{account_id}", response_model=DuxSoupAccountResponse)
async def get_duxsoup_account(
    account_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific DuxSoup account"""
    try:
        result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DuxSoup account not found"
            )
        
        return DuxSoupAccountResponse(
            id=account.id,
            dux_soup_user_id=account.dux_soup_user_id,
            dux_soup_auth_key=account.dux_soup_auth_key,
            email=account.email,
            first_name=account.first_name,
            last_name=account.last_name,
            user_id=account.user_id,
            created_at=account.created_at,
            updated_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get DuxSoup account: {str(e)}"
        )

@router.put("/{account_id}", response_model=DuxSoupAccountResponse)
async def update_duxsoup_account(
    account_id: str,
    account_data: DuxSoupAccountUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a DuxSoup account"""
    try:
        # Check if account exists
        result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DuxSoup account not found"
            )
        
        # Check for conflicts if updating unique fields
        if account_data.dux_soup_user_id and account_data.dux_soup_user_id != account.dux_soup_user_id:
            conflict_result = await session.execute(
                select(DuxSoupUser).where(DuxSoupUser.dux_soup_user_id == account_data.dux_soup_user_id)
            )
            if conflict_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="DuxSoup user ID already exists"
                )
        
        if account_data.email and account_data.email != account.email:
            conflict_result = await session.execute(
                select(DuxSoupUser).where(DuxSoupUser.email == account_data.email)
            )
            if conflict_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Verify user exists if user_id is provided
        if account_data.user_id and account_data.user_id != account.user_id:
            user_result = await session.execute(
                select(User).where(User.id == account_data.user_id)
            )
            if not user_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User not found"
                )
        
        # Update account
        update_data = account_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await session.execute(
                update(DuxSoupUser)
                .where(DuxSoupUser.id == account_id)
                .values(**update_data)
            )
            await session.commit()
            
            # Refresh account
            await session.refresh(account)
        
        return DuxSoupAccountResponse(
            id=account.id,
            dux_soup_user_id=account.dux_soup_user_id,
            dux_soup_auth_key=account.dux_soup_auth_key,
            email=account.email,
            first_name=account.first_name,
            last_name=account.last_name,
            user_id=account.user_id,
            created_at=account.created_at,
            updated_at=account.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update DuxSoup account: {str(e)}"
        )

@router.delete("/{account_id}")
async def delete_duxsoup_account(
    account_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a DuxSoup account"""
    try:
        # Check if account exists
        result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DuxSoup account not found"
            )
        
        # Delete account
        await session.execute(
            delete(DuxSoupUser).where(DuxSoupUser.id == account_id)
        )
        await session.commit()
        
        return {"message": "DuxSoup account deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete DuxSoup account: {str(e)}"
        )

@router.post("/bulk", response_model=BulkDuxSoupAccountResponse)
async def bulk_create_duxsoup_accounts(
    request: BulkDuxSoupAccountRequest,
    session: AsyncSession = Depends(get_session)
):
    """Bulk create DuxSoup accounts"""
    try:
        created_accounts = []
        skipped_accounts = []
        errors = []
        
        for account_data in request.accounts:
            try:
                # Check if account already exists
                result = await session.execute(
                    select(DuxSoupUser).where(
                        (DuxSoupUser.dux_soup_user_id == account_data.dux_soup_user_id) |
                        (DuxSoupUser.email == account_data.email)
                    )
                )
                if result.scalar_one_or_none():
                    skipped_accounts.append(account_data.email)
                    continue
                
                # Verify user exists if user_id is provided
                if account_data.user_id:
                    user_result = await session.execute(
                        select(User).where(User.id == account_data.user_id)
                    )
                    if not user_result.scalar_one_or_none():
                        errors.append(f"User not found for account {account_data.email}")
                        continue
                
                # Create DuxSoup account
                account = DuxSoupUser(
                    id=str(uuid.uuid4()),
                    dux_soup_user_id=account_data.dux_soup_user_id,
                    dux_soup_auth_key=account_data.dux_soup_auth_key,
                    email=account_data.email,
                    first_name=account_data.first_name,
                    last_name=account_data.last_name,
                    user_id=account_data.user_id,
                    created_at=datetime.utcnow()
                )
                
                session.add(account)
                created_accounts.append(account_data.email)
                
            except Exception as e:
                errors.append(f"Failed to create account {account_data.email}: {str(e)}")
                continue
        
        await session.commit()
        
        return BulkDuxSoupAccountResponse(
            success=len(errors) == 0,
            created_count=len(created_accounts),
            skipped_count=len(skipped_accounts),
            errors=errors,
            created_accounts=created_accounts,
            skipped_accounts=skipped_accounts
        )
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create DuxSoup accounts: {str(e)}"
        )

# =============================================================================
# FILE UPLOAD ENDPOINTS
# =============================================================================

def parse_csv_file(file_content: bytes) -> tuple[List[str], List[Dict[str, Any]]]:
    """Parse CSV file content and return columns and data"""
    try:
        # Try to decode as UTF-8 first
        try:
            content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            # Try with different encodings
            content = file_content.decode('latin-1')
        
        # Detect delimiter
        first_line = content.split('\n')[0]
        delimiter = ','
        if '\t' in first_line:
            delimiter = '\t'
        elif ';' in first_line:
            delimiter = ';'
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        columns = csv_reader.fieldnames or []
        data = list(csv_reader)
        
        return columns, data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV file: {str(e)}"
        )

def parse_json_file(file_content: bytes) -> tuple[List[str], List[Dict[str, Any]]]:
    """Parse JSON file content and return columns and data"""
    try:
        content = file_content.decode('utf-8')
        data = json.loads(content)
        
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of objects")
        
        if not data:
            return [], []
        
        # Get columns from first object
        columns = list(data[0].keys()) if data else []
        
        return columns, data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse JSON file: {str(e)}"
        )

@router.post("/bulk-preview", response_model=FilePreviewResponse)
async def preview_bulk_import_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """Preview uploaded file for bulk import"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['csv', 'json']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be CSV or JSON format"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Parse file based on extension
        if file_extension == 'csv':
            columns, data = parse_csv_file(file_content)
        else:  # json
            columns, data = parse_json_file(file_content)
        
        # Return preview (first 5 rows)
        sample_data = data[:5]
        
        return FilePreviewResponse(
            columns=columns,
            sample_data=sample_data,
            total_rows=len(data),
            file_type=file_extension
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview file: {str(e)}"
        )

@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_duxsoup_accounts(
    file: UploadFile = File(...),
    field_mapping: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """Bulk import DuxSoup accounts from file"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['csv', 'json']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be CSV or JSON format"
            )
        
        # Parse field mapping
        try:
            mapping = json.loads(field_mapping)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid field mapping format"
            )
        
        # Read and parse file
        file_content = await file.read()
        if file_extension == 'csv':
            columns, data = parse_csv_file(file_content)
        else:  # json
            columns, data = parse_json_file(file_content)
        
        # Validate required fields are mapped
        required_fields = ['dux_soup_user_id', 'dux_soup_auth_key', 'email', 'first_name', 'last_name']
        missing_fields = [field for field in required_fields if field not in mapping or not mapping[field]]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field mappings: {', '.join(missing_fields)}"
            )
        
        # Process accounts
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for row_data in data:
            try:
                # Map fields
                account_data = {}
                for field, column in mapping.items():
                    if column in row_data:
                        account_data[field] = row_data[column]
                    else:
                        account_data[field] = ""
                
                # Validate required fields
                if not all(account_data.get(field) for field in required_fields):
                    errors.append(f"Missing required data in row: {row_data}")
                    continue
                
                # Check if account already exists
                result = await session.execute(
                    select(DuxSoupUser).where(
                        (DuxSoupUser.dux_soup_user_id == account_data['dux_soup_user_id']) |
                        (DuxSoupUser.email == account_data['email'])
                    )
                )
                if result.scalar_one_or_none():
                    skipped_count += 1
                    continue
                
                # Create DuxSoup account
                account = DuxSoupUser(
                    id=str(uuid.uuid4()),
                    dux_soup_user_id=account_data['dux_soup_user_id'],
                    dux_soup_auth_key=account_data['dux_soup_auth_key'],
                    email=account_data['email'],
                    first_name=account_data['first_name'],
                    last_name=account_data['last_name'],
                    user_id=None,  # Can be linked later
                    created_at=datetime.utcnow()
                )
                
                session.add(account)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Failed to process row: {str(e)}")
                continue
        
        await session.commit()
        
        return BulkImportResponse(
            success=len(errors) == 0,
            imported_count=imported_count,
            skipped_count=skipped_count,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk import accounts: {str(e)}"
        )


