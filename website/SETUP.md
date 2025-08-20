# Quick Setup Guide

## 🚀 Get Running in 5 Minutes

### 1. Prerequisites Check
- ✅ Node.js installed (v14+)
- ✅ MySQL installed and running
- ✅ Git (to clone/download the project)

### 2. Install Dependencies
```bash
npm install
```

### 3. Database Setup
1. Open MySQL command line or phpMyAdmin
2. Run the setup script:
```bash
mysql -u root -p < setup-database.sql
```
3. Update database credentials in `config.local.js` if needed

### 4. Telegram Bot Setup
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy your bot token
4. Update `config.local.js`:
```javascript
telegram: {
  botToken: 'YOUR_ACTUAL_BOT_TOKEN_HERE',
  // ... rest stays the same
}
```

### 5. Start the Server

#### Windows Users:
Double-click `start-dev.bat` or run:
```powershell
.\start-dev.ps1
```

#### Mac/Linux Users:
```bash
npm run dev
```

### 6. Test the Application
- Open browser: http://localhost:3000
- Message your bot on Telegram
- Check console for any errors

## 🔧 Troubleshooting

### "Port 3000 already in use"
Change port in `config.local.js`:
```javascript
port: 3001, // or any available port
```

### "Database connection failed"
1. Ensure MySQL is running
2. Check credentials in `config.local.js`
3. Verify database exists: `SHOW DATABASES;`

### "Bot not responding"
1. Verify bot token is correct
2. Check if bot is enabled in Telegram
3. Look for errors in console output

### Memory Issues
Run with increased memory:
```bash
node --max-old-space-size=4096 dev-server.js
```

## 📁 Key Files
- `dev-server.js` - Development server wrapper
- `config.local.js` - Local configuration
- `setup-database.sql` - Database setup script
- `start-dev.bat` - Windows startup script
- `start-dev.ps1` - PowerShell startup script

## 🆘 Need Help?
- Check the full README.md for detailed instructions
- Look at console output for error messages
- Contact: mirzaglitch@gmail.com or @mirzaGlitch on Telegram
