from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from pydantic import BaseModel

from .database import get_db
from .models import User, Order, AdminAuditLog, UserEventLog, ImpersonationSession, VendorProfile
from .admin_auth import (
    get_current_admin, 
    get_current_user,
    get_token_payload,
    log_admin_action, 
    log_user_event,
    create_impersonation_token,
    get_password_hash,
    AdminUserCreate,
    UserStatusUpdate,
    ImpersonationRequest
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Response Models
class DashboardStats(BaseModel):
    total_users: int
    total_restaurants: int
    total_vendors: int
    total_orders: int
    pending_vendor_approvals: int
    stuck_orders_count: int
    active_impersonation_sessions: int
    recent_signups_24h: int

class ActionQueue(BaseModel):
    pending_vendors: List[Dict[str, Any]]
    stuck_orders: List[Dict[str, Any]]

class UserListResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    role: str
    status: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    deactivation_reason: Optional[str]

class UserDetailResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    phone: str
    address: str
    role: str
    status: str
    is_active: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    deactivation_reason: Optional[str]
    deactivated_by: Optional[int]
    deactivated_at: Optional[datetime]

class UserOrderHistory(BaseModel):
    orders: List[Dict[str, Any]]
    total_orders: int

class UserActivityLog(BaseModel):
    events: List[Dict[str, Any]]
    admin_actions: List[Dict[str, Any]]

class AuditLogResponse(BaseModel):
    id: int
    admin_name: str
    target_user_name: Optional[str]
    action: str
    details: Optional[Dict[str, Any]]
    created_at: datetime
    ip_address: Optional[str]

class ImpersonationResponse(BaseModel):
    impersonation_token: str
    target_user: Dict[str, Any]
    expires_at: datetime

# Dashboard Endpoints
@router.get("/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics and metrics"""
    
    # Basic counts
    total_users = db.query(User).filter(User.role.in_(["restaurant", "vendor"])).count()
    total_restaurants = db.query(User).filter(User.role == "restaurant").count()
    total_vendors = db.query(User).filter(User.role == "vendor").count()
    total_orders = db.query(Order).count()
    
    # Action queue metrics
    pending_vendor_approvals = db.query(User).filter(
        and_(User.role == "vendor", User.status == "pending_approval")
    ).count()
    
    # Orders stuck in pending for > 48 hours
    stuck_threshold = datetime.utcnow() - timedelta(hours=48)
    stuck_orders_count = db.query(Order).filter(
        and_(Order.status == "pending", Order.created_at < stuck_threshold)
    ).count()
    
    # Active impersonation sessions
    active_impersonation_sessions = db.query(ImpersonationSession).filter(
        and_(
            ImpersonationSession.is_active == True,
            ImpersonationSession.expires_at > datetime.utcnow()
        )
    ).count()
    
    # Recent signups (24h)
    recent_threshold = datetime.utcnow() - timedelta(hours=24)
    recent_signups_24h = db.query(User).filter(
        and_(
            User.role.in_(["restaurant", "vendor"]),
            User.created_at > recent_threshold
        )
    ).count()
    
    return DashboardStats(
        total_users=total_users,
        total_restaurants=total_restaurants,
        total_vendors=total_vendors,
        total_orders=total_orders,
        pending_vendor_approvals=pending_vendor_approvals,
        stuck_orders_count=stuck_orders_count,
        active_impersonation_sessions=active_impersonation_sessions,
        recent_signups_24h=recent_signups_24h
    )

@router.get("/action-queues", response_model=ActionQueue)
async def get_action_queues(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get items requiring immediate admin attention"""
    
    # Pending vendor approvals
    pending_vendors = db.query(User).filter(
        and_(User.role == "vendor", User.status == "pending_approval")
    ).limit(10).all()
    
    pending_vendors_data = [
        {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "days_pending": (datetime.utcnow() - user.created_at).days
        }
        for user in pending_vendors
    ]
    
    # Stuck orders (pending > 48h)
    stuck_threshold = datetime.utcnow() - timedelta(hours=48)
    stuck_orders = db.query(Order).filter(
        and_(Order.status == "pending", Order.created_at < stuck_threshold)
    ).limit(10).all()
    
    stuck_orders_data = [
        {
            "id": order.id,
            "restaurant_name": order.restaurant.name,
            "vendor_name": order.vendor.name,
            "created_at": order.created_at,
            "hours_stuck": int((datetime.utcnow() - order.created_at).total_seconds() / 3600),
            "items_text": order.items_text[:100] + "..." if len(order.items_text) > 100 else order.items_text
        }
        for order in stuck_orders
    ]
    
    return ActionQueue(
        pending_vendors=pending_vendors_data,
        stuck_orders=stuck_orders_data
    )

# User Management Endpoints
@router.get("/users", response_model=List[UserListResponse])
async def list_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status: active, inactive, pending_approval"),
    role: Optional[str] = Query(None, description="Filter by role: restaurant, vendor"),
    search: Optional[str] = Query(None, description="Search by name, username, or email"),
    limit: int = Query(50, le=100),
    offset: int = Query(0)
):
    """List all users with filtering and search"""
    
    query = db.query(User).filter(User.role.in_(["restaurant", "vendor"]))
    
    # Apply filters
    if status:
        query = query.filter(User.status == status)
    if role:
        query = query.filter(User.role == role)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    users = query.offset(offset).limit(limit).all()
    
    return [
        UserListResponse(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            role=user.role,
            status=user.status,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            deactivation_reason=user.deactivation_reason
        )
        for user in users
    ]

@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed user information"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserDetailResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        phone=user.phone,
        address=user.address,
        role=user.role,
        status=user.status,
        is_active=user.is_active,
        description=user.description,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        deactivation_reason=user.deactivation_reason,
        deactivated_by=user.deactivated_by,
        deactivated_at=user.deactivated_at
    )

@router.post("/users", response_model=UserDetailResponse)
async def create_user(
    user_data: AdminUserCreate,
    request: Request,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Manually create a new user account"""
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        address=user_data.address,
        description=user_data.description,
        status=user_data.status,
        is_active=user_data.status == "active"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log admin action
    log_admin_action(
        db=db,
        admin_id=admin.id,
        action="user_created",
        target_user_id=new_user.id,
        details={
            "username": user_data.username,
            "role": user_data.role,
            "status": user_data.status
        },
        request=request
    )
    
    return UserDetailResponse(
        id=new_user.id,
        username=new_user.username,
        name=new_user.name,
        email=new_user.email,
        phone=new_user.phone,
        address=new_user.address,
        role=new_user.role,
        status=new_user.status,
        is_active=new_user.is_active,
        description=new_user.description,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        last_login_at=new_user.last_login_at,
        deactivation_reason=new_user.deactivation_reason,
        deactivated_by=new_user.deactivated_by,
        deactivated_at=new_user.deactivated_at
    )

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    request: Request,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Activate/Deactivate a user account"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot modify admin user status")
    
    previous_status = user.status
    previous_active = user.is_active
    
    # Update user status
    user.status = status_update.status
    user.is_active = status_update.status == "active"
    
    if status_update.status == "inactive":
        user.deactivation_reason = status_update.reason
        user.deactivated_by = admin.id
        user.deactivated_at = datetime.utcnow()
    elif status_update.status == "active" and previous_status == "inactive":
        user.deactivation_reason = None
        user.deactivated_by = None
        user.deactivated_at = None
    
    db.commit()
    
    # Log admin action
    action = "user_reactivated" if status_update.status == "active" and not previous_active else "user_deactivated"
    log_admin_action(
        db=db,
        admin_id=admin.id,
        action=action,
        target_user_id=user.id,
        details={
            "previous_status": previous_status,
            "new_status": status_update.status,
            "reason": status_update.reason
        },
        request=request
    )
    
    return {"message": f"User status updated to {status_update.status}"}

# User Activity & Support Endpoints
@router.get("/users/{user_id}/orders", response_model=UserOrderHistory)
async def get_user_orders(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100)
):
    """Get user's order history"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == "restaurant":
        orders = db.query(Order).filter(Order.restaurant_id == user_id).order_by(Order.created_at.desc()).limit(limit).all()
    elif user.role == "vendor":
        orders = db.query(Order).filter(Order.vendor_id == user_id).order_by(Order.created_at.desc()).limit(limit).all()
    else:
        orders = []
    
    total_orders = len(orders)
    
    orders_data = [
        {
            "id": order.id,
            "restaurant_name": order.restaurant.name,
            "vendor_name": order.vendor.name,
            "status": order.status,
            "items_text": order.items_text,
            "notes": order.notes,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }
        for order in orders
    ]
    
    return UserOrderHistory(orders=orders_data, total_orders=total_orders)

@router.get("/users/{user_id}/activity", response_model=UserActivityLog)
async def get_user_activity(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = Query(50, le=200)
):
    """Get user's activity log and admin actions performed on them"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user events
    user_events = db.query(UserEventLog).filter(
        UserEventLog.user_id == user_id
    ).order_by(UserEventLog.created_at.desc()).limit(limit).all()
    
    events_data = [
        {
            "id": event.id,
            "event_type": event.event_type,
            "details": event.details,
            "created_at": event.created_at,
            "ip_address": event.ip_address
        }
        for event in user_events
    ]
    
    # Get admin actions on this user
    admin_actions = db.query(AdminAuditLog).filter(
        AdminAuditLog.target_user_id == user_id
    ).order_by(AdminAuditLog.created_at.desc()).limit(limit).all()
    
    admin_actions_data = [
        {
            "id": action.id,
            "admin_name": action.admin.name,
            "action": action.action,
            "details": action.details,
            "created_at": action.created_at,
            "ip_address": action.ip_address
        }
        for action in admin_actions
    ]
    
    return UserActivityLog(events=events_data, admin_actions=admin_actions_data)

# Impersonation Endpoints
@router.post("/users/{user_id}/impersonate", response_model=ImpersonationResponse)
async def start_impersonation(
    user_id: int,
    impersonation_request: ImpersonationRequest,
    request: Request,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Start an impersonation session for the target user"""
    
    # Verify target user exists and is not an admin
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    if target_user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot impersonate admin users")
    
    # Create impersonation token
    target_user_data = {
        "username": target_user.username,
        "role": target_user.role,
        "name": target_user.name
    }
    
    impersonation_token = create_impersonation_token(
        admin_id=admin.id,
        target_user_id=target_user.id,
        target_user_data=target_user_data
    )
    
    # Store impersonation session
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    session = ImpersonationSession(
        admin_id=admin.id,
        target_user_id=target_user.id,
        session_token=impersonation_token,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    
    # Log admin action
    log_admin_action(
        db=db,
        admin_id=admin.id,
        action="impersonation_started",
        target_user_id=target_user.id,
        details={
            "reason": impersonation_request.reason,
            "target_username": target_user.username,
            "expires_at": expires_at.isoformat()
        },
        request=request
    )
    
    return ImpersonationResponse(
        impersonation_token=impersonation_token,
        target_user={
            "id": target_user.id,
            "username": target_user.username,
            "name": target_user.name,
            "role": target_user.role
        },
        expires_at=expires_at
    )

# Audit Log Endpoints
@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    action: Optional[str] = Query(None, description="Filter by action type"),
    admin_id: Optional[int] = Query(None, description="Filter by admin ID"),
    target_user_id: Optional[int] = Query(None, description="Filter by target user ID"),
    limit: int = Query(50, le=200),
    offset: int = Query(0)
):
    """Get admin audit logs"""
    
    query = db.query(AdminAuditLog)
    
    # Apply filters
    if action:
        query = query.filter(AdminAuditLog.action == action)
    if admin_id:
        query = query.filter(AdminAuditLog.admin_id == admin_id)
    if target_user_id:
        query = query.filter(AdminAuditLog.target_user_id == target_user_id)
    
    audit_logs = query.order_by(AdminAuditLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        AuditLogResponse(
            id=log.id,
            admin_name=log.admin.name,
            target_user_name=log.target_user.name if log.target_user else None,
            action=log.action,
            details=log.details,
            created_at=log.created_at,
            ip_address=log.ip_address
        )
        for log in audit_logs
    ]