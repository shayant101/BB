# 🧪 BistroBoard Admin Command Center - Testing & Usage Guide

## 🚀 **Quick Start - How to Test the Admin System**

### **Prerequisites**
Your BistroBoard system is already running:
- ✅ Backend API: `http://localhost:8000`
- ✅ Frontend: `http://localhost:3000`
- ✅ Admin system initialized with user `admin` / `admin123`

---

## 🔑 **Method 1: Using the API Documentation (Easiest)**

### **Step 1: Open the Interactive API Docs**
```bash
# Open in your browser
http://localhost:8000/docs
```

### **Step 2: Login as Admin**
1. Find the **"POST /token"** endpoint
2. Click **"Try it out"**
3. Enter admin credentials:
```json
{
  "username": "admin",
  "password": "admin123"
}
```
4. Click **"Execute"**
5. **Copy the `access_token`** from the response

### **Step 3: Authorize Your Session**
1. Click the **"Authorize"** button at the top of the docs page
2. Enter: `Bearer YOUR_ACCESS_TOKEN_HERE`
3. Click **"Authorize"**

### **Step 4: Test Admin Endpoints**
Now you can test any admin endpoint by clicking "Try it out":

#### **Dashboard Stats**
- Find **"GET /api/admin/dashboard-stats"**
- Click "Try it out" → "Execute"
- See platform metrics

#### **Action Queues**
- Find **"GET /api/admin/action-queues"**
- Click "Try it out" → "Execute"
- See pending vendors and stuck orders

#### **User Management**
- Find **"GET /api/admin/users"**
- Click "Try it out" → "Execute"
- See all users in the system

---

## 💻 **Method 2: Using cURL Commands**

### **Step 1: Get Admin Token**
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Copy the `access_token` from the response**

### **Step 2: Test Dashboard**
```bash
# Replace YOUR_TOKEN with the actual token
curl -X GET "http://localhost:8000/api/admin/dashboard-stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Step 3: View Action Queues**
```bash
curl -X GET "http://localhost:8000/api/admin/action-queues" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Step 4: List All Users**
```bash
curl -X GET "http://localhost:8000/api/admin/users" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Step 5: Test User Impersonation**
```bash
# Impersonate restaurant1 (user ID 1)
curl -X POST "http://localhost:8000/api/admin/users/1/impersonate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"target_user_id": 1, "reason": "Testing user experience for support"}'
```

### **Step 6: View Audit Logs**
```bash
curl -X GET "http://localhost:8000/api/admin/audit-logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 **Method 3: Using the Frontend (Advanced)**

### **Step 1: Login as Admin via Frontend**
1. Go to `http://localhost:3000`
2. Login with: `admin` / `admin123`
3. You'll see the admin role in the interface

### **Step 2: Use Browser Developer Tools**
1. Open Developer Tools (F12)
2. Go to **Console** tab
3. Use JavaScript to make API calls:

```javascript
// Get your token from localStorage or make a login request
const token = "YOUR_ADMIN_TOKEN_HERE";

// Test dashboard stats
fetch('http://localhost:8000/api/admin/dashboard-stats', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(data => console.log('Dashboard Stats:', data));

// Test action queues
fetch('http://localhost:8000/api/admin/action-queues', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(data => console.log('Action Queues:', data));
```

---

## 🧪 **Complete Testing Scenarios**

### **Scenario 1: Platform Health Monitoring**
```bash
# 1. Get admin token
TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 2. Check dashboard stats
curl -X GET "http://localhost:8000/api/admin/dashboard-stats" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 3. Check action queues
curl -X GET "http://localhost:8000/api/admin/action-queues" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### **Scenario 2: User Management**
```bash
# 1. List all users
curl -X GET "http://localhost:8000/api/admin/users" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 2. Get specific user details (user ID 1)
curl -X GET "http://localhost:8000/api/admin/users/1" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 3. View user's order history
curl -X GET "http://localhost:8000/api/admin/users/1/orders" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 4. View user's activity log
curl -X GET "http://localhost:8000/api/admin/users/1/activity" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### **Scenario 3: User Status Management**
```bash
# 1. Deactivate a user (user ID 4 - the pending vendor)
curl -X PUT "http://localhost:8000/api/admin/users/4/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "inactive", "reason": "Testing deactivation functionality"}'

# 2. Reactivate the user
curl -X PUT "http://localhost:8000/api/admin/users/4/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "active", "reason": "Testing reactivation functionality"}'
```

