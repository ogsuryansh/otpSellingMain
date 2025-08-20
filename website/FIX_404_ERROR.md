# Fix 404 Error - Step by Step Guide

## Current Issue
You're getting a 404 error on the main page. The logs show:
```
📥 GET /favicon.png - 2025-08-20T17:50:01.811Z
📤 GET / - 404 (1ms)
```

## Root Cause
The issue is likely with the Vercel configuration and routing. Here's how to fix it:

## Step 1: Use the Simple Server

I've created `vercel-server-simple.js` which is more reliable. The configuration has been updated to use this file.

## Step 2: Verify Your Current Setup

Your current files should be:
- ✅ `vercel.json` - Updated with `rewrites` instead of `routes`
- ✅ `vercel-server-simple.js` - New simple server
- ✅ `package.json` - Updated to use simple server

## Step 3: Test Locally First

```bash
# Test the simple server
node vercel-server-simple.js

# In another terminal, test the endpoints
curl http://localhost:3000/
curl http://localhost:3000/api/health
curl http://localhost:3000/test
```

## Step 4: Deploy to Vercel

### Option A: Using Vercel CLI
```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Deploy
vercel --prod
```

### Option B: Using Git
1. Commit your changes
2. Push to GitHub/GitLab
3. Vercel will auto-deploy

## Step 5: Check Environment Variables

Make sure these are set in your Vercel dashboard:

**Required:**
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/otp_bot
MONGODB_DATABASE=otp_bot
NODE_ENV=production
```

**Optional:**
```bash
APP_URL=https://your-app.vercel.app
SESSION_SECRET=your_session_secret_here
```

## Step 6: Test the Deployment

After deployment, test these endpoints:

1. **Health Check**: `https://your-app.vercel.app/api/health`
2. **Main Page**: `https://your-app.vercel.app/`
3. **Test Route**: `https://your-app.vercel.app/test`

## Step 7: Debugging

If you still get 404 errors:

### Check Vercel Logs
1. Go to Vercel dashboard
2. Click on your project
3. Go to "Functions" tab
4. Check the logs for errors

### Check Build Logs
1. In Vercel dashboard, go to "Deployments"
2. Click on the latest deployment
3. Check build logs for errors

## Step 8: Alternative Solutions

### If the simple server doesn't work:

1. **Use the minimal server**:
   ```bash
   # Rename files
   mv vercel.json vercel.json.backup
   mv vercel-minimal.json vercel.json
   mv index.js vercel-server.js
   ```

2. **Use the robust server**:
   ```bash
   # Update vercel.json to use robust server
   # Change "src": "vercel-server-simple.js" to "src": "vercel-server-robust.js"
   ```

## Step 9: Expected Results

After fixing, you should see:

### Health Check Response:
```json
{
  "status": "ok",
  "timestamp": "2025-08-20T17:50:01.811Z",
  "environment": "production",
  "message": "Vercel deployment is working!"
}
```

### Main Page Response:
```json
{
  "message": "Hello from Vercel!",
  "status": "success",
  "timestamp": "2025-08-20T17:50:01.811Z",
  "routes": [
    "/api/health",
    "/test",
    "/admin-dashboard"
  ]
}
```

## Step 10: If Still Not Working

1. **Check MongoDB connection** - Make sure your MongoDB Atlas cluster allows connections from all IPs (0.0.0.0/0)

2. **Try the emergency fallback**:
   ```bash
   # Use the minimal setup
   mv vercel.json vercel.json.backup
   mv vercel-minimal.json vercel.json
   ```

3. **Contact Vercel support** if the issue persists

## Quick Commands

```bash
# Test locally
npm start

# Deploy to Vercel
vercel --prod

# Check logs
vercel logs

# Test endpoints
curl https://your-app.vercel.app/api/health
curl https://your-app.vercel.app/
```

## Success Indicators

✅ Health endpoint returns 200  
✅ Main page returns 200  
✅ No 404 errors in logs  
✅ Database connects successfully  
✅ All routes accessible  

## Next Steps After Fix

1. Test all your application routes
2. Set up proper environment variables
3. Configure your MongoDB Atlas cluster
4. Set up monitoring and logging
5. Configure custom domain if needed
