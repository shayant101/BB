# 🔗 Clerk Webhook Setup Guide

This guide will help you configure Clerk webhooks to automatically sync user creation with your BistroBoard database.

## 📋 Prerequisites

- Access to your Clerk Dashboard
- Your backend API deployed and accessible via HTTPS
- Webhook secret from Clerk

## 🚀 Step-by-Step Setup

### Step 1: Access Clerk Dashboard

1. Go to [Clerk Dashboard](https://dashboard.clerk.com/)
2. Select your BistroBoard application
3. Navigate to **"Webhooks"** in the left sidebar

### Step 2: Create New Webhook

1. Click **"Add Endpoint"** or **"Create Webhook"**
2. Enter your webhook URL:
   ```
   https://your-domain.com/webhooks/clerk
   ```
   
   **Examples:**
   - Production: `https://bistroboard-api.onrender.com/webhooks/clerk`
   - Development: `https://your-ngrok-url.ngrok.io/webhooks/clerk`

### Step 3: Configure Events

Select the following events to subscribe to:
- ✅ `user.created` - When a new user signs up
- ✅ `user.updated` - When user profile is updated
- ✅ `user.deleted` - When user account is deleted

### Step 4: Get Webhook Secret

1. After creating the webhook, Clerk will provide a **Webhook Secret**
2. Copy this secret (it looks like: `whsec_1234567890abcdef...`)
3. Add it to your backend environment variables

### Step 5: Update Environment Variables

Add the webhook secret to your backend `.env` file:

```bash
# Clerk Webhook Configuration
CLERK_WEBHOOK_SECRET=whsec_your_actual_webhook_secret_here
```

**Important:** Replace `whsec_your_actual_webhook_secret_here` with your actual webhook secret from Clerk.

### Step 6: Test the Webhook

1. In Clerk Dashboard, find your webhook and click **"Test"**
2. Send a test `user.created` event
3. Check your backend logs for successful processing
4. Verify the test user appears in your admin panel

## 🔧 Development Setup (Using ngrok)

If you're testing locally, you'll need to expose your local server:

1. Install ngrok: `npm install -g ngrok`
2. Start your backend: `cd backend && python3 -m uvicorn app.main:app --reload --port 8000`
3. In another terminal: `ngrok http 8000`
4. Use the ngrok HTTPS URL in Clerk webhook configuration

## 🐛 Troubleshooting

### Webhook Not Receiving Events

1. **Check URL accessibility:**
   ```bash
   curl -X POST https://your-domain.com/webhooks/clerk \
     -H "Content-Type: application/json" \
     -d '{"test": "webhook"}'
   ```

2. **Verify webhook secret:**
   - Ensure `CLERK_WEBHOOK_SECRET` matches exactly what Clerk provides
   - Check for extra spaces or characters

3. **Check backend logs:**
   - Look for webhook processing messages
   - Verify no authentication errors

### Users Still Not Syncing

1. **Verify events are selected:**
   - Ensure `user.created` is checked in Clerk webhook configuration

2. **Check webhook endpoint:**
   - Confirm the endpoint URL is correct and accessible
   - Test with a simple HTTP client

3. **Review signature verification:**
   - The webhook uses HMAC-SHA256 signature verification
   - Ensure the secret is correctly configured

## 📝 Webhook Payload Example

When a user signs up, Clerk sends this payload to your webhook:

```json
{
  "data": {
    "id": "user_31ZNVZvLZ5kYQdFcCveZENmFBVB",
    "email_addresses": [
      {
        "id": "idn_31ZNVZvLZ5kYQdFcCveZENmFBVB",
        "email_address": "user@example.com"
      }
    ],
    "primary_email_address_id": "idn_31ZNVZvLZ5kYQdFcCveZENmFBVB",
    "first_name": "John",
    "last_name": "Doe"
  },
  "object": "event",
  "type": "user.created"
}
```

## ✅ Verification Steps

After setup, verify everything works:

1. **Create a test user** in your app
2. **Check admin panel** - user should appear immediately
3. **Check backend logs** - should show webhook processing
4. **Verify user data** - email, name should be correctly populated

## 🔒 Security Notes

- Always use HTTPS for webhook URLs
- Keep your webhook secret secure and never commit it to version control
- Regularly rotate webhook secrets for security
- Monitor webhook logs for suspicious activity

## 📞 Support

If you encounter issues:
1. Check Clerk Dashboard webhook logs
2. Review backend application logs
3. Verify network connectivity and firewall settings
4. Test webhook endpoint manually with curl

---

**Next Steps:** Once webhooks are configured, your Gmail users (`shayan.s.toor@gmail.com` and `shayantoor1@gmail.com`) should automatically sync when they sign up again or when you trigger a user sync event.