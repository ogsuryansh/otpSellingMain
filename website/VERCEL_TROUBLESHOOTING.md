# Vercel 404 Error Troubleshooting Guide

## Error: 404 NOT_FOUND

If you're getting a 404 error when deploying to Vercel, follow these steps to resolve it:

## Step 1: Check Your Vercel Configuration

### Option A: Use the Simplified Configuration
Replace your `vercel.json` with this simplified version:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "vercel-server.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/styles/(.*)",
      "dest": "/public/styles/$1"
    },
    {
      "src": "/public/(.*)",
      "dest": "/public/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/vercel-server.js"
    }
  ]
}
```

### Option B: Use the Newer Configuration Format
If the above doesn't work, try this newer format:

```json
{
  "functions": {
    "vercel-server.js": {
      "maxDuration": 30
    }
  },
  "rewrites": [
    {
      "source": "/styles/(.*)",
      "destination": "/public/styles/$1"
    },
    {
      "source": "/public/(.*)",
      "destination": "/public/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/vercel-server.js"
    }
  ]
}
```

## Step 2: Use the Robust Server

Replace your `vercel-server.js` with `vercel-server-robust.js` which handles database connection failures gracefully.

## Step 3: Check Environment Variables

Make sure you have set these environment variables in your Vercel dashboard:

### Required Variables:
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/otp_bot
MONGODB_DATABASE=otp_bot
NODE_ENV=production
```

### Optional Variables:
```bash
APP_URL=https://your-app.vercel.app
SESSION_SECRET=your_session_secret_here
DEFAULT_TODAYS_EARNINGS=₹0
DEFAULT_TOTAL_EARNINGS=₹0
DEFAULT_TODAYS_USERS=0
DEFAULT_TOTAL_USERS=0
DEFAULT_TODAYS_SOLD=0
DEFAULT_TOTAL_SOLD=0
```

## Step 4: Verify File Structure

Ensure your project has this structure:
```
├── vercel.json
├── vercel-server.js (or vercel-server-robust.js)
├── package.json
├── config/
│   └── database.js
├── views/
│   └── v3/
├── public/
│   └── styles/
└── node_modules/
```

## Step 5: Check Package.json

Make sure your `package.json` has:
```json
{
  "main": "vercel-server.js",
  "scripts": {
    "start": "node vercel-server.js"
  }
}
```

## Step 6: Test Locally First

Before deploying to Vercel, test locally:

```bash
# Install dependencies
npm install

# Test the server locally
npm start

# Or test the robust version
node vercel-server-robust.js
```

## Step 7: Check Vercel Logs

1. Go to your Vercel dashboard
2. Click on your project
3. Go to "Functions" tab
4. Check the logs for any errors

## Step 8: Alternative Deployment Methods

### Method 1: Use Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow the prompts
```

### Method 2: Use Git Integration
1. Push your code to GitHub/GitLab
2. Connect your repository to Vercel
3. Deploy automatically

## Step 9: Common Issues and Solutions

### Issue 1: Database Connection Fails
**Solution**: Use `vercel-server-robust.js` which handles database failures gracefully.

### Issue 2: Static Files Not Loading
**Solution**: Check that your `public` folder structure is correct.

### Issue 3: Environment Variables Not Set
**Solution**: Make sure all environment variables are set in Vercel dashboard.

### Issue 4: Node.js Version Issues
**Solution**: Add this to your `package.json`:
```json
{
  "engines": {
    "node": ">=14.0.0"
  }
}
```

## Step 10: Debugging Steps

1. **Check Health Endpoint**: Visit `https://your-app.vercel.app/api/health`
2. **Check Build Logs**: Look at the build logs in Vercel dashboard
3. **Check Function Logs**: Look at the function logs for runtime errors
4. **Test Database Connection**: Make sure your MongoDB URI is correct

## Step 11: Final Checklist

- [ ] Environment variables set in Vercel
- [ ] MongoDB Atlas cluster accessible from all IPs (0.0.0.0/0)
- [ ] All dependencies in package.json
- [ ] vercel.json configuration correct
- [ ] Server file exports correctly
- [ ] Static files in correct location
- [ ] Views folder structure correct

## Step 12: If Still Not Working

1. **Try the robust server**: Use `vercel-server-robust.js`
2. **Check MongoDB**: Ensure your database is accessible
3. **Simplify**: Remove database dependency temporarily to test basic deployment
4. **Contact Support**: Use Vercel's support if issues persist

## Quick Fix Commands

```bash
# Test locally
npm start

# Check if server loads
node -e "console.log('Testing...'); const app = require('./vercel-server.js'); console.log('✅ Server loaded');"

# Deploy with Vercel CLI
vercel --prod
```

## Emergency Fallback

If nothing works, create a minimal `index.js`:

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Vercel!' });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

module.exports = app;
```

And use this `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.js",
      "use": "@vercel/node"
    }
  ]
}
```

This will at least get your deployment working, then you can gradually add back the features.
