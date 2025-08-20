# OTP Selling Bot & Website

A complete Telegram bot and web application for OTP selling services with admin panel and user management.

## 🚀 Features

### Bot Features
- **User Management**: Registration, profile management, balance tracking
- **Admin Panel**: Complete admin interface with user management
- **Services**: OTP services for various platforms
- **Payment System**: Balance management and recharge options
- **Promocode System**: Promotional code functionality
- **History Tracking**: Transaction and number history
- **Support System**: Direct support integration

### Website Features
- **Admin Dashboard**: Complete web-based admin interface
- **User Management**: User registration, profiles, and management
- **Service Management**: Add, edit, and manage OTP services
- **API Integration**: Connect external APIs for services
- **Payment Processing**: Manual and automated payment handling
- **Analytics**: User statistics and service analytics

## 📁 Project Structure

```
otpSellingMain/
├── Bot/                    # Telegram Bot (Python)
│   ├── src/
│   │   ├── config/         # Bot configuration
│   │   ├── database/       # Database operations
│   │   ├── handlers/       # Bot command handlers
│   │   └── utils/          # Utility functions
│   ├── main.py            # Bot entry point
│   ├── dev_bot.py         # Development bot with auto-restart
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables template
├── website/               # Web Application (Node.js)
│   ├── config/           # Website configuration
│   ├── views/            # EJS templates
│   ├── public/           # Static files
│   ├── server.js         # Main server file
│   ├── package.json      # Node.js dependencies
│   └── .env.example      # Environment variables template
└── README.md             # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 18+
- MongoDB Atlas account
- Telegram Bot Token

### Bot Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd otpSellingMain/Bot
   ```

2. **Install Python dependencies**
   ```bash
   py -3.12 -m pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Required environment variables for bot**
   ```env
   BOT_TOKEN=your_telegram_bot_token
   MONGODB_URI=your_mongodb_connection_string
   MONGODB_DATABASE=otp_bot
   MONGODB_COLLECTION=users
   SUPPORT_USERNAME=your_support_username
   ADMIN_USER_ID=your_telegram_user_id
   ```

5. **Run the bot**
   ```bash
   # Development mode with auto-restart
   py -3.12 dev_bot.py
   
   # Production mode
   py -3.12 main.py
   ```

### Website Setup

1. **Navigate to website directory**
   ```bash
   cd ../website
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Required environment variables for website**
   ```env
   PORT=3000
   MONGODB_URI=your_mongodb_connection_string
   SESSION_SECRET=your_session_secret
   BOT_TOKEN=your_telegram_bot_token
   ```

5. **Run the website**
   ```bash
   # Development mode
   npm run dev
   
   # Production mode
   npm start
   ```

## 🔧 Configuration

### Bot Configuration
- **Bot Token**: Get from @BotFather on Telegram
- **MongoDB**: Use MongoDB Atlas for cloud database
- **Admin ID**: Your Telegram user ID for admin access
- **Support Username**: Username for support contact

### Website Configuration
- **Port**: Default 3000, change as needed
- **Session Secret**: Random string for session security
- **Database**: Same MongoDB instance as bot
- **Bot Integration**: Same bot token for integration

## 📱 Bot Commands

### User Commands
- `/start` - Start the bot and show main menu
- `/admin` - Admin panel (admin only)

### Admin Commands
- `/add <user_id> <amount>` - Add balance to user
- `/cut <user_id> <amount>` - Cut balance from user
- `/trnx <user_id>` - View user transaction history
- `/nums <user_id>` - View user number history
- `/smm_history <user_id>` - View user SMM history
- `/ban <user_id>` - Ban user
- `/unban <user_id>` - Unban user
- `/broadcast <message>` - Broadcast message to all users

## 🌐 Website Features

### Admin Panel
- **Dashboard**: Overview of users and services
- **User Management**: View and manage all users
- **Service Management**: Add and manage OTP services
- **API Integration**: Connect external service APIs
- **Payment Management**: Handle manual payments
- **Analytics**: View usage statistics

### User Interface
- **Registration**: User account creation
- **Profile Management**: Update user information
- **Service Purchase**: Buy OTP services
- **Payment**: Recharge account balance
- **History**: View transaction and service history

## 🔒 Security Features

- **Environment Variables**: Sensitive data stored in .env files
- **Admin Authentication**: Telegram user ID verification
- **Session Management**: Secure session handling
- **Input Validation**: All user inputs validated
- **Error Handling**: Comprehensive error management

## 📊 Database Schema

### Users Collection
```javascript
{
  user_id: Number,
  username: String,
  first_name: String,
  balance: Number,
  total_purchased: Number,
  total_used: Number,
  created_at: Date,
  updated_at: Date
}
```

### Services Collection
```javascript
{
  service_id: String,
  name: String,
  price: Number,
  description: String,
  status: String,
  created_at: Date
}
```

## 🚀 Deployment

### Bot Deployment
1. **VPS/Server**: Deploy on any VPS with Python 3.12
2. **Docker**: Use Docker for containerized deployment
3. **Cloud Platforms**: Deploy on Heroku, Railway, or similar

### Website Deployment
1. **Vercel**: Easy deployment for Node.js apps
2. **Heroku**: Cloud platform deployment
3. **VPS**: Traditional server deployment
4. **Docker**: Containerized deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- **Telegram**: Contact @your_support_username
- **Email**: support@yourdomain.com
- **Issues**: Create an issue on GitHub

## 🔄 Updates

- **Auto-restart**: Bot automatically restarts on file changes (development)
- **Hot reload**: Website supports hot reloading (development)
- **Version control**: Git-based version control
- **Backup**: Regular database backups recommended

## 📈 Monitoring

- **Bot Status**: Monitor bot uptime and performance
- **Database**: Monitor MongoDB connection and performance
- **Website**: Monitor website uptime and user activity
- **Logs**: Comprehensive logging for debugging

---

**Note**: Make sure to keep your environment variables secure and never commit them to version control.
