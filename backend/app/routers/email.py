from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from ..email_service import EmailService
from ..auth_simple import verify_token
from ..mongo_models import User, EmailLog, EmailTemplate
from fastapi import Header, status

router = APIRouter()

# Pydantic models
class EmailRequest(BaseModel):
    to_email: EmailStr
    template_type: str  # "welcome", "new_order", "order_confirmation"
    template_data: Dict[str, Any]
    user_id: Optional[int] = None

class EmailResponse(BaseModel):
    success: bool
    message: str
    email_log_id: Optional[str] = None

class EmailTemplateResponse(BaseModel):
    template_id: str
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: List[str] = []
    is_active: bool
    created_at: str
    updated_at: str

class EmailLogResponse(BaseModel):
    log_id: str
    user_id: Optional[int] = None
    to_email: str
    template_type: str
    template_id: str
    subject: str
    status: str
    external_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}
    sent_at: str
    delivered_at: Optional[str] = None

# Dependency to get current user from JWT token
async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )
    
    token = authorization.split(" ")[1]
    token_data = verify_token(token)
    user = await User.find_one(User.username == token_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/send", response_model=EmailResponse)
async def send_email(
    email_request: EmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Send transactional email"""
    try:
        # Only allow admins to send arbitrary emails
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can send emails directly"
            )
        
        email_service = EmailService()
        
        # Add background task to send email
        background_tasks.add_task(
            email_service._send_email,
            to_email=email_request.to_email,
            template_type=email_request.template_type,
            template_data=email_request.template_data,
            user_id=email_request.user_id
        )
        
        return EmailResponse(
            success=True,
            message="Email queued for sending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue email: {str(e)}"
        )

@router.get("/templates", response_model=List[EmailTemplateResponse])
async def get_email_templates(current_user: User = Depends(get_current_user)):
    """Get available email templates"""
    try:
        # Only allow admins to view templates
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view email templates"
            )
        
        templates = await EmailTemplate.find(EmailTemplate.is_active == True).to_list()
        
        return [
            EmailTemplateResponse(
                template_id=template.template_id,
                name=template.name,
                subject=template.subject,
                html_content=template.html_content,
                text_content=template.text_content,
                variables=template.variables,
                is_active=template.is_active,
                created_at=template.created_at.isoformat(),
                updated_at=template.updated_at.isoformat()
            )
            for template in templates
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email templates: {str(e)}"
        )

@router.get("/logs/{user_id}", response_model=List[EmailLogResponse])
async def get_email_logs(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get email logs for a user (admin only)"""
    try:
        # Only allow admins to view email logs
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view email logs"
            )
        
        logs = await EmailLog.find(EmailLog.user_id == user_id).sort(-EmailLog.sent_at).to_list()
        
        return [
            EmailLogResponse(
                log_id=log.log_id,
                user_id=log.user_id,
                to_email=log.to_email,
                template_type=log.template_type,
                template_id=log.template_id,
                subject=log.subject,
                status=log.status,
                external_id=log.external_id,
                error_message=log.error_message,
                metadata=log.metadata,
                sent_at=log.sent_at.isoformat(),
                delivered_at=log.delivered_at.isoformat() if log.delivered_at else None
            )
            for log in logs
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email logs: {str(e)}"
        )

@router.get("/logs", response_model=List[EmailLogResponse])
async def get_all_email_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all email logs (admin only)"""
    try:
        # Only allow admins to view all email logs
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view email logs"
            )
        
        logs = await EmailLog.find().sort(-EmailLog.sent_at).limit(limit).to_list()
        
        return [
            EmailLogResponse(
                log_id=log.log_id,
                user_id=log.user_id,
                to_email=log.to_email,
                template_type=log.template_type,
                template_id=log.template_id,
                subject=log.subject,
                status=log.status,
                external_id=log.external_id,
                error_message=log.error_message,
                metadata=log.metadata,
                sent_at=log.sent_at.isoformat(),
                delivered_at=log.delivered_at.isoformat() if log.delivered_at else None
            )
            for log in logs
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email logs: {str(e)}"
        )