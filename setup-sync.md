# Bot and Website Synchronization Setup Guide

## Overview

This guide will help you set up proper synchronization between your Telegram bot and web application using a shared MongoDB database.

## Issues Fixed

1. **Different MongoDB URIs**: Bot and website now use the same MongoDB connection
2. **Inconsistent Database Names**: Both use `otp_bot` database
3. **Separate Connections**: Now share the same database connection pool
4. **Missing Environment Variables**: Centralized configuration
5. **Data Structure Mismatches**: Consistent data schemas

## Setup Steps

### 1. Environment Configuration

Create a `.env` file in the **website** directory:

```env
# Website Configuration
PORT=3000
HOST=localhost
NODE_ENV=development

# MongoDB Configuration (Same as Bot)
MONGODB_URI=mongodb://localhost:27017/otp_bot
MONGODB_DATABASE=otp_bot
MONGODB_COLLECTION=users

# Database Connection Settings (Same as Bot)
DB_MAX_POOL_SIZE=10
DB_MIN_POOL_SIZE=1
DB_MAX_IDLE_TIME_MS=30000
DB_CONNECT_TIMEOUT_MS=10000
DB_SOCKET_TIMEOUT_MS=10000

# Session Configuration
SESSION_SECRET=your_session_secret_here_change_this_in_production

# App Configuration
APP_URL=http://localhost:3000

# Bot Configuration (for webhook integration)
BOT_TOKEN=your_telegram_bot_token_here
BACKEND_URL=http://localhost:3000

# Support Configuration
SUPPORT_USERNAME=@support
ADMIN_USER_ID=your_admin_user_id

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
```

### 2. Bot Environment

Ensure your **Bot** `.env` file has the same MongoDB settings:

```env
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# MongoDB Configuration (Same as Website)
MONGODB_URI=mongodb://localhost:27017/otp_bot
MONGODB_DATABASE=otp_bot
MONGODB_COLLECTION=users

# Database Connection Settings (Same as Website)
DB_MAX_POOL_SIZE=10
DB_MIN_POOL_SIZE=1
DB_MAX_IDLE_TIME_MS=30000
DB_CONNECT_TIMEOUT_MS=10000
DB_SOCKET_TIMEOUT_MS=10000

# Support Configuration
SUPPORT_USERNAME=@support
ADMIN_USER_ID=your_admin_user_id

# Backend URL for Web App buttons
BACKEND_URL=http://localhost:3000

# Rate Limiting Settings
MAX_REQUESTS_PER_MINUTE=60
RATE_LIMIT_WINDOW=60

# Logging Settings
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Environment
NODE_ENV=development
DEBUG=false
```

### 3. Database Setup

Run the database setup script:

```bash
cd Bot
python setup_database.py
```

This will create the necessary collections and sample data.

### 4. Start Services

#### Start the Website:
```bash
cd website
npm install
npm run dev
```

#### Start the Bot:
```bash
cd Bot
python main.py
```

### 5. Test Synchronization

#### Check Sync Status:
In your bot, use the admin command:
```
/syncstatus
```

#### Force Sync:
If data is out of sync, use:
```
/sync
```

## New Admin Commands

The bot now includes these sync-related admin commands:

- `/sync` - Sync all data with website
- `/syncusers` - Sync only user data
- `/syncservices` - Sync only service data
- `/syncstatus` - Check sync status

## API Endpoints

### Bot Statistics
```
GET http://localhost:3000/api/bot-stats
```

### Sync Status
```
GET http://localhost:3000/api/sync-status
```

## Database Collections

### Shared Collections
- `users` - User data, balances, transaction history
- `services` - Available services and pricing
- `servers` - Server configurations and API settings

### Website-Specific Collections
- `website_users` - Synced user data for website display
- `settings` - Bot and website configuration
- `promocodes` - Promotional codes
- `flags` - Country flags for UI

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Ensure MongoDB is running: `mongod`
   - Check connection string in both `.env` files
   - Verify network connectivity

2. **Sync Issues**
   - Run `/syncstatus` in bot to check status
   - Use `/sync` command to force synchronization
   - Check database permissions

3. **Port Conflicts**
   - Change PORT in website `.env` if 3000 is in use
   - Kill existing process: `lsof -ti:3000 | xargs kill`

4. **Environment Variables**
   - Ensure both bot and website have the same MongoDB settings
   - Check for typos in variable names
   - Restart services after changing `.env` files

### Verification Steps

1. **Check Database Connection**
   ```bash
   # Connect to MongoDB
   mongosh
   use otp_bot
   show collections
   ```

2. **Test API Endpoints**
   ```bash
   curl http://localhost:3000/api/bot-stats
   curl http://localhost:3000/api/sync-status
   ```

3. **Check Bot Commands**
   - Send `/admin` to see available commands
   - Use `/syncstatus` to check sync status

## Data Flow

1. **Bot Operations** → Updates `users`, `services`, `servers` collections
2. **Website Dashboard** → Reads from same collections for real-time data
3. **Manual Sync** → Copies data to website-specific collections if needed
4. **API Endpoints** → Provide real-time statistics and sync status

## Security Notes

- Change default session secrets in production
- Use strong MongoDB passwords
- Enable authentication for MongoDB in production
- Use HTTPS in production environment

## Next Steps

1. Test all admin commands in the bot
2. Verify website dashboard shows real-time data
3. Test API endpoints
4. Monitor sync status regularly
5. Set up automated sync if needed

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify environment variables match
3. Test database connectivity
4. Review logs for error messages
5. Use sync commands to force data alignment
