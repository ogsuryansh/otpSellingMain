# Telegram OTP Bot - Local Development Setup

This is a Telegram bot application for OTP (One-Time Password) services. This guide will help you set it up for local development.

## Prerequisites

- Node.js (v14 or higher)
- MySQL database
- Telegram Bot Token (from @BotFather)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Database Setup

1. Create a MySQL database:
```sql
CREATE DATABASE otp_bot_local;
```

2. Update database credentials in `config.local.js`:
```javascript
database: {
  host: 'localhost',
  port: 3306,
  name: 'otp_bot_local',
  user: 'your_username',
  password: 'your_password',
}
```

### 3. Telegram Bot Setup

1. Create a new bot with [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Update the token in `config.local.js`:
```javascript
telegram: {
  botToken: 'your_actual_bot_token_here',
  // ... other settings
}
```

### 4. Run the Application

#### Option 1: Simple Development Server
```bash
npm run dev
```

#### Option 2: Development with Debug
```bash
npm run dev:debug
```

#### Option 3: Development with Auto-restart (requires nodemon)
```bash
npm install -g nodemon
npm run dev:nodemon
```

### 5. Access the Application

- Web Interface: http://localhost:3000
- Bot Webhook: http://localhost:3000/bot

## Configuration

The application uses `config.local.js` for local development settings. Key configurations:

- **Port**: Default 3000
- **Database**: MySQL connection settings
- **Telegram Bot**: Token and webhook settings
- **Development Mode**: Polling instead of webhook for local development

## Environment Variables

You can override settings using environment variables:

```bash
export PORT=3001
export DB_HOST=localhost
export TELEGRAM_BOT_TOKEN=your_token
npm run dev
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL is running
   - Check database credentials in `config.local.js`
   - Verify database exists

2. **Telegram Bot Not Responding**
   - Verify bot token is correct
   - Check if bot is enabled
   - For local development, use polling mode (webhook disabled)

3. **Port Already in Use**
   - Change port in `config.local.js`
   - Or kill process using the port

### Memory Issues

If you encounter memory allocation errors:
- Increase Node.js memory limit: `node --max-old-space-size=4096 dev-server.js`
- Or use the debug script: `npm run dev:debug`

## Production vs Development

- **Development**: Uses polling for Telegram bot updates
- **Production**: Uses webhook for better performance
- **Local**: Runs on localhost:3000
- **Production**: Configured for external domain

## File Structure

```
├── server.js          # Main application (bundled)
├── dev-server.js      # Development wrapper
├── config.local.js    # Local configuration
├── package.json       # Dependencies and scripts
├── views/            # EJS templates
├── public/           # Static assets
└── README.md         # This file
```

## Support

For issues and questions:
- Email: mirzaglitch@gmail.com
- Telegram: @mirzaGlitch
