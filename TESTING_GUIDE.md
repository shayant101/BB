# BistroBoard Testing Guide

## System Overview

BistroBoard is a marketplace platform connecting restaurants with vendors, featuring:
- **Authentication**: Clerk-based user management
- **Marketplace**: Vendor discovery and product browsing
- **Orders**: Cart-based ordering system with real-time status
- **Dashboard**: Order management and vendor profiles

## Pre-Testing Setup

### 1. Environment Verification
```bash
# Backend (Terminal 1)
cd "bistroboard 2/backend"
python -m uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd "bistroboard 2/frontend"
npm run dev -- --turbo
```

### 2. Service Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl -I http://localhost:3000
```

### 3. Database Connection
Verify MongoDB Atlas connection in backend logs:
```
✅ Successfully connected to MongoDB Atlas
🔄 Initializing Beanie ODM...
✅ Beanie initialized with document models
```

## Authentication Testing

### Test Case 1: User Registration
**Objective**: Verify new user can sign up with Clerk

**Steps**:
1. Navigate to http://localhost:3000
2. Click "Sign Up" button
3. Complete Clerk registration form
4. Verify redirect to dashboard

**Expected Results**:
- ✅ Clerk signup form displays
- ✅ User account created successfully
- ✅ Automatic redirect to `/dashboard`
- ✅ User profile visible in dashboard header

**Backend Verification**:
```
🔍 Created new user for storefront orders: {user_id}
✅ Authentication successful for user: {name} (restaurant)
```

### Test Case 2: User Login
**Objective**: Verify existing user can sign in

**Steps**:
1. Navigate to http://localhost:3000
2. Click "Sign In" button
3. Enter credentials
4. Verify dashboard access

**Expected Results**:
- ✅ Clerk signin form displays
- ✅ Authentication successful
- ✅ Dashboard loads with user data
- ✅ Navigation menu shows user profile

### Test Case 3: Authentication Persistence
**Objective**: Verify session persistence across page refreshes

**Steps**:
1. Sign in to application
2. Navigate to different pages
3. Refresh browser
4. Verify still authenticated

**Expected Results**:
- ✅ User remains signed in after refresh
- ✅ All protected routes accessible
- ✅ API calls include valid tokens

## Marketplace Testing

### Test Case 4: Vendor Listing
**Objective**: Verify marketplace displays vendors correctly

**Steps**:
1. Sign in to application
2. Navigate to `/marketplace`
3. Verify vendor cards display
4. Check pagination if applicable

**Expected Results**:
- ✅ Multiple vendor cards visible
- ✅ Vendor names, images, and details display
- ✅ "View Storefront" buttons functional
- ✅ No authentication errors (401)

**Backend Verification**:
```
🔍 Marketplace auth check - Authorization header: Bearer eyJ...
✅ Clerk token verified: {'clerk_user_id': 'user_...'}
✅ Authentication successful for user: {name} (restaurant)
```

### Test Case 5: Vendor Storefront (Critical Test)
**Objective**: Verify individual vendor storefronts load correctly with proper data

**Steps**:
1. From marketplace, click "View Storefront"
2. Verify vendor name displays correctly (not "Vendor X's Store")
3. Check that products display with proper units and images
4. Verify both storefront and products API endpoints work
5. Test "Add to Cart" functionality

**Expected Results**:
- ✅ Storefront page loads with **actual vendor name** (e.g., "Golden Harvest Co.")
- ✅ Products display with correct **units** (e.g., "each", "lb") and **images**
- ✅ No AttributeError in backend logs
- ✅ Both `/api/storefront/{id}` and `/api/storefront/{id}/products` return 200 OK
- ✅ Add to Cart buttons functional
- ✅ Cart icon updates with item count

**Backend Verification**:
```
🔍 Storefront auth - Clerk user ID: user_...
🔍 Storefront - User: {name} (ID: {id}, Role: restaurant)
INFO: GET /api/storefront/{vendor_id} HTTP/1.1" 200 OK
INFO: GET /api/storefront/{vendor_id}/products HTTP/1.1" 200 OK
```

**Critical Checks**:
- ❌ **FAIL**: Vendor name shows "Vendor 39's Store" → Check `business_name` field in API response
- ❌ **FAIL**: AttributeError in logs → Check `unit_of_measure` and `image_urls` field mapping
- ❌ **FAIL**: 404 on products endpoint → Ensure `/storefront/{id}/products` endpoint exists

## Order Management Testing

### Test Case 6: Cart Functionality
**Objective**: Verify shopping cart operations

**Steps**:
1. Add multiple items to cart
2. Open cart modal
3. Modify quantities
4. Remove items
5. Verify totals calculation

**Expected Results**:
- ✅ Items appear in cart with correct details
- ✅ Quantity controls work properly
- ✅ Subtotal, tax, and total calculate correctly
- ✅ Remove functionality works

### Test Case 7: Order Placement (Critical Test)
**Objective**: Verify complete order flow from cart to dashboard

**Steps**:
1. Add items to cart from vendor storefront
2. Open cart modal
3. Click "Place Order"
4. Verify success message
5. Navigate to dashboard
6. Check "All Orders" tab

**Expected Results**:
- ✅ Order placement succeeds
- ✅ Success message shows order ID
- ✅ Cart clears after order
- ✅ Order appears in dashboard with **product names** (not IDs)
- ✅ Order shows correct vendor, items, and status

**Backend Verification**:
```
🔍 Storefront orders auth - Clerk user ID: user_...
🔍 Creating storefront order for restaurant: {name} (ID: {id})
🔍 Storefront order created: Order {order_id} for restaurant {restaurant_id} from vendor {vendor_id}
```

**Critical Check**: Order should display as:
```
"Baby Spinach - Large: 4 x $5.40"
```
NOT as:
```
"9-15: 4 x $5.40"
```

### Test Case 8: Dashboard Order Display
**Objective**: Verify orders display correctly in dashboard

**Steps**:
1. Navigate to dashboard
2. Check "All Orders" tab
3. Verify order details
4. Check order status

**Expected Results**:
- ✅ All placed orders visible
- ✅ Product names display correctly
- ✅ Vendor information accurate
- ✅ Order status shows "pending"
- ✅ Timestamps are correct

**Backend Verification**:
```
🔍 Orders API - User: {name} (ID: {id}, Role: restaurant)
🔍 Searching for orders with restaurant_id: {id}
🔍 Found {count} orders for restaurant
🔍 Order {order_id}: restaurant_id={id}, vendor_id={vendor_id}, status=pending
```

## API Integration Testing

### Test Case 9: Authentication Headers
**Objective**: Verify all API calls include proper Clerk tokens

**Steps**:
1. Open browser developer tools
2. Navigate through application
3. Monitor Network tab
4. Verify Authorization headers

**Expected Results**:
- ✅ All API calls include `Authorization: Bearer {token}`
- ✅ No 401 Unauthorized responses
- ✅ Tokens refresh automatically when needed

### Test Case 10: Error Handling
**Objective**: Verify graceful error handling

**Steps**:
1. Temporarily stop backend server
2. Try to place an order
3. Restart backend
4. Verify recovery

**Expected Results**:
- ✅ User-friendly error messages
- ✅ No application crashes
- ✅ Automatic recovery when backend returns

## Performance Testing

### Test Case 11: Page Load Times
**Objective**: Verify acceptable performance

**Metrics**:
- ✅ Homepage loads < 3 seconds
- ✅ Dashboard loads < 5 seconds
- ✅ Marketplace loads < 5 seconds
- ✅ Storefront loads < 3 seconds

### Test Case 12: Concurrent Users
**Objective**: Test multiple user sessions

**Steps**:
1. Open multiple browser windows/incognito tabs
2. Sign in with different accounts
3. Perform simultaneous operations
4. Verify no conflicts

## Regression Testing Checklist

After any code changes, verify:

### Authentication
- [ ] Sign up flow works
- [ ] Sign in flow works
- [ ] Session persistence
- [ ] Logout functionality

### Marketplace
- [ ] Vendor listing loads
- [ ] Storefront pages accessible
- [ ] **Vendor names display correctly** (not "Vendor X's Store")
- [ ] Product details display with proper **units and images**
- [ ] **No AttributeError in backend logs**
- [ ] **Both storefront endpoints return 200 OK** (`/storefront/{id}` and `/storefront/{id}/products`)
- [ ] Search/filtering (if implemented)

### Orders
- [ ] Add to cart works
- [ ] Cart operations (modify, remove)
- [ ] Order placement succeeds
- [ ] Orders appear in dashboard
- [ ] **Product names display correctly** (not IDs)

### Dashboard
- [ ] Order history loads
- [ ] User profile displays
- [ ] Navigation works
- [ ] Real-time updates (if implemented)

## Troubleshooting Common Issues

### Issue: Orders showing product IDs instead of names
**Solution**: Verify CartModal sends `name` field and backend uses `item.name`

### Issue: 401 Authentication errors
**Solution**: Check Clerk token in API interceptor and backend verification

### Issue: Frontend not loading
**Solution**: Follow [FRONTEND_TROUBLESHOOTING.md](./FRONTEND_TROUBLESHOOTING.md)

### Issue: Orders not appearing in dashboard
**Solution**: Verify user authentication consistency between order creation and retrieval

### Issue: Storefront AttributeError and 404 Errors
**Symptoms**:
- Storefront pages show AttributeError in backend logs
- Products endpoint returns 404 Not Found
- Vendor name shows as "Vendor X's Store" instead of actual name

**Root Causes**:
1. **AttributeError**: Backend trying to access `item.unit` and `item.image_url` but database model has `unit_of_measure` and `image_urls` (array)
2. **404 Products Endpoint**: Frontend calls `/storefront/{vendor_id}/products` but endpoint doesn't exist
3. **Generic Vendor Name**: Frontend expects `business_name` field but backend only returns `vendor_name`

**Solutions**:
1. **Fix AttributeError** in `backend/app/routers/storefront.py`:
   ```python
   # Change from:
   unit=item.unit,
   image_url=item.image_url,
   
   # To:
   unit=item.unit_of_measure,
   image_url=item.image_urls[0] if item.image_urls else None,
   ```

2. **Add Missing Products Endpoint** in `backend/app/routers/storefront.py`:
   ```python
   @router.get("/storefront/{vendor_id}/products", response_model=List[StorefrontItem])
   async def get_vendor_products(vendor_id: int, current_user: User = Depends(get_current_user)):
       # Implementation similar to get_vendor_storefront but returns only products
   ```

3. **Fix Vendor Name Display** in `StorefrontResponse` model:
   ```python
   # Add to StorefrontResponse:
   business_name: Optional[str] = None
   
   # Set in response:
   business_name=vendor.name,
   ```

**Backend Log Indicators**:
```
# Before fix:
INFO: 127.0.0.1 - "GET /api/storefront/37/products HTTP/1.1" 404 Not Found
AttributeError: 'InventoryItem' object has no attribute 'unit'

# After fix:
INFO: 127.0.0.1 - "GET /api/storefront/37 HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "GET /api/storefront/37/products HTTP/1.1" 200 OK
```

**Testing Verification**:
- [ ] Storefront pages load without backend errors
- [ ] Products display with correct units and images
- [ ] Vendor name shows actual business name, not "Vendor X's Store"
- [ ] Both `/storefront/{id}` and `/storefront/{id}/products` endpoints return 200 OK

## Test Data

### Sample Vendors
- Golden Harvest Co. (ID: 37)
- Fresh Valley Farms (ID: 41)
- Coastal Seafood Supply (ID: 45)

### Sample Products
- Baby Spinach - Large ($7.20)
- Fresh Salmon Fillet - Standard ($24.00)
- Organic Tomatoes ($3.50/lb)

## Automated Testing (Future)

Consider implementing:
- Unit tests for components
- Integration tests for API endpoints
- E2E tests with Playwright/Cypress
- Load testing with Artillery

---
*Last Updated: 2025-08-26*
*System Status: Fully Functional*
*Critical Path: Authentication → Marketplace → Cart → Order → Dashboard*