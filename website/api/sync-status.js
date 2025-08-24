const { MongoClient } = require('mongodb');
require('dotenv').config();

// Use the same MongoDB connection as the bot and website
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/otp_bot';
const MONGODB_DATABASE = process.env.MONGODB_DATABASE || 'otp_bot';
const MONGODB_COLLECTION = process.env.MONGODB_COLLECTION || 'users';

async function connectToDatabase() {
  try {
    const client = new MongoClient(MONGODB_URI, {
      maxPoolSize: parseInt(process.env.DB_MAX_POOL_SIZE) || 10,
      minPoolSize: parseInt(process.env.DB_MIN_POOL_SIZE) || 1,
      maxIdleTimeMS: parseInt(process.env.DB_MAX_IDLE_TIME_MS) || 30000,
      serverSelectionTimeoutMS: 5000,
      connectTimeoutMS: parseInt(process.env.DB_CONNECT_TIMEOUT_MS) || 10000,
      socketTimeoutMS: parseInt(process.env.DB_SOCKET_TIMEOUT_MS) || 10000
    });
    await client.connect();
    const db = client.db(MONGODB_DATABASE);
    console.log('✅ Connected to MongoDB successfully');
    return { client, db };
  } catch (error) {
    console.error('❌ MongoDB connection error:', error);
    throw error;
  }
}

async function getSyncStatus() {
  let client;
  try {
    const { client: mongoClient, db } = await connectToDatabase();
    client = mongoClient;
    
    // Get counts from bot collections
    const botUsersCollection = db.collection(MONGODB_COLLECTION);
    const botServicesCollection = db.collection('services');
    const botServersCollection = db.collection('servers');
    
    // Get counts from website collections
    const websiteUsersCollection = db.collection('website_users');
    const websiteServicesCollection = db.collection('services');
    const websiteServersCollection = db.collection('servers');
    
    // Count documents in each collection
    const [
      botUsersCount,
      botServicesCount,
      botServersCount,
      websiteUsersCount,
      websiteServicesCount,
      websiteServersCount
    ] = await Promise.all([
      botUsersCollection.countDocuments(),
      botServicesCollection.countDocuments(),
      botServersCollection.countDocuments(),
      websiteUsersCollection.countDocuments(),
      websiteServicesCollection.countDocuments(),
      websiteServersCollection.countDocuments()
    ]);
    
    // Calculate sync status
    const usersSynced = botUsersCount === websiteUsersCount;
    const servicesSynced = botServicesCount === websiteServicesCount;
    const serversSynced = botServersCount === websiteServersCount;
    
    // Get last sync timestamps
    const lastUserSync = await websiteUsersCollection.findOne(
      {}, 
      { sort: { last_sync: -1 }, projection: { last_sync: 1 } }
    );
    
    const lastServiceSync = await websiteServicesCollection.findOne(
      {}, 
      { sort: { last_sync: -1 }, projection: { last_sync: 1 } }
    );
    
    const lastServerSync = await websiteServersCollection.findOne(
      {}, 
      { sort: { last_sync: -1 }, projection: { last_sync: 1 } }
    );
    
    return {
      success: true,
      data: {
        users: {
          bot: botUsersCount,
          website: websiteUsersCount,
          synced: usersSynced,
          last_sync: lastUserSync?.last_sync || null
        },
        services: {
          bot: botServicesCount,
          website: websiteServicesCount,
          synced: servicesSynced,
          last_sync: lastServiceSync?.last_sync || null
        },
        servers: {
          bot: botServersCount,
          website: websiteServersCount,
          synced: serversSynced,
          last_sync: lastServerSync?.last_sync || null
        },
        overall_sync: usersSynced && servicesSynced && serversSynced,
        timestamp: new Date()
      }
    };
    
  } catch (error) {
    console.error('❌ Error getting sync status:', error);
    return {
      success: false,
      error: error.message,
      data: null
    };
  } finally {
    if (client) {
      await client.close();
    }
  }
}

module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const result = await getSyncStatus();
    
    if (result.success) {
      res.status(200).json(result);
    } else {
      res.status(500).json(result);
    }
  } catch (error) {
    console.error('❌ API Error:', error);
    res.status(500).json({ 
      success: false,
      error: 'Internal server error',
      message: error.message 
    });
  }
};
