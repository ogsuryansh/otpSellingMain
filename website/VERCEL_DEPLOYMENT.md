# Vercel Deployment Guide

This guide will help you deploy your Telegram OTP Bot application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **MongoDB Database**: Set up a MongoDB database (MongoDB Atlas recommended)
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Environment Variables Setup

Before deploying, you need to set up the following environment variables in your Vercel project:

### Required Environment Variables

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/otp_bot
MONGODB_DATABASE=otp_bot

# Application Settings
NODE_ENV=production
APP_URL=https://your-app.vercel.app
SESSION_SECRET=your_session_secret_here

# Default Dashboard Values
DEFAULT_TODAYS_EARNINGS=₹0
DEFAULT_TOTAL_EARNINGS=₹0
DEFAULT_TODAYS_USERS=0
DEFAULT_TOTAL_USERS=0
DEFAULT_TODAYS_SOLD=0
DEFAULT_TOTAL_SOLD=0
```

### Optional Environment Variables

```bash
# Telegram Bot Configuration (if you're using Telegram features)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-app.vercel.app/bot
USE_WEBHOOK=false
```

## Deployment Steps

### 1. Connect Your Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your Git repository
4. Select the repository containing this code

### 2. Configure Project Settings

1. **Framework Preset**: Select "Node.js"
2. **Root Directory**: Leave as default (if your code is in the root)
3. **Build Command**: Leave as default (Vercel will auto-detect)
4. **Output Directory**: Leave as default
5. **Install Command**: `npm install`

### 3. Set Environment Variables

1. In the Vercel dashboard, go to your project settings
2. Navigate to "Environment Variables"
3. Add each environment variable from the list above
4. Make sure to set them for "Production" environment

### 4. Deploy

1. Click "Deploy"
2. Vercel will automatically build and deploy your application
3. Wait for the deployment to complete

## Post-Deployment

### 1. Verify Deployment

- Visit your deployed URL (e.g., `https://your-app.vercel.app`)
- Check the health endpoint: `https://your-app.vercel.app/api/health`
- Test the main dashboard: `https://your-app.vercel.app/admin-dashboard`

### 2. Database Setup

Make sure your MongoDB database is properly configured and accessible from Vercel's servers.

### 3. Custom Domain (Optional)

1. In your Vercel project settings, go to "Domains"
2. Add your custom domain
3. Update your `APP_URL` environment variable to match

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify your `MONGODB_URI` is correct
   - Ensure your MongoDB cluster allows connections from all IPs (0.0.0.0/0)
   - Check if your MongoDB user has the correct permissions

2. **Build Failures**
   - Check the build logs in Vercel dashboard
   - Ensure all dependencies are in `package.json`
   - Verify Node.js version compatibility

3. **Environment Variables Not Working**
   - Make sure environment variables are set for the correct environment (Production)
   - Redeploy after adding new environment variables
   - Check variable names for typos

### Debugging

- Use the `/api/health` endpoint to check if the server is running
- Check Vercel function logs in the dashboard
- Monitor MongoDB connection logs

## File Structure for Vercel

The following files are essential for Vercel deployment:

```
├── vercel.json          # Vercel configuration
├── vercel-server.js     # Vercel-optimized server
├── package.json         # Dependencies and scripts
├── config/
│   └── database.js      # Database configuration
├── views/               # EJS templates
├── public/              # Static assets
└── README.md           # Project documentation
```

## Performance Optimization

1. **Database Connection**: The app uses connection pooling for better performance
2. **Static Assets**: CSS and other static files are served efficiently
3. **Caching**: Consider implementing caching for frequently accessed data
4. **CDN**: Vercel automatically provides CDN for static assets

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to your repository
2. **MongoDB Security**: Use strong passwords and restrict network access
3. **Session Security**: Use a strong session secret
4. **HTTPS**: Vercel automatically provides SSL certificates

## Support

If you encounter issues:

1. Check the Vercel deployment logs
2. Verify all environment variables are set correctly
3. Test the application locally first
4. Check MongoDB connection and permissions
