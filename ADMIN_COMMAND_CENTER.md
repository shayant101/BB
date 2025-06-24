# BistroBoard Admin Command Center

## Overview

The Admin Command Center is a comprehensive backend system designed for BistroBoard administrators to efficiently monitor platform health, manage users, and provide rapid support resolution. This system prioritizes operational efficiency, powerful support capabilities, and robust security.

## 🏗️ Architecture Overview

### Data Model Enhancements

#### Enhanced User Model
- **`is_active`**: Boolean flag for soft delete functionality
- **`status`**: Enum values: "active", "inactive", "pending_approval"
- **`deactivation_reason`**: Text field for audit trail
- **`deactivated_by`**: Foreign key to admin user who performed action
- **`deactivated_at`**: Timestamp of deactivation
- **`last_login_at`**: Track user activity for support

#### New Admin Models

**AdminAuditLog**: Immutable audit trail
- Tracks all admin actions with full context
- Includes IP address, user agent, session ID
- Links admin to target user and action details

**UserEventLog**: User activity tracking
- Login/logout events, profile updates, order creation
- Essential for support and user behavior analysis

**ImpersonationSession**: Secure user impersonation
- Short-lived sessions (5 minutes)
- Full audit trail of impersonation activities
- Automatic expiration and cleanup

## 🔐 Security & RBAC Strategy

### Role-Based Access Control
- **Admin Role**: Full access to all admin endpoints
- **User Roles**: Restaurant/Vendor users cannot access admin functions
- **Token Validation**: Enhanced JWT with impersonation claims

### Impersonation Security Flow
1. **Admin Authentication**: Verify admin credentials
2. **Target Validation**: Ensure target user exists and is not admin
3. **Token Generation**: Create short-lived JWT (5 minutes) with special claims:
   ```json
   {
     "sub": "target_username",
     "user_id": 123,
     "role": "restaurant",
     "is_impersonating": true,
     "impersonator_id": 456,
     "exp": 1640995200
   }
   ```
4. **Session Tracking**: Store session in database for audit
5. **Automatic Expiry**: Tokens expire quickly to minimize risk

### Audit Trail
- **Immutable Logging**: All admin actions permanently recorded
- **Context Capture**: IP, user agent, session details
- **Action Types**: user_created, user_deactivated, user_reactivated, impersonation_started

## 📊 API Endpoints

### Dashboard & Analytics

#### `GET /api/admin/dashboard-stats`
Returns comprehensive platform metrics:
```json
{
  "total_users": 150,
  "total_restaurants": 75,
  "total_vendors": 75,
  "total_orders": 1250,
  "pending_vendor_approvals": 5,
  "stuck_orders_count": 3,
  "active_impersonation_sessions": 0,
  "recent_signups_24h": 8
}
```

#### `GET /api/admin/action-queues`
Items requiring immediate attention:
```json
{
  "pending_vendors": [
    {
      "id": 123,
      "name": "Fresh Farms Co.",
      "username": "pending_vendor1",
      "email": "contact@freshfarms.com",
      "created_at": "2024-01-15T10:30:00Z",
      "days_pending": 3
    }
  ],
  "stuck_orders": [
    {
      "id": 456,
      "restaurant_name": "Mario's Pizzeria",
      "vendor_name": "Fresh Valley Produce",
      "created_at": "2024-01-13T14:20:00Z",
      "hours_stuck": 52,
      "items_text": "10 lbs tomatoes, 5 lbs onions..."
    }
  ]
}
```

### User Management

#### `GET /api/admin/users`
List users with filtering and search:
- **Query Parameters**: `status`, `role`, `search`, `limit`, `offset`
- **Search**: Name, username, email
- **Filters**: Active/inactive, restaurant/vendor

#### `GET /api/admin/users/{user_id}`
Detailed user profile with admin context

#### `POST /api/admin/users`
Manually create user accounts:
```json
{
  "username": "new_restaurant",
  "password": "secure_password",
  "role": "restaurant",
  "name": "New Restaurant",
  "email": "contact@newrestaurant.com",
  "phone": "555-0123",
  "address": "123 Main St",
  "status": "active"
}
```

#### `PUT /api/admin/users/{user_id}/status`
Activate/deactivate users with reason logging:
```json
{
  "status": "inactive",
  "reason": "Violation of terms of service - spam complaints"
}
```

### User Activity & Support

#### `GET /api/admin/users/{user_id}/orders`
Complete order history for support context

#### `GET /api/admin/users/{user_id}/activity`
Combined view of:
- User events (login, profile updates, orders)
- Admin actions performed on the user
- Timeline view for support investigations

### Secure Impersonation

