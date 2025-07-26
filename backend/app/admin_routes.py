from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel
import math

from .mongo_models import User, Order, AdminAuditLog, UserEventLog, ImpersonationSession
from .admin_auth import (
    get_current_admin,
    log_admin_action,
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
    user_id: int
    username: str
    name: str
    email: str
    role: str
    status: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

class ImpersonationResponse(BaseModel):
    impersonation_token: str
    target_user: Dict[str, Any]
    expires_at: datetime

class AuditLogResponse(BaseModel):
    log_id: int
    admin_name: str
    target_user_name: Optional[str] = None
    action: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    ip_address: Optional[str] = None

@router.get("/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats(admin: User = Depends(get_current_admin)):
    total_users = await User.find(User.role.in_(["restaurant", "vendor"])).count()
    total_restaurants = await User.find(User.role == "restaurant").count()
    total_vendors = await User.find(User.role == "vendor").count()
    total_orders = await Order.find().count()
    pending_vendor_approvals = await User.find(User.role == "vendor", User.status == "pending_approval").count()
    
    stuck_threshold = datetime.utcnow() - timedelta(hours=48)
    stuck_orders_count = await Order.find(Order.status == "pending", Order.created_at < stuck_threshold).count()
    
    active_impersonation_sessions = await ImpersonationSession.find(
        ImpersonationSession.is_active == True,
        ImpersonationSession.expires_at > datetime.utcnow()
    ).count()
    
    recent_threshold = datetime.utcnow() - timedelta(hours=24)
    recent_signups_24h = await User.find(
        User.role.in_(["restaurant", "vendor"]),
        User.created_at > recent_threshold
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
async def get_action_queues(admin: User = Depends(get_current_admin)):
    pending_vendors = await User.find(User.role == "vendor", User.status == "pending_approval").limit(10).to_list()
    pending_vendors_data = [
        {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at
        } for user in pending_vendors
    ]
    
    stuck_threshold = datetime.utcnow() - timedelta(hours=48)
    stuck_orders = await Order.find(Order.status == "pending", Order.created_at < stuck_threshold).limit(10).to_list()
    stuck_orders_data = [
        {
            "order_id": order.order_id,
            "restaurant_name": order.restaurant.name,
            "vendor_name": order.vendor.name,
            "created_at": order.created_at
        } for order in stuck_orders
    ]
    
    return ActionQueue(
        pending_vendors=pending_vendors_data,
        stuck_orders=stuck_orders_data
    )

@router.get("/users", response_model=List[UserListResponse])
async def list_users(
    admin: User = Depends(get_current_admin),
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    query_conditions = [User.role.in_(["restaurant", "vendor"])]
    if status:
        query_conditions.append(User.status == status)
    if role:
        query_conditions.append(User.role == role)
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        query_conditions.append(
            {"$or": [{"name": search_regex}, {"username": search_regex}, {"email": search_regex}]}
        )
    
    users = await User.find(*query_conditions).to_list()
    return [UserListResponse(**user.dict()) for user in users]

@router.post("/users", response_model=UserListResponse)
async def create_user(user_data: AdminUserCreate, request: Request, admin: User = Depends(get_current_admin)):
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    last_user = await User.find().sort(-User.user_id).limit(1).first_or_none()
    next_user_id = (last_user.user_id + 1) if last_user else 1

    new_user = User(
        user_id=next_user_id,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        **user_data.dict(exclude={"password"})
    )
    await new_user.insert()
    
    await log_admin_action(
        admin_id=admin.user_id,
        action="user_created",
        target_user_id=new_user.user_id,
        details={"username": new_user.username, "role": new_user.role},
        request=request
    )
    return UserListResponse(**new_user.dict())

@router.put("/users/{user_id}/status")
async def update_user_status(user_id: int, status_update: UserStatusUpdate, request: Request, admin: User = Depends(get_current_admin)):
    user = await User.find_one(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot modify admin user status")
    
    previous_status = user.status
    user.status = status_update.status
    user.is_active = status_update.status == "active"
    if status_update.status == "inactive":
        user.deactivation_reason = status_update.reason
        user.deactivated_by = admin.user_id
        user.deactivated_at = datetime.utcnow()
    else:
        user.deactivation_reason = None
        user.deactivated_by = None
        user.deactivated_at = None
    
    await user.save()
    
    await log_admin_action(
        admin_id=admin.user_id,
        action="user_status_updated",
        target_user_id=user.user_id,
        details={"previous_status": previous_status, "new_status": user.status, "reason": status_update.reason},
        request=request
    )
    return {"message": f"User status updated to {user.status}"}

@router.post("/users/{user_id}/impersonate", response_model=ImpersonationResponse)
async def start_impersonation(user_id: int, impersonation_request: ImpersonationRequest, request: Request, admin: User = Depends(get_current_admin)):
    target_user = await User.find_one(User.user_id == user_id)
    if not target_user or target_user.role == "admin":
        raise HTTPException(status_code=404, detail="Target user not found or is an admin")
    
    impersonation_token = create_impersonation_token(
        admin_id=admin.user_id,
        target_user_id=target_user.user_id,
        target_user_data=target_user.dict()
    )
    
    expires_at = datetime.utcnow() + timedelta(minutes=IMPERSONATION_TOKEN_EXPIRE_MINUTES)
    session = ImpersonationSession(
        admin_id=admin.user_id,
        target_user_id=target_user.user_id,
        session_token=impersonation_token,
        expires_at=expires_at
    )
    await session.insert()
    
    await log_admin_action(
        admin_id=admin.user_id,
        action="impersonation_started",
        target_user_id=target_user.user_id,
        details={"reason": impersonation_request.reason},
        request=request
    )
    
    return ImpersonationResponse(
        impersonation_token=impersonation_token,
        target_user=target_user.dict(),
        expires_at=expires_at
    )

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    admin: User = Depends(get_current_admin),
    action: Optional[str] = Query(None),
    admin_id: Optional[int] = Query(None),
    target_user_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200)
):
    query_conditions = []
    if action:
        query_conditions.append(AdminAuditLog.action == action)
    if admin_id:
        query_conditions.append(AdminAuditLog.admin_id == admin_id)
    if target_user_id:
        query_conditions.append(AdminAuditLog.target_user_id == target_user_id)
    
    audit_logs = await AdminAuditLog.find(*query_conditions).sort(-AdminAuditLog.created_at).limit(limit).to_list()
    
    response = []
    for log in audit_logs:
        admin_user = await User.find_one(User.user_id == log.admin_id)
        target_user = await User.find_one(User.user_id == log.target_user_id) if log.target_user_id else None
        response.append(AuditLogResponse(
            log_id=log.log_id,
            admin_name=admin_user.name if admin_user else "Unknown",
            target_user_name=target_user.name if target_user else None,
            **log.dict(exclude={"log_id", "admin_name", "target_user_name"})
        ))
    return response