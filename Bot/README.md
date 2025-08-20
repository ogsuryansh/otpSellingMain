# Telegram OTP Bot

A modular Telegram bot built with Python for OTP (One-Time Password) services.

## Features

- 👋 Welcome message with user stats
- 💰 Balance management
- 📦 Service selection
- 💳 Payment integration
- 🎫 Promocode system
- 👤 User profile
- 🆘 Support system
- 📋 Transaction history

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` file with your configuration:

```env
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/otp_bot
MONGODB_DATABASE=otp_bot

# Support Configuration
SUPPORT_USERNAME=@support
ADMIN_USER_ID=your_admin_user_id

# Environment
NODE_ENV=development
DEBUG=false
```

### 3. Get Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy your bot token and add it to `.env`

### 4. Database Setup

Make sure MongoDB is running and accessible with the URI specified in your `.env` file.

### 5. Run the Bot

```bash
python main.py
```

## Project Structure

```
Bot/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables example
├── README.md              # This file
└── src/
    ├── config/
    │   └── bot_config.py  # Bot configuration
    ├── database/
    │   └── user_db.py     # Database operations
    ├── handlers/
    │   ├── start_handler.py    # /start command handler
    │   └── callback_handler.py # Button callback handler
    └── utils/
        └── keyboard_utils.py   # Keyboard utilities
```

## Usage

### Commands

- `/start` - Show welcome message and main menu

### Buttons

- **Services** - View available OTP services
- **Balance** - Check current balance
- **Recharge** - Add funds to account
- **Use Promocode** - Apply promocode for bonus
- **Profile** - View user profile
- **Support** - Contact support
- **History** - View transaction history

## Development

The bot is built with a modular architecture:

- **Handlers**: Handle different types of interactions
- **Database**: MongoDB integration for user data
- **Utils**: Reusable utility functions
- **Config**: Centralized configuration management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
