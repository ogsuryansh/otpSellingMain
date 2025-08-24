const { MongoClient } = require('mongodb');
require('dotenv').config();

// Input validation utilities
const validateInput = {
  // Validate and sanitize string inputs
  string: (value, maxLength = 100) => {
    if (typeof value !== 'string') return null;
    if (value.length > maxLength) return null;
    // Remove potentially dangerous characters
    return value.replace(/[<>"'&]/g, '');
  },
  
  // Validate numeric inputs
  number: (value) => {
    const num = parseFloat(value);
    return isNaN(num) ? null : num;
  },
  
  // Validate ObjectId
  objectId: (value) => {
    if (!value || typeof value !== 'string') return null;
    if (!/^[0-9a-fA-F]{24}$/.test(value)) return null;
    return value;
  },
  
  // Validate email
  email: (value) => {
    if (!value || typeof value !== 'string') return null;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value) ? value : null;
  },
  
  // Validate URL
  url: (value) => {
    if (!value || typeof value !== 'string') return null;
    try {
      new URL(value);
      return value;
    } catch {
      return null;
    }
  }
};

class Database {
  constructor() {
    this.client = null;
    this.db = null;
    // Use the same MongoDB URI as the bot
    this.uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/otp_bot';
    this.dbName = process.env.MONGODB_DATABASE || 'otp_bot';
    this.isConnected = false;
  }

  async connect() {
    try {
      if (this.isConnected) return this.db;
      
      console.log(`🔗 Connecting to MongoDB: ${this.uri}`);
      console.log(`📊 Database: ${this.dbName}`);
      
      this.client = new MongoClient(this.uri, {
        maxPoolSize: parseInt(process.env.DB_MAX_POOL_SIZE) || 10,
        minPoolSize: parseInt(process.env.DB_MIN_POOL_SIZE) || 1,
        maxIdleTimeMS: parseInt(process.env.DB_MAX_IDLE_TIME_MS) || 30000,
        serverSelectionTimeoutMS: 5000,
        connectTimeoutMS: parseInt(process.env.DB_CONNECT_TIMEOUT_MS) || 10000,
        socketTimeoutMS: parseInt(process.env.DB_SOCKET_TIMEOUT_MS) || 10000
      });
      
      await this.client.connect();
      this.db = this.client.db(this.dbName);
      this.isConnected = true;
      
      console.log('✅ Connected to MongoDB successfully');
      return this.db;
    } catch (error) {
      console.error('❌ MongoDB connection error:', error);
      this.isConnected = false;
      throw error;
    }
  }

  async disconnect() {
    if (this.client) {
      await this.client.close();
      this.isConnected = false;
      console.log('🔌 Disconnected from MongoDB');
    }
  }

  getCollection(collectionName) {
    if (!this.db || !this.isConnected) {
      throw new Error('Database not connected. Call connect() first.');
    }
    
    // Validate collection name
    if (!validateInput.string(collectionName, 50)) {
      throw new Error('Invalid collection name');
    }
    
    return this.db.collection(collectionName);
  }

  // Dashboard data methods - Get real data from bot's MongoDB
  async getDashboardData() {
    try {
      const botStats = await this.getBotStats();
      
      // Get additional data from website database
      const servicesCollection = this.getCollection('services');
      const serversCollection = this.getCollection('servers');
      
      // Get real top services from database
      const topServices = await servicesCollection
        .find({})
        .sort({ users: -1 })
        .limit(3)
        .toArray();
      
      // Get server count
      const serverCount = await serversCollection.countDocuments();
      
      // Get service count
      const serviceCount = await servicesCollection.countDocuments();
      
      // Use bot data for dashboard
      const stats = {
        todaysEarnings: `₹${botStats.totalBalance.toFixed(2)}`,
        totalEarnings: `₹${botStats.totalBalance.toFixed(2)}`,
        todaysUsers: botStats.todaysUsers,
        totalUsers: botStats.totalUsers,
        todaysSold: botStats.todaysNumbersSold,
        totalSold: botStats.totalNumbersSold,
        topServices: topServices,
        serverCount: serverCount,
        serviceCount: serviceCount,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      return stats;
      
    } catch (error) {
      console.error('❌ Error getting dashboard data:', error);
      
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
  
  // New method to get bot statistics - Uses the same database as bot
  async getBotStats() {
    try {
      // Use the same MongoDB connection as configured
      const usersCollection = this.getCollection(process.env.MONGODB_COLLECTION || 'users');
      
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
      
      return {
        totalUsers,
        todaysUsers,
        totalBalance: parseFloat(totalBalance.toFixed(2)),
        todaysTransactions,
        totalTransactions: 0, // Will be calculated if needed
        todaysNumbersSold,
        totalNumbersSold
      };
      
    } catch (error) {
      console.error('❌ Error getting bot stats:', error);
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
      // Validate and sanitize server data
      const validatedData = {
        server_name: validateInput.string(serverData.server_name, 100),
        country: validateInput.string(serverData.country, 10),
        flag: validateInput.string(serverData.flag, 50),
        status: validateInput.string(serverData.status, 20) || 'active',
        description: validateInput.string(serverData.description, 500) || ''
      };
      
      // Check if required fields are valid
      if (!validatedData.server_name || !validatedData.country || !validatedData.flag) {
        throw new Error('Invalid server data: server_name, country, and flag are required');
      }
      
      const serversCollection = this.getCollection('servers');
      const result = await serversCollection.insertOne({
        ...validatedData,
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
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      const result = await serversCollection.updateOne(
        { _id: objectId },
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

  async getServerById(id) {
    try {
      const serversCollection = this.getCollection('servers');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      const server = await serversCollection.findOne({ _id: objectId });
      return server;
    } catch (error) {
      console.error('Error getting server by ID:', error);
      throw error;
    }
  }

  async deleteServer(id) {
    try {
      console.log(`🗑️ [DEBUG] Deleting server with ID: ${id}`);
      
      // Validate ObjectId
      const validatedId = validateInput.objectId(id);
      if (!validatedId) {
        throw new Error('Invalid server ID format');
      }
      
      const serversCollection = this.getCollection('servers');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(validatedId);
      
      console.log(`🔍 [DEBUG] Searching for server with ObjectId: ${objectId}`);
      const result = await serversCollection.deleteOne({ _id: objectId });
      console.log(`✅ [DEBUG] Server delete result: ${result.deletedCount} deleted`);
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error deleting server:', error);
      throw error;
    }
  }

  async deleteAllServers() {
    try {
      console.log('🗑️ [DEBUG] Deleting all servers');
      const serversCollection = this.getCollection('servers');
      const result = await serversCollection.deleteMany({});
      console.log(`✅ [DEBUG] Bulk server delete result: ${result.deletedCount} deleted`);
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error deleting all servers:', error);
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
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      const result = await servicesCollection.updateOne(
        { _id: objectId },
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

  async getServiceById(id) {
    try {
      const servicesCollection = this.getCollection('services');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      const service = await servicesCollection.findOne({ _id: objectId });
      return service;
    } catch (error) {
      console.error('Error getting service by ID:', error);
      throw error;
    }
  }

  async deleteService(id) {
    try {
      console.log(`🗑️ [DEBUG] Deleting service with ID: ${id}`);
      const servicesCollection = this.getCollection('services');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      console.log(`🔍 [DEBUG] Searching for service with ObjectId: ${objectId}`);
      const result = await servicesCollection.deleteOne({ _id: objectId });
      console.log(`✅ [DEBUG] Service delete result: ${result.deletedCount} deleted`);
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error deleting service:', error);
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
      
      // Validate and sanitize API data
      const validatedData = {
        server_id: validateInput.objectId(apiData.server_id),
        api_name: validateInput.string(apiData.api_name, 100),
        use_auth_headers: typeof apiData.use_auth_headers === 'boolean' ? apiData.use_auth_headers : false,
        api_response_type: validateInput.string(apiData.api_response_type, 20),
        get_number_url: validateInput.url(apiData.get_number_url),
        get_message_url: validateInput.url(apiData.get_message_url),
        cancel_number_url: validateInput.url(apiData.cancel_number_url),
        auto_cancel_minutes: validateInput.number(apiData.auto_cancel_minutes) || 5,
        retry_times: validateInput.number(apiData.retry_times) || 0,
        status: typeof apiData.status === 'boolean' ? apiData.status : true
      };
      
      // Check if required fields are valid
      if (!validatedData.server_id || !validatedData.api_name || !validatedData.api_response_type || 
          !validatedData.get_number_url || !validatedData.get_message_url || !validatedData.cancel_number_url) {
        throw new Error('Invalid API data: server_id, api_name, api_response_type, get_number_url, get_message_url, and cancel_number_url are required');
      }
      
      const apisCollection = this.getCollection('apis');
      
      const apiToInsert = {
        ...validatedData,
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
        console.log(`   ${index + 1}. ${api.api_name} - ${api.get_number_url} - ID: ${api._id}`);
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
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      // Validate and sanitize API data for update
      const validatedData = {
        server_id: validateInput.objectId(apiData.server_id),
        api_name: validateInput.string(apiData.api_name, 100),
        use_auth_headers: typeof apiData.use_auth_headers === 'boolean' ? apiData.use_auth_headers : false,
        api_response_type: validateInput.string(apiData.api_response_type, 20),
        get_number_url: validateInput.url(apiData.get_number_url),
        get_message_url: validateInput.url(apiData.get_message_url),
        cancel_number_url: validateInput.url(apiData.cancel_number_url),
        auto_cancel_minutes: validateInput.number(apiData.auto_cancel_minutes) || 5,
        retry_times: validateInput.number(apiData.retry_times) || 0,
        status: typeof apiData.status === 'boolean' ? apiData.status : true
      };
      
      const result = await apisCollection.updateOne(
        { _id: objectId },
        { 
          $set: {
            ...validatedData,
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

  async getApiById(id) {
    try {
      const apisCollection = this.getCollection('apis');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      const api = await apisCollection.findOne({ _id: objectId });
      return api;
    } catch (error) {
      console.error('Error getting API by ID:', error);
      throw error;
    }
  }

  async deleteApi(id) {
    try {
      console.log(`🗑️ [DEBUG] Deleting API with ID: ${id}`);
      const apisCollection = this.getCollection('apis');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      console.log(`🔍 [DEBUG] Searching for API with ObjectId: ${objectId}`);
      const result = await apisCollection.deleteOne({ _id: objectId });
      
      console.log(`✅ [DEBUG] API delete result: ${result.deletedCount} deleted`);
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error deleting API:', error);
      throw error;
    }
  }

  async getApis() {
    try {
      const apisCollection = this.getCollection('apis');
      return await apisCollection.find({}).toArray();
    } catch (error) {
      console.error('Error getting APIs:', error);
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
      console.log(`🗑️ [DEBUG] Deleting flag with ID: ${id}`);
      const flagsCollection = this.getCollection('flags');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      console.log(`🔍 [DEBUG] Searching for flag with ObjectId: ${objectId}`);
      const result = await flagsCollection.deleteOne({ _id: objectId });
      console.log(`✅ [DEBUG] Flag delete result: ${result.deletedCount} deleted`);
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error deleting flag:', error);
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

  // Promocode methods
  async getPromocodes() {
    try {
      const promocodesCollection = this.getCollection('promocodes');
      return await promocodesCollection.find({}).sort({ createdAt: -1 }).toArray();
    } catch (error) {
      console.error('Error getting promocodes:', error);
      throw error;
    }
  }

  async addPromocode(promocodeData) {
    try {
      const promocodesCollection = this.getCollection('promocodes');
      const result = await promocodesCollection.insertOne({
        ...promocodeData,
        createdAt: new Date(),
        updatedAt: new Date()
      });
      return result;
    } catch (error) {
      console.error('Error adding promocode:', error);
      throw error;
    }
  }

  async updatePromocode(id, promocodeData) {
    try {
      const promocodesCollection = this.getCollection('promocodes');
      const result = await promocodesCollection.updateOne(
        { _id: id },
        { 
          $set: {
            ...promocodeData,
            updatedAt: new Date()
          }
        }
      );
      return result;
    } catch (error) {
      console.error('Error updating promocode:', error);
      throw error;
    }
  }

  async deletePromocode(id) {
    try {
      console.log(`🗑️ [DEBUG] Deleting promocode with ID: ${id}`);
      const promocodesCollection = this.getCollection('promocodes');
      
      // Convert string id to ObjectId
      const { ObjectId } = require('mongodb');
      const objectId = new ObjectId(id);
      
      console.log(`🔍 [DEBUG] Searching for promocode with ObjectId: ${objectId}`);
      const result = await promocodesCollection.deleteOne({ _id: objectId });
      console.log(`✅ [DEBUG] Promocode delete result: ${result.deletedCount} deleted`);
      return result;
    } catch (error) {
      console.error('❌ [DEBUG] Error deleting promocode:', error);
      throw error;
    }
  }

  async getPromocodeById(id) {
    try {
      const promocodesCollection = this.getCollection('promocodes');
      const promocode = await promocodesCollection.findOne({ _id: id });
      return promocode;
    } catch (error) {
      console.error('Error getting promocode by ID:', error);
      throw error;
    }
  }
}

module.exports = new Database();