### **Scenario 4: Secure Impersonation**
```bash
# 1. Start impersonation session
IMPERSONATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/admin/users/1/impersonate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"target_user_id": 1, "reason": "Testing user interface for support ticket"}')

echo "Impersonation Response: $IMPERSONATION_RESPONSE"

# 2. Extract impersonation token
IMPERSONATION_TOKEN=$(echo $IMPERSONATION_RESPONSE | grep -o '"impersonation_token":"[^"]*' | cut -d'"' -f4)

# 3. Use impersonation token to access user's data
curl -X GET "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer $IMPERSONATION_TOKEN" | jq '.'
```

### **Scenario 5: Audit Trail Verification**
```bash
# 1. View all audit logs
curl -X GET "http://localhost:8000/api/admin/audit-logs" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 2. Filter audit logs by action type
curl -X GET "http://localhost:8000/api/admin/audit-logs?action=impersonation_started" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 3. View recent audit logs (last 10)
curl -X GET "http://localhost:8000/api/admin/audit-logs?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## 📊 **Expected Test Results**

### **Dashboard Stats Response**
```json
{
  "total_users": 3,
  "total_restaurants": 1,
  "total_vendors": 2,
  "total_orders": 5,
  "pending_vendor_approvals": 1,
  "stuck_orders_count": 0,
  "active_impersonation_sessions": 0,
  "recent_signups_24h": 1
}
```

### **Action Queues Response**
```json
{
  "pending_vendors": [
    {
      "id": 4,
      "name": "Fresh Farms Co.",
      "username": "pending_vendor1",
      "email": "contact@freshfarms.com",
      "created_at": "2025-06-19T11:04:18.436957",
      "days_pending": 0
    }
  ],
  "stuck_orders": []
}
```

### **User List Response**
```json
[
  {
    "id": 1,
    "username": "restaurant1",
    "name": "Mario's Pizzeria",
    "email": "mario@pizzeria.com",
    "role": "restaurant",
    "status": "active",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "last_login_at": "2025-06-19T11:05:27.123456",
    "deactivation_reason": null
  }
]
```

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **"401 Unauthorized" Error**
- **Problem**: Token expired or invalid
- **Solution**: Get a new admin token using the login endpoint

#### **"403 Forbidden" Error**
- **Problem**: User doesn't have admin role
- **Solution**: Ensure you're using the admin account (`admin` / `admin123`)

#### **"404 Not Found" Error**
- **Problem**: Endpoint URL is incorrect
- **Solution**: Check the endpoint path (should start with `/api/admin/`)

#### **Empty Response or No Data**
- **Problem**: Database might not be initialized
- **Solution**: Run the initialization script:
```bash
cd backend && python -m app.admin_init
```

### **Verify System Status**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if admin user exists
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## 🎯 **Real-World Usage Examples**

### **Daily Admin Tasks**

#### **Morning Health Check**
```bash
# Quick platform overview
curl -X GET "http://localhost:8000/api/admin/dashboard-stats" \
  -H "Authorization: Bearer $TOKEN"
```

#### **Approve Pending Vendors**
```bash
# 1. Check pending vendors
curl -X GET "http://localhost:8000/api/admin/action-queues" \
  -H "Authorization: Bearer $TOKEN"

# 2. Approve vendor (change status to active)
curl -X PUT "http://localhost:8000/api/admin/users/4/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "active", "reason": "Vendor verification completed - approved"}'
```

#### **Support Investigation**
```bash
# 1. Find user having issues
curl -X GET "http://localhost:8000/api/admin/users?search=mario" \
  -H "Authorization: Bearer $TOKEN"

# 2. Check their recent activity
curl -X GET "http://localhost:8000/api/admin/users/1/activity" \
  -H "Authorization: Bearer $TOKEN"

# 3. Impersonate to reproduce issue
curl -X POST "http://localhost:8000/api/admin/users/1/impersonate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"target_user_id": 1, "reason": "Investigating reported login issues"}'
```

---

## 🎉 **You're Ready to Use the Admin System!**

The Admin Command Center is fully functional and ready for production use. Start with the **API Documentation method** at `http://localhost:8000/docs` for the easiest testing experience.

**Key Admin Credentials**: `admin` / `admin123`

**All admin endpoints are working and secured with proper authentication and audit logging.**