const { MongoClient } = require('mongodb');
require('dotenv').config();

class Database {
  constructor() {
    this.client = null;
    this.db = null;
    this.uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/otp_bot';
    this.dbName = process.env.MONGODB_DATABASE || 'otp_bot';
  }

  async connect() {
    try {
      this.client = new MongoClient(this.uri);
      await this.client.connect();
      this.db = this.client.db(this.dbName);
      console.log('✅ Connected to MongoDB successfully');
      return this.db;
    } catch (error) {
      console.error('❌ MongoDB connection error:', error);
      throw error;
    }
  }

  async disconnect() {
    if (this.client) {
      await this.client.close();
      console.log('🔌 Disconnected from MongoDB');
    }
  }

  getCollection(collectionName) {
    if (!this.db) {
      throw new Error('Database not connected. Call connect() first.');
    }
    console.log(`📋 [DEBUG] Getting collection: ${collectionName} from database: ${this.dbName}`);
    return this.db.collection(collectionName);
  }

  // Dashboard data methods - Get real data from bot's MongoDB
  async getDashboardData() {
    try {
      console.log('🔍 [DEBUG] Starting getDashboardData() method - Fetching from bot database');
      
      // Connect to bot's MongoDB to get real data
      const botStats = await this.getBotStats();
      
      console.log('✅ [DEBUG] Bot stats retrieved:', botStats);
      
      // Get additional data from website database
      const servicesCollection = this.getCollection('services');
      const serversCollection = this.getCollection('servers');
      
      // Get real top services from database
      console.log('🔍 [DEBUG] Querying top services from services collection...');
      const topServices = await servicesCollection
        .find({})
        .sort({ users: -1 })
        .limit(3)
        .toArray();
      
      console.log('📈 [DEBUG] Top services found:', topServices.length);
      
      // Get server count
      console.log('🔍 [DEBUG] Counting servers...');
      const serverCount = await serversCollection.countDocuments();
      console.log('🖥️  [DEBUG] Total servers found:', serverCount);
      
      // Get service count
      console.log('🔍 [DEBUG] Counting services...');
      const serviceCount = await servicesCollection.countDocuments();
      console.log('📦 [DEBUG] Total services found:', serviceCount);
      
      // Use bot data for dashboard
      const stats = {
        todaysEarnings: `₹${botStats.totalBalance.toFixed(2)}`,
        totalEarnings: `₹${botStats.totalBalance.toFixed(2)}`,
        todaysUsers: botStats.todaysUsers,
        totalUsers: botStats.totalUsers,
        todaysSold: botStats.todaysNumbersSold, // Use actual number purchases
        totalSold: botStats.totalNumbersSold,   // Use actual number purchases
        topServices: topServices,
        serverCount: serverCount,
        serviceCount: serviceCount,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      console.log('📊 [DEBUG] Dashboard stats prepared from bot data:', stats);
      
      return stats;
      
    } catch (error) {
      console.error('❌ [DEBUG] Error getting dashboard data from bot:', error);
      
      // Fallback to default values if bot data fails
      return {
        todaysEarnings: '₹0',
        totalEarnings: '₹0',
        todaysUsers: 0,
        totalUsers: 0,
        todaysSold: 0,
        totalSold: 0,
        topServices: [],
        serverCount: 0,
        serviceCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
      };
    }
  }
  
  // New method to get bot statistics
  async getBotStats() {
    try {
      console.log('🔍 [DEBUG] Connecting to bot MongoDB...');
      
      // Use the same MongoDB connection as the bot
      const botUri = process.env.MONGODB_URI || 'mongodb+srv://vishalgiri0044:kR9oUspxQUtYdund@cluster0.zdudgbg.mongodb.net/otp_bot?retryWrites=true&w=majority&appName=Cluster0';
      const botDbName = process.env.MONGODB_DATABASE || 'otp_bot';
      const botCollection = process.env.MONGODB_COLLECTION || 'users';
      
      const botClient = new MongoClient(botUri);
      await botClient.connect();
      const botDb = botClient.db(botDbName);
      const usersCollection = botDb.collection(botCollection);
      
      console.log('✅ [DEBUG] Connected to bot MongoDB successfully');
      
      // Get total users count
      const totalUsers = await usersCollection.countDocuments();
      
      // Get today's new users (users created today)
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const todaysUsers = await usersCollection.countDocuments({
        created_at: { $gte: today }
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
      
      // Get number purchases (transactions that are debits for number purchases)
      const numberPurchases = await usersCollection.aggregate([
        {
          $unwind: "$transaction_history"
        },
        {
          $match: {
            "transaction_history.type": "debit",
            "transaction_history.reason": { $regex: /number|purchase|bought/i }
          }
        },
        {
          $count: "count"
        }
      ]).toArray();
      
      const totalNumbersSold = numberPurchases.length > 0 ? numberPurchases[0].count : 0;
      
      // Get today's number purchases
      const todaysNumberPurchases = await usersCollection.aggregate([
        {
          $unwind: "$transaction_history"
        },
        {
          $match: {
            "transaction_history.type": "debit",
            "transaction_history.reason": { $regex: /number|purchase|bought/i },
            "transaction_history.created_at": { $gte: yesterday }
          }
        },
        {
          $count: "count"
        }
      ]).toArray();
      
      const todaysNumbersSold = todaysNumberPurchases.length > 0 ? todaysNumberPurchases[0].count : 0;
      
      await botClient.close();
      
      return {
        totalUsers,
        todaysUsers,
        totalBalance: parseFloat(totalBalance.toFixed(2)),
        todaysTransactions,
        totalTransactions,
        todaysNumbersSold,
        totalNumbersSold
      };
      
    } catch (error) {
      console.error('❌ [DEBUG] Error getting bot stats:', error);
      return {
        totalUsers: 0,
        todaysUsers: 0,
        totalBalance: 0,
        todaysTransactions: 0,
        totalTransactions: 0,
        todaysNumbersSold: 0,
        totalNumbersSold: 0
      };
    }
  }



  // Server methods
  async getServers() {
    try {
      const serversCollection = this.getCollection('servers');
      return await serversCollection.find({}).toArray();
    } catch (error) {
      console.error('Error getting servers:', error);
      throw error;
    }
  }

  async addServer(serverData) {
    try {
      const serversCollection = this.getCollection('servers');
      const result = await serversCollection.insertOne({
        ...serverData,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      return result;
    } catch (error) {
      console.error('Error adding server:', error);
      throw error;
    }
  }

  async updateServer(id, serverData) {
    try {
      const serversCollection = this.getCollection('servers');
      const result = await serversCollection.updateOne(
        { _id: id },
        { 
          $set: {
            ...serverData,
            updatedAt: new Date()
          }
        }
      );
      return result;
    } catch (error) {
      console.error('Error updating server:', error);
      throw error;
    }
  }

  async deleteServer(id) {
    try {
      const serversCollection = this.getCollection('servers');
      const result = await serversCollection.deleteOne({ _id: id });
      return result;
    } catch (error) {
      console.error('Error deleting server:', error);
      throw error;
    }
  }

  // Service methods
  async getServices() {
    try {
      const servicesCollection = this.getCollection('services');
      return await servicesCollection.find({}).toArray();
    } catch (error) {
      console.error('Error getting services:', error);
      throw error;
    }
  }

  async addService(serviceData) {
    try {
      const servicesCollection = this.getCollection('services');
      const result = await servicesCollection.insertOne({
        ...serviceData,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      return result;
    } catch (error) {
      console.error('Error adding service:', error);
      throw error;
    }
  }

  async updateService(id, serviceData) {
    try {
      const servicesCollection = this.getCollection('services');
      const result = await servicesCollection.updateOne(
        { _id: id },
        { 
          $set: {
            ...serviceData,
            updatedAt: new Date()
          }
        }
      );
      return result;
    } catch (error) {
      console.error('Error updating service:', error);
      throw error;
    }
  }

  async deleteService(id) {
    try {
      const servicesCollection = this.getCollection('services');
      const result = await servicesCollection.deleteOne({ _id: id });
      return result;
    } catch (error) {
      console.error('Error deleting service:', error);
      throw error;
    }
  }

  // API methods
  async getApis() {
    try {
      console.log('🔍 [DEBUG] getApis() called');
      const apisCollection = this.getCollection('apis');
      console.log('📋 [DEBUG] Collection name: apis');
      console.log('🔗 [DEBUG] Database connected:', !!this.db);
      
      const apis = await apisCollection.find({}).toArray();
      console.log('📊 [DEBUG] Found APIs:', apis.length);
      
      if (apis.length === 0) {
        console.log('⚠️ [DEBUG] No APIs found in collection');
      } else {
        apis.forEach((api, index) => {
          console.log(`   ${index + 1}. ${api.server_name} - ${api.api_url} - Status: ${api.status} - ID: ${api._id}`);
        });
      }
      
      return apis;
    } catch (error) {
      console.error('❌ [DEBUG] Error getting APIs:', error);
      throw error;
    }
  }

  async addApi(apiData) {
    try {
      console.log('💾 [DEBUG] addApi called with data:', apiData);
      const apisCollection = this.getCollection('apis');
      
      const apiToInsert = {
        ...apiData,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      console.log('📝 [DEBUG] Inserting API:', apiToInsert);
      const result = await apisCollection.insertOne(apiToInsert);
      console.log('✅ [DEBUG] API inserted successfully:', result);
      
      // Verify the API was saved by retrieving it
      const savedApi = await apisCollection.findOne({ _id: result.insertedId });
      console.log('🔍 [DEBUG] Verified saved API:', savedApi);
      
      // Check if the API is actually in the collection
      const allApis = await apisCollection.find({}).toArray();
      console.log('📊 [DEBUG] Total APIs in collection after insert:', allApis.length);
      allApis.forEach((api, index) => {
        console.log(`   ${index + 1}. ${api.server_name} - ${api.api_url} - ID: ${api._id}`);
      });
      
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error adding API:', error);
      throw error;
    }
  }

  async updateApi(id, apiData) {
    try {
      const apisCollection = this.getCollection('apis');
      const result = await apisCollection.updateOne(
        { _id: id },
        { 
          $set: {
            ...apiData,
            updatedAt: new Date()
          }
        }
      );
      return result;
    } catch (error) {
      console.error('Error updating API:', error);
      throw error;
    }
  }

  async deleteApi(id) {
    try {
      console.log('🗑️ [DEBUG] deleteApi called with id:', id);
      const apisCollection = this.getCollection('apis');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      console.log('🔍 [DEBUG] Searching for API with ObjectId:', objectId);
      const result = await apisCollection.deleteOne({ _id: objectId });
      
      console.log('✅ [DEBUG] Delete result:', result);
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error deleting API:', error);
      throw error;
    }
  }

  // Settings methods
  async getSettings() {
    try {
      const settingsCollection = this.getCollection('settings');
      let settings = await settingsCollection.findOne({ type: 'bot_settings' });
      
      if (!settings) {
        settings = {
          type: 'bot_settings',
          channel: process.env.DEFAULT_CHANNEL || '',
          supportUrl: process.env.DEFAULT_SUPPORT_URL || '',
          smmPanel: process.env.DEFAULT_SMM_PANEL === 'true' || false,
          smmUrl: process.env.DEFAULT_SMM_URL || '',
          smmProfit: parseInt(process.env.DEFAULT_SMM_PROFIT) || 0,
          manual: process.env.DEFAULT_MANUAL === 'true' || false,
          manualUpi: process.env.DEFAULT_MANUAL_UPI || '',
          manualQr: process.env.DEFAULT_MANUAL_QR || '',
          paytm: process.env.DEFAULT_PAYTM === 'true' || false,
          paytmMid: process.env.DEFAULT_PAYTM_MID || '',
          paytmUpi: process.env.DEFAULT_PAYTM_UPI || '',
          bharatpe: process.env.DEFAULT_BHARATPE === 'true' || false,
          bharatpeMid: process.env.DEFAULT_BHARATPE_MID || '',
          bharatpeMtoken: process.env.DEFAULT_BHARATPE_MTOKEN || '',
          bharatpeUpi: process.env.DEFAULT_BHARATPE_UPI || '',
          bharatpeQr: process.env.DEFAULT_BHARATPE_QR || '',
          crypto: process.env.DEFAULT_CRYPTO === 'true' || false,
          cryptoHash: process.env.DEFAULT_CRYPTO_HASH || '',
          upi: process.env.DEFAULT_UPI === 'true' || false,
          upiApi: process.env.DEFAULT_UPI_API || '',
          upiPostback: process.env.UPI_POSTBACK_URL || 'http://localhost:3001/webhook',
          upiIp: process.env.UPI_IP_ADDRESS || '127.0.0.1',
          createdAt: new Date(),
          updatedAt: new Date()
        };
        await settingsCollection.insertOne(settings);
      }
      
      return settings;
    } catch (error) {
      console.error('Error getting settings:', error);
      throw error;
    }
  }

  async updateSettings(settingsData) {
    try {
      const settingsCollection = this.getCollection('settings');
      const result = await settingsCollection.updateOne(
        { type: 'bot_settings' },
        { 
          $set: {
            ...settingsData,
            updatedAt: new Date()
          }
        },
        { upsert: true }
      );
      return result;
    } catch (error) {
      console.error('Error updating settings:', error);
      throw error;
    }
  }

  // Get all data for my-services page
  async getMyServicesData() {
    try {
      console.log('🔍 [DEBUG] getMyServicesData() called');
      
      const servers = await this.getServers();
      const services = await this.getServices();
      const apis = await this.getApis();
      
      console.log('📊 [DEBUG] Data counts:');
      console.log('   - Servers:', servers.length);
      console.log('   - Services:', services.length);
      console.log('   - APIs:', apis.length);
      
      // Convert MongoDB _id to id for template compatibility
      const processedServers = servers.map(server => ({
        ...server,
        id: server._id.toString()
      }));
      
      const processedServices = services.map(service => ({
        ...service,
        id: service._id.toString()
      }));
      
      const processedApis = apis.map(api => ({
        ...api,
        id: api._id.toString()
      }));
      
      console.log('✅ [DEBUG] Processed APIs:', processedApis.length);
      processedApis.forEach((api, index) => {
        console.log(`   ${index + 1}. ID: ${api.id} - ${api.server_name} - ${api.api_url}`);
      });
      
      const result = [
        {
          name: 'My Servers',
          type: 'servers',
          from: 'servers',
          data: processedServers,
          paginateButtons: [1],
          limit: 10,
          offset: 0,
          paginateLink: '/my-services?page=1&'
        },
        {
          name: 'My Services',
          type: 'services',
          from: 'services',
          data: processedServices,
          paginateButtons: [1],
          limit: 10,
          offset: 0,
          paginateLink: '/my-services?page=1&'
        },
        {
          name: 'My Connected APIs',
          type: 'apis',
          from: 'apis',
          data: processedApis,
          paginateButtons: [1],
          limit: 10,
          offset: 0,
          paginateLink: '/my-services?page=1&'
        }
      ];
      
      console.log('🎯 [DEBUG] Returning my-services data with sections:', result.length);
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error getting my services data:', error);
      throw error;
    }
  }

  // Clear dashboard stats (remove existing data)
  async clearDashboardStats() {
    try {
      console.log('🗑️ [DEBUG] Clearing dashboard stats from database...');
      const statsCollection = this.getCollection('stats');
      const result = await statsCollection.deleteOne({ type: 'dashboard' });
      
      if (result.deletedCount > 0) {
        console.log('✅ [DEBUG] Dashboard stats cleared successfully');
        return true;
      } else {
        console.log('⚠️ [DEBUG] No dashboard stats found to clear');
        return false;
      }
    } catch (error) {
      console.error('❌ [DEBUG] Error clearing dashboard stats:', error);
      throw error;
    }
  }

  // Update dashboard stats when data changes
  async updateDashboardStats() {
    try {
      const servicesCollection = this.getCollection('services');
      const serversCollection = this.getCollection('servers');
      const statsCollection = this.getCollection('stats');

      // Calculate real stats
      const totalServices = await servicesCollection.countDocuments();
      const totalServers = await serversCollection.countDocuments();
      
      // Calculate total users from services
      const services = await servicesCollection.find({}).toArray();
      const totalUsers = services.reduce((sum, service) => sum + (service.users || 0), 0);
      
      // Calculate total earnings (example calculation)
      const totalEarnings = services.reduce((sum, service) => {
        const price = parseFloat(service.price?.replace('₹', '') || 0);
        const users = service.users || 0;
        return sum + (price * users);
      }, 0);

      // Update stats
      await statsCollection.updateOne(
        { type: 'dashboard' },
        {
          $set: {
            todaysEarnings: process.env.DEFAULT_TODAYS_EARNINGS || '₹0', // Will be calculated based on today's transactions
            totalEarnings: `₹${totalEarnings.toFixed(2)}`,
            todaysUsers: parseInt(process.env.DEFAULT_TODAYS_USERS) || 0, // Will be calculated based on today's registrations
            totalUsers: totalUsers,
            todaysSold: parseInt(process.env.DEFAULT_TODAYS_SOLD) || 0, // Will be calculated based on today's sales
            totalSold: totalServices,
            updatedAt: new Date()
          }
        },
        { upsert: true }
      );

      return true;
    } catch (error) {
      console.error('Error updating dashboard stats:', error);
      throw error;
    }
  }

  // Flag methods
  async getFlags() {
    try {
      const flagsCollection = this.getCollection('flags');
      let flags = await flagsCollection.find({}).toArray();
      
      // If no flags exist, create default flags
      if (flags.length === 0) {
        const defaultFlags = [
          { country: 'India', flag: '🇮🇳', createdAt: new Date(), updatedAt: new Date() },
          { country: 'USA', flag: '🇺🇸', createdAt: new Date(), updatedAt: new Date() },
          { country: 'UK', flag: '🇬🇧', createdAt: new Date(), updatedAt: new Date() },
          { country: 'Canada', flag: '🇨🇦', createdAt: new Date(), updatedAt: new Date() },
          { country: 'Australia', flag: '🇦🇺', createdAt: new Date(), updatedAt: new Date() }
        ];
        
        await flagsCollection.insertMany(defaultFlags);
        flags = defaultFlags;
      }
      
      // Convert to object format for easy access
      const flagsObject = {};
      flags.forEach(flag => {
        flagsObject[flag.country] = flag.flag;
      });
      
      return flagsObject;
    } catch (error) {
      console.error('Error getting flags:', error);
      throw error;
    }
  }

  async addFlag(flagData) {
    try {
      const flagsCollection = this.getCollection('flags');
      const result = await flagsCollection.insertOne({
        ...flagData,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      return result;
    } catch (error) {
      console.error('Error adding flag:', error);
      throw error;
    }
  }

  async updateFlag(id, flagData) {
    try {
      const flagsCollection = this.getCollection('flags');
      const result = await flagsCollection.updateOne(
        { _id: id },
        { 
          $set: {
            ...flagData,
            updatedAt: new Date()
          }
        }
      );
      return result;
    } catch (error) {
      console.error('Error updating flag:', error);
      throw error;
    }
  }

  async deleteFlag(id) {
    try {
      const flagsCollection = this.getCollection('flags');
      const result = await flagsCollection.deleteOne({ _id: id });
      return result;
    } catch (error) {
      console.error('Error deleting flag:', error);
      throw error;
    }
  }

  // User methods
  async getUsers() {
    try {
      const usersCollection = this.getCollection('users');
      const users = await usersCollection.find({}).toArray();
      return users;
    } catch (error) {
      console.error('Error getting users:', error);
      throw error;
    }
  }

  async getUserById(userId) {
    try {
      const usersCollection = this.getCollection('users');
      const user = await usersCollection.findOne({ userId: userId });
      return user;
    } catch (error) {
      console.error('Error getting user by ID:', error);
      throw error;
    }
  }

  // Update flags method
  async updateFlags(flagsData) {
    try {
      const flagsCollection = this.getCollection('flags');
      
      // Clear existing flags
      await flagsCollection.deleteMany({});
      
      // Insert new flags
      const flagsArray = Object.entries(flagsData).map(([country, flag]) => ({
        country,
        flag,
        createdAt: new Date(),
        updatedAt: new Date()
      }));
      
      if (flagsArray.length > 0) {
        await flagsCollection.insertMany(flagsArray);
      }
      
      return { success: true, message: 'Flags updated successfully' };
    } catch (error) {
      console.error('Error updating flags:', error);
      throw error;
    }
  }
}

module.exports = new Database();
