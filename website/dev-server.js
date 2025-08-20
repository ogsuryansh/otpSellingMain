// Development Server Wrapper
require('dotenv').config();

// Load local configuration
const config = require('./config.local');

// Set environment variables for the main server
process.env.PORT = config.port;
process.env.HOST = config.host;
process.env.NODE_ENV = 'development';

// Database environment variables
process.env.DB_HOST = config.database.host;
process.env.DB_PORT = config.database.port;
process.env.DB_NAME = config.database.name;
process.env.DB_USER = config.database.user;
process.env.DB_PASSWORD = config.database.password;

// Telegram bot environment variables
process.env.TELEGRAM_BOT_TOKEN = config.telegram.botToken;
process.env.TELEGRAM_WEBHOOK_URL = config.telegram.webhookUrl;
process.env.USE_WEBHOOK = config.telegram.useWebhook.toString();

// App environment variables
process.env.APP_URL = config.app.url;
process.env.SESSION_SECRET = config.app.sessionSecret;

console.log('🚀 Starting development server...');
console.log(`📍 Server will run on: http://${config.host}:${config.port}`);
console.log(`🔧 Environment: ${process.env.NODE_ENV}`);
console.log(`🤖 Telegram Bot: ${config.telegram.useWebhook ? 'Webhook Mode' : 'Polling Mode'}`);

// Start the main server
require('./server.js');
