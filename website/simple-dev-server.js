// Development Server Wrapper with MongoDB Support
require('dotenv').config();

// Load local configuration
const config = require('./config.local');

// Set environment variables for the server
process.env.PORT = config.port;
process.env.HOST = config.host;
process.env.NODE_ENV = 'development';

// App environment variables
process.env.APP_URL = config.app.url;
process.env.SESSION_SECRET = config.app.sessionSecret;

// MongoDB environment variables
process.env.MONGODB_URI = config.mongodb.uri;
process.env.MONGODB_DATABASE = config.mongodb.database;
process.env.MONGODB_COLLECTION = config.mongodb.collection;

console.log('🚀 Starting development server with MongoDB...');
console.log(`📍 Server will run on: http://${config.host}:${config.port}`);
console.log(`🔧 Environment: ${process.env.NODE_ENV}`);
console.log(`💾 Database: MongoDB (${config.mongodb.database})`);

// Start the server
require('./simple-server.js');
