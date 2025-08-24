const { MongoClient } = require('mongodb');
require('dotenv').config();

// Use the same MongoDB connection as the bot and website
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/otp_bot';
const MONGODB_DATABASE = process.env.MONGODB_DATABASE || 'otp_bot';
const MONGODB_COLLECTION = process.env.MONGODB_COLLECTION || 'users';

async function connectToBotDatabase() {
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
    console.log('✅ Connected to bot MongoDB successfully');
    return { client, db };
  } catch (error) {
    console.error('❌ Bot MongoDB connection error:', error);
    throw error;
  }
}

async function getBotStats() {
  let client;
  try {
    const { client: mongoClient, db } = await connectToBotDatabase();
    client = mongoClient;
    
    const usersCollection = db.collection(MONGODB_COLLECTION);
    
    // Get total users count
    const totalUsers = await usersCollection.countDocuments();
    
    // Get today's new users (users created today)
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todaysUsers = await usersCollection.countDocuments({
      created_at: { $gte: today }
    });
    
    // Get users with balance > 0
    const usersWithBalance = await usersCollection.countDocuments({
      balance: { $gt: 0 }
    });
    
    // Get total balance across all users
    const balanceResult = await usersCollection.aggregate([
      {
        $group: {
          _id: null,
          totalBalance: { $sum: "$balance" }
        }
      }
    ]).toArray();
    
    const totalBalance = balanceResult.length > 0 ? balanceResult[0].totalBalance : 0;
    
    // Get recent transactions count (last 24 hours)
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const recentTransactions = await usersCollection.aggregate([
      {
        $unwind: "$transaction_history"
      },
      {
        $match: {
          "transaction_history.created_at": { $gte: yesterday }
        }
      },
      {
        $count: "count"
      }
    ]).toArray();
    
    const todaysTransactions = recentTransactions.length > 0 ? recentTransactions[0].count : 0;
    
    // Get total transactions
    const totalTransactionsResult = await usersCollection.aggregate([
      {
        $group: {
          _id: null,
          totalTransactions: { $sum: { $size: "$transaction_history" } }
        }
      }
    ]).toArray();
    
    const totalTransactions = totalTransactionsResult.length > 0 ? totalTransactionsResult[0].totalTransactions : 0;
    
    // Get banned users count
    const bannedUsers = await usersCollection.countDocuments({
      banned: true
    });
    
    // Get active users (users who have used the bot in last 7 days)
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const activeUsers = await usersCollection.countDocuments({
      updated_at: { $gte: weekAgo }
    });
    
    return {
      totalUsers,
      todaysUsers,
      usersWithBalance,
      totalBalance: parseFloat(totalBalance.toFixed(2)),
      todaysTransactions,
      totalTransactions,
      bannedUsers,
      activeUsers,
      success: true
    };
    
  } catch (error) {
    console.error('❌ Error getting bot stats:', error);
    return {
      success: false,
      error: error.message,
      totalUsers: 0,
      todaysUsers: 0,
      usersWithBalance: 0,
      totalBalance: 0,
      todaysTransactions: 0,
      totalTransactions: 0,
      bannedUsers: 0,
      activeUsers: 0
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
    const stats = await getBotStats();
    res.status(200).json(stats);
  } catch (error) {
    console.error('❌ API Error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
};
