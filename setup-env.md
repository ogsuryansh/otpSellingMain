# Environment Setup Guide

## Current Status
Your bot is currently using MongoDB Atlas (cloud database) as shown in the terminal output:
```
MONGODB_URI=mongodb+srv://vishalgiri0044:kR9oUspxQUtYdund@cluster0.zdudgbg.mongodb.net/otp_bot?retryWrites=true&w=majority&appName=Cluster0
```

## Environment Files Created

I've created two environment files for you:

### 1. Bot Environment (`Bot/env.bot`)
- Contains the same MongoDB Atlas URI your bot is currently using
- Includes all necessary configuration for bot operation
- **Action Required**: Rename `env.bot` to `.env` in the Bot directory

### 2. Website Environment (`website/env.website`)
- Uses the same MongoDB Atlas URI for synchronization
- Includes all necessary configuration for website operation
- **Action Required**: Rename `env.website` to `.env` in the website directory

## Setup Steps

### Step 1: Configure Bot Environment
```bash
cd Bot
# Rename the environment file
mv env.bot .env

# Edit the .env file to add your actual values
# Replace these placeholders:
# - your_telegram_bot_token_here (with your actual bot token)
# - your_admin_user_id (with your Telegram user ID)
```

### Step 2: Configure Website Environment
```bash
cd website
# Rename the environment file
mv env.website .env

# Edit the .env file to add your actual values
# Replace these placeholders:
# - your_telegram_bot_token_here (with your actual bot token)
# - your_admin_user_id (with your Telegram user ID)
# - your_session_secret_here_change_this_in_production (with a random secret)
```

### Step 3: Verify Configuration

#### Check Bot Environment:
```bash
cd Bot
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('MONGODB_URI:', os.getenv('MONGODB_URI'))
print('MONGODB_DATABASE:', os.getenv('MONGODB_DATABASE'))
print('BOT_TOKEN:', 'SET' if os.getenv('BOT_TOKEN') else 'NOT SET')
print('ADMIN_USER_ID:', os.getenv('ADMIN_USER_ID'))
"
```

#### Check Website Environment:
```bash
cd website
node -e "
require('dotenv').config()
console.log('MONGODB_URI:', process.env.MONGODB_URI)
console.log('MONGODB_DATABASE:', process.env.MONGODB_DATABASE)
console.log('PORT:', process.env.PORT)
console.log('BOT_TOKEN:', process.env.BOT_TOKEN ? 'SET' : 'NOT SET')
"
```

## Important Notes

### MongoDB Atlas Configuration
- Both bot and website are configured to use the same MongoDB Atlas database
- This ensures perfect synchronization between bot and website
- No need to run local MongoDB - everything is in the cloud

### Security Considerations
1. **Bot Token**: Make sure to add your actual Telegram bot token
2. **Admin User ID**: Add your Telegram user ID to access admin commands
3. **Session Secret**: Generate a random string for website sessions
4. **Database Access**: The MongoDB Atlas credentials are already configured

### Required Values to Set

#### In Bot/.env:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz  # Your actual bot token
ADMIN_USER_ID=123456789  # Your Telegram user ID
```

#### In website/.env:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz  # Your actual bot token
ADMIN_USER_ID=123456789  # Your Telegram user ID
SESSION_SECRET=your_random_secret_string_here  # Random string for sessions
```

## Testing the Setup

### 1. Test Bot Connection:
```bash
cd Bot
python setup_database.py
```

### 2. Test Website Connection:
```bash
cd website
npm install
npm run dev
```

### 3. Test Sync Commands:
Once both are running, in your bot:
```
/admin  # Check admin panel
/syncstatus  # Check sync status
/sync  # Force sync
```

## Troubleshooting

### Common Issues:

1. **Environment File Not Found**
   - Make sure you renamed `env.bot` to `.env` in Bot directory
   - Make sure you renamed `env.website` to `.env` in website directory

2. **MongoDB Connection Failed**
   - The Atlas URI is already configured correctly
   - Check your internet connection
   - Verify the database exists in Atlas

3. **Bot Token Issues**
   - Get your bot token from @BotFather on Telegram
   - Make sure it's in the correct format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

4. **Admin Access Issues**
   - Get your user ID by sending a message to @userinfobot on Telegram
   - Add it to both environment files

## Next Steps

After setting up the environment files:

1. **Start the Bot**:
   ```bash
   cd Bot
   python main.py
   ```

2. **Start the Website**:
   ```bash
   cd website
   npm run dev
   ```

3. **Test Synchronization**:
   - Use `/syncstatus` in bot to check sync status
   - Use `/sync` to force synchronization
   - Check website dashboard for real-time data

The synchronization system is now properly configured to work with your MongoDB Atlas database!
