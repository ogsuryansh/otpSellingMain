# OTP Bot Website

A web dashboard for managing the Telegram OTP Bot with real-time data synchronization.

## Features

- 📊 Real-time dashboard with bot statistics
- 👥 User management and monitoring
- 🔧 Service and server management
- 🔗 API integration management
- 💰 Payment and balance tracking
- 🔄 Automatic data synchronization with bot

## Setup Instructions

### Prerequisites

- Node.js 16+ 
- MongoDB (local or Atlas)
- Python 3.12+ (for bot)

### Environment Configuration

Create a `.env` file in the website directory:

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

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. For production:
```bash
npm start
```

## Data Synchronization

The website and bot share the same MongoDB database to ensure data consistency. The synchronization system includes:

### Automatic Sync
- Real-time data updates between bot and website
- Shared user data, services, and server information
- Consistent balance and transaction tracking

### Manual Sync Commands (Bot Admin)
- `/sync` - Sync all data with website
- `/syncusers` - Sync only user data
- `/syncservices` - Sync only service data
- `/syncstatus` - Check sync status

### API Endpoints

#### Bot Statistics
```
GET /api/bot-stats
```
Returns real-time bot statistics including user counts, balances, and transaction data.

#### Sync Status
```
GET /api/sync-status
```
Returns synchronization status between bot and website databases.

## Database Collections

### Bot Collections
- `users` - User data, balances, transaction history
- `services` - Available services and pricing
- `servers` - Server configurations and API settings

### Website Collections
- `website_users` - Synced user data for website display
- `services` - Service data for website management
- `servers` - Server data for website management
- `settings` - Bot and website configuration
- `promocodes` - Promotional codes
- `flags` - Country flags for UI

## Development

### Project Structure
```
website/
├── api/                 # API endpoints
├── config/             # Configuration files
├── middleware/         # Express middleware
├── views/             # EJS templates
├── public/            # Static assets
├── package.json       # Dependencies
└── server-optimized.js # Main server file
```

### Key Files
- `config/database.js` - Database connection and operations
- `api/bot-stats.js` - Bot statistics API
- `api/sync-status.js` - Sync status API
- `server-optimized.js` - Main Express server

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check if MongoDB is running
   - Verify connection string in `.env`
   - Ensure network connectivity

2. **Sync Issues**
   - Run `/syncstatus` in bot to check status
   - Use `/sync` command to force synchronization
   - Check database permissions

3. **Port Already in Use**
   - Change PORT in `.env`
   - Kill existing process: `lsof -ti:3000 | xargs kill`

### Logs
- Check console output for detailed error messages
- MongoDB connection logs show sync status
- API endpoints log request/response data

## Security

- Environment variables for sensitive data
- Input validation and sanitization
- Rate limiting on API endpoints
- CORS configuration for cross-origin requests

## Support

For issues and questions:
- Check the troubleshooting section
- Review MongoDB connection settings
- Verify environment variables
- Test sync commands in bot

## License

This project is part of the OTP Bot system.