#### `POST /api/admin/users/{user_id}/impersonate`
Generate temporary impersonation token:
```json
{
  "target_user_id": 123,
  "reason": "Debugging order placement issue reported by user"
}
```

**Response**:
```json
{
  "impersonation_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "target_user": {
    "id": 123,
    "username": "restaurant1",
    "name": "Mario's Pizzeria",
    "role": "restaurant"
  },
  "expires_at": "2024-01-15T15:35:00Z"
}
```

### Audit & Compliance

#### `GET /api/admin/audit-logs`
Searchable audit trail with filters:
- **Filters**: `action`, `admin_id`, `target_user_id`
- **Pagination**: `limit`, `offset`
- **Sorting**: Most recent first

## 🎯 Action-Oriented Dashboard Logic

### Action Queues Calculation

**Pending Vendor Approvals**:
```sql
SELECT COUNT(*) FROM users 
WHERE role = 'vendor' AND status = 'pending_approval'
```

**Stuck Orders** (>48 hours pending):
```sql
SELECT COUNT(*) FROM orders 
WHERE status = 'pending' 
AND created_at < datetime('now', '-48 hours')
```

**Recent Activity Monitoring**:
- New signups in last 24 hours
- Active impersonation sessions
- Failed login attempts (future enhancement)

### Dashboard Prioritization
1. **Critical Issues**: Stuck orders, system errors
2. **Approval Queue**: Pending vendors by days waiting
3. **Growth Metrics**: New signups, order volume
4. **Security Alerts**: Active impersonations, suspicious activity

## 🔧 Implementation Details

### Soft Delete Strategy
- **Never hard delete**: Preserve all historical data
- **Status-based filtering**: Use `is_active` and `status` fields
- **Reason logging**: Always capture why action was taken
- **Reversible actions**: Reactivation restores full functionality

### Database Considerations
- **Indexes**: Added on `status`, `is_active`, `created_at` for performance
- **JSON Fields**: Store flexible metadata in `details` columns
- **Foreign Keys**: Maintain referential integrity for audit trails

### Error Handling
- **Validation**: Prevent admin actions on other admins
- **Authorization**: Role-based endpoint protection
- **Audit Failures**: Log failed admin attempts
- **Token Security**: Automatic cleanup of expired sessions

## 🚀 Getting Started

### 1. Database Migration
```bash
cd backend
python app/migrate_admin.py
```

### 2. Initialize Admin System
```bash
python -m app.admin_init
```

### 3. Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`
- **Change immediately in production!**

### 4. Test Admin Endpoints
```bash
# Login as admin
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Get dashboard stats
curl -X GET "http://localhost:8000/api/admin/dashboard-stats" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 📈 Future Enhancements

### Phase 2 Features
- **Real-time Notifications**: WebSocket alerts for critical issues
- **Advanced Analytics**: User behavior patterns, order trends
- **Bulk Operations**: Mass user updates, batch approvals
- **Custom Dashboards**: Role-specific admin views

### Security Enhancements
- **2FA for Admins**: Multi-factor authentication requirement
- **IP Whitelisting**: Restrict admin access by location
- **Session Management**: Force logout, concurrent session limits
- **Advanced Audit**: File integrity monitoring, change detection

### Operational Tools
- **System Health**: Database performance, API response times
- **Automated Actions**: Auto-approve vendors, escalate stuck orders
- **Integration APIs**: Connect with external support tools
- **Reporting**: Scheduled reports, compliance exports

## 🛡️ Security Best Practices

1. **Change Default Credentials**: Immediately update admin password
2. **Use HTTPS**: Never transmit admin tokens over HTTP
3. **Monitor Audit Logs**: Regular review of admin activities
4. **Limit Impersonation**: Use only for legitimate support needs
5. **Regular Backups**: Protect audit trail data
6. **Access Reviews**: Periodic admin permission audits

## 📞 Support & Troubleshooting

### Common Issues
- **Token Expiry**: Impersonation tokens expire in 5 minutes
- **Permission Denied**: Ensure user has admin role
- **Database Locks**: Check for long-running queries during bulk operations

### Monitoring Queries
```sql
-- Active impersonation sessions
SELECT * FROM impersonation_sessions 
WHERE is_active = 1 AND expires_at > datetime('now');

-- Recent admin actions
SELECT * FROM admin_audit_logs 
ORDER BY created_at DESC LIMIT 50;

-- Users needing attention
SELECT * FROM users 
WHERE status = 'pending_approval' 
ORDER BY created_at ASC;
```

---

**The BistroBoard Admin Command Center provides enterprise-grade administrative capabilities while maintaining the simplicity and reliability of the core platform.**