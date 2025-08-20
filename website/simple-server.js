const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const database = require('./config/database');

const app = express();
const port = process.env.PORT || 3001;

// Add CORS support for Vercel deployment
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// Set EJS as templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views/v3'));

// Serve static files
app.use('/styles', express.static(path.join(__dirname, 'public/styles')));
app.use('/public', express.static(path.join(__dirname, 'public')));

// Parse JSON and URL-encoded bodies
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Get flags from MongoDB
let flags = {};

// Routes
app.get('/', (req, res) => {
  res.redirect('/admin-dashboard');
});

app.get('/admin-dashboard', async (req, res) => {
  console.log('🌐 [DEBUG] /admin-dashboard route accessed');
  console.log('👤 [DEBUG] Request from IP:', req.ip);
  console.log('📅 [DEBUG] Request timestamp:', new Date().toISOString());
  
  try {
    console.log('🔍 [DEBUG] Calling database.getDashboardData()...');
    const dashboardData = await database.getDashboardData();
    console.log('✅ [DEBUG] Dashboard data retrieved successfully');
    
    console.log('🔍 [DEBUG] Calling database.getFlags()...');
    const flags = await database.getFlags();
    console.log('✅ [DEBUG] Flags retrieved successfully');
    
    console.log('🎨 [DEBUG] Rendering admin-dashboard template with data...');
    res.render('admin-dashboard', { 
      ...dashboardData, 
      flags,
      page: 'dashboard' 
    });
    console.log('✅ [DEBUG] admin-dashboard page rendered successfully');
  } catch (error) {
    console.error('❌ [DEBUG] Error loading dashboard:', error);
    res.status(500).render('error', { 
      message: 'Error loading dashboard data',
      page: 'dashboard'
    });
  }
});

app.get('/add-server', async (req, res) => {
  try {
    const flags = await database.getFlags();
    res.render('add-server', { 
      flags,
      myServer: null,
      page: 'add-server'
    });
  } catch (error) {
    console.error('Error loading add-server page:', error);
    res.status(500).render('error', { 
      message: 'Error loading page',
      page: 'add-server'
    });
  }
});

app.get('/add-service', async (req, res) => {
  try {
    const servers = await database.getServers();
    
    // Convert MongoDB _id to id for template compatibility
    const processedServers = servers.map(server => ({
      ...server,
      id: server._id.toString()
    }));
    
    res.render('add-service', { 
      servers: processedServers,
      myService: null,
      page: 'add-service'
    });
  } catch (error) {
    console.error('Error loading add-service page:', error);
    res.status(500).render('error', { 
      message: 'Error loading page',
      page: 'add-service'
    });
  }
});

app.get('/connect-api', async (req, res) => {
  try {
    const servers = await database.getServers();
    
    // Convert MongoDB _id to id for template compatibility
    const processedServers = servers.map(server => ({
      ...server,
      id: server._id.toString()
    }));
    
    res.render('connect-api', { 
      servers: processedServers,
      myApi: null,
      page: 'connect-api'
    });
  } catch (error) {
    console.error('Error loading connect-api page:', error);
    res.status(500).render('error', { 
      message: 'Error loading page',
      page: 'connect-api'
    });
  }
});

app.get('/bot-settings', async (req, res) => {
  try {
    const setting = await database.getSettings();
    res.render('bot-settings', { 
      setting,
      postback_url: process.env.POSTBACK_URL || 'http://localhost:3001/webhook',
      ipv6_address: process.env.IPV6_ADDRESS || '127.0.0.1',
      page: 'bot-settings'
    });
  } catch (error) {
    console.error('Error loading bot-settings page:', error);
    res.status(500).render('error', { 
      message: 'Error loading settings',
      page: 'bot-settings'
    });
  }
});

app.get('/my-services', async (req, res) => {
  console.log('🌐 [DEBUG] /my-services route accessed');
  
  try {
    console.log('🔍 [DEBUG] Calling database.getMyServicesData()...');
    const data = await database.getMyServicesData();
    console.log('✅ [DEBUG] My services data retrieved');
    
    console.log('🔍 [DEBUG] Calling database.getFlags()...');
    const flags = await database.getFlags();
    console.log('✅ [DEBUG] Flags retrieved');
    
    console.log('📊 [DEBUG] Data sections being passed to template:');
    data.forEach((section, index) => {
      console.log(`   ${index + 1}. ${section.name} - Type: ${section.type} - Items: ${section.data.length}`);
    });
    
    console.log('🎨 [DEBUG] Rendering my-services template...');
    res.render('my-services', { 
      data,
      flags,
      url: '/my-services?',
      page: 'my-services'
    });
    console.log('✅ [DEBUG] my-services page rendered successfully');
  } catch (error) {
    console.error('❌ [DEBUG] Error loading my-services page:', error);
    res.status(500).render('error', { 
      message: 'Error loading services data',
      page: 'my-services'
    });
  }
});

app.get('/qr-code', async (req, res) => {
  try {
    const setting = await database.getSettings();
    const qrUrl = setting.manualQr || process.env.DEFAULT_QR_URL || 'https://via.placeholder.com/300x300/00D4AA/FFFFFF?text=QR+Code';
    const qrType = req.query.type || 'paytm';
    
    res.render('qr-code', { 
      type: qrType,
      url: qrUrl,
      page: 'qr-code'
    });
  } catch (error) {
    console.error('Error loading QR code page:', error);
    res.status(500).render('error', { 
      message: 'Error loading QR code',
      page: 'qr-code'
    });
  }
});

app.get('/manage-flags', async (req, res) => {
  try {
    const flags = await database.getFlags();
    const flagsArray = Object.entries(flags).map(([country, flag]) => ({ country, flag }));
    
    res.render('manage-flags', { 
      flags: flagsArray,
      page: 'manage-flags'
    });
  } catch (error) {
    console.error('Error loading manage-flags page:', error);
    res.status(500).render('error', { 
      message: 'Error loading flags data',
      page: 'manage-flags'
    });
  }
});

app.get('/promocode', async (req, res) => {
  try {
    const promocodes = await database.getPromocodes();
    res.render('promocode', { 
      promocodes,
      myPromocode: null,
      page: 'promocode'
    });
  } catch (error) {
    console.error('Error loading promocode page:', error);
    res.status(500).render('error', { 
      message: 'Error loading promocode data',
      page: 'promocode'
    });
  }
});

// Clear dashboard stats route
app.post('/clear-dashboard-stats', async (req, res) => {
  console.log('🗑️ [DEBUG] /clear-dashboard-stats route accessed');
  
  try {
    const result = await database.clearDashboardStats();
    
    if (result) {
      console.log('✅ [DEBUG] Dashboard stats cleared successfully via API');
      res.json({ 
        status: 1, 
        message: 'Dashboard stats cleared successfully! The dashboard will now show default values.' 
      });
    } else {
      console.log('⚠️ [DEBUG] No dashboard stats found to clear via API');
      res.json({ 
        status: 0, 
        message: 'No dashboard stats found to clear.' 
      });
    }
  } catch (error) {
    console.error('❌ [DEBUG] Error clearing dashboard stats via API:', error);
    res.status(500).json({ 
      status: 0, 
      message: 'Error clearing dashboard stats' 
    });
  }
});

// Handle form submissions
app.post('/add-server', async (req, res) => {
  console.log('🔍 [DEBUG] /add-server POST request received');
  console.log('📝 [DEBUG] Request body:', req.body);
  
  try {
    const { name, code, flag } = req.body;
    
    console.log('🔍 [DEBUG] Extracted data:');
    console.log('   - name:', name);
    console.log('   - code:', code);
    console.log('   - flag:', flag);
    
    if (!name || !code || !flag) {
      console.log('❌ [DEBUG] Missing required fields');
      return res.status(400).json({ 
        status: 0, 
        message: 'All fields are required' 
      });
    }

    const serverData = {
      server_name: name,
      country: code,
      flag: flag
    };

    console.log('💾 [DEBUG] Server data to save:', serverData);
    const result = await database.addServer(serverData);
    console.log('✅ [DEBUG] Server saved successfully:', result);
    
    // Update dashboard stats after adding server
    console.log('🔄 [DEBUG] Updating dashboard stats...');
    await database.updateDashboardStats();
    console.log('✅ [DEBUG] Dashboard stats updated');
    
    res.json({ 
      status: 1, 
      message: 'Server added successfully!',
      data: result
    });
  } catch (error) {
    console.error('❌ [DEBUG] Error adding server:', error);
    res.status(500).json({ 
      status: 0, 
      message: 'Error adding server' 
    });
  }
});

app.post('/add-service', async (req, res) => {
  try {
    const { server_id, service_id, name, code, description, price, cancel_disable } = req.body;
    
    if (!server_id || !service_id || !name || !code || !price) {
      return res.status(400).json({ 
        status: 0, 
        message: 'Required fields are missing' 
      });
    }

    // Get server name
    const servers = await database.getServers();
    const server = servers.find(s => s._id.toString() === server_id);
    
    const serviceData = {
      server_id,
      server_name: server ? server.server_name : process.env.DEFAULT_SERVER_NAME || 'Unknown Server',
      service_id,
      name,
      code,
      description: description || process.env.DEFAULT_SERVICE_DESCRIPTION || '',
      price: `₹${price}`,
      cancel_disable: cancel_disable || process.env.DEFAULT_CANCEL_DISABLE || '5',
      users: parseInt(process.env.DEFAULT_SERVICE_USERS) || 0
    };

    const result = await database.addService(serviceData);
    
    // Update dashboard stats after adding service
    await database.updateDashboardStats();
    
    res.json({ 
      status: 1, 
      message: 'Service added successfully!',
      data: result
    });
  } catch (error) {
    console.error('Error adding service:', error);
    res.status(500).json({ 
      status: 0, 
      message: 'Error adding service' 
    });
  }
});

app.post('/connect-api', async (req, res) => {
  console.log('🔍 [DEBUG] /connect-api POST request received');
  console.log('📝 [DEBUG] Request body:', req.body);
  
  try {
    const { server_id, api_url, api_key, api_type, status } = req.body;
    
    console.log('🔍 [DEBUG] Extracted data:');
    console.log('   - server_id:', server_id);
    console.log('   - api_url:', api_url);
    console.log('   - api_key:', api_key);
    console.log('   - api_type:', api_type);
    console.log('   - status:', status);
    
    if (!server_id || !api_url || !api_key) {
      console.log('❌ [DEBUG] Missing required fields');
      return res.status(400).json({ 
        status: 0, 
        message: 'Required fields are missing' 
      });
    }

    // Get server name
    const servers = await database.getServers();
    const server = servers.find(s => s._id.toString() === server_id);
    
    const apiData = {
      server_id,
      server_name: server ? server.server_name : process.env.DEFAULT_SERVER_NAME || 'Unknown Server',
      api_url,
      api_key,
      api_type: api_type || process.env.DEFAULT_API_TYPE || 'GET',
      status: status === 'true'
    };

    console.log('💾 [DEBUG] API data to save:', apiData);
    const result = await database.addApi(apiData);
    console.log('✅ [DEBUG] API saved successfully:', result);
    
    res.json({ 
      status: 1, 
      message: 'API connected successfully!',
      data: result
    });
  } catch (error) {
    console.error('❌ [DEBUG] Error connecting API:', error);
    res.status(500).json({ 
      status: 0, 
      message: 'Error connecting API' 
    });
  }
});

app.post('/bot-settings', async (req, res) => {
  try {
    const settingsData = req.body;
    
    // Convert string values to boolean where needed
    const processedSettings = {
      ...settingsData,
      smmPanel: settingsData.smmPanel === 'true',
      manual: settingsData.manual === 'true',
      paytm: settingsData.paytm === 'true',
      bharatpe: settingsData.bharatpe === 'true',
      crypto: settingsData.crypto === 'true',
      upi: settingsData.upi === 'true'
    };

    const result = await database.updateSettings(processedSettings);
    
    res.json({ 
      status: 1, 
      message: 'Settings updated successfully!',
      data: result
    });
  } catch (error) {
    console.error('Error updating settings:', error);
    res.status(500).json({ 
      status: 0, 
      message: 'Error updating settings' 
    });
  }
});

// Delete endpoints
app.delete('/delete-server/:id', async (req, res) => {
  try {
    console.log(`🗑️ [DEBUG] Deleting server with ID: ${req.params.id}`);
    const { id } = req.params;
    const result = await database.deleteServer(id);
    
    if (result.deletedCount > 0) {
      console.log(`✅ [DEBUG] Successfully deleted server with ID: ${id}`);
      // Update dashboard stats after deleting server
      await database.updateDashboardStats();
      res.json({ status: 1, message: 'Server deleted successfully!' });
    } else {
      console.log(`❌ [DEBUG] Server not found with ID: ${id}`);
      res.status(404).json({ status: 0, message: 'Server not found' });
    }
  } catch (error) {
    console.error('❌ [DEBUG] Error deleting server:', error);
    res.status(500).json({ status: 0, message: 'Error deleting server' });
  }
});

app.delete('/delete-all-servers', async (req, res) => {
  try {
    console.log('🗑️ [DEBUG] Bulk deleting all servers');
    const result = await database.deleteAllServers();
    
    console.log(`✅ [DEBUG] Successfully deleted ${result.deletedCount} servers`);
    // Update dashboard stats after deleting servers
    await database.updateDashboardStats();
    res.json({ 
      status: 1, 
      message: `Successfully deleted ${result.deletedCount} servers!`,
      deletedCount: result.deletedCount
    });
  } catch (error) {
    console.error('❌ [DEBUG] Error bulk deleting servers:', error);
    res.status(500).json({ status: 0, message: 'Error deleting servers' });
  }
});

app.delete('/delete-service/:id', async (req, res) => {
  try {
    console.log(`🗑️ [DEBUG] Deleting service with ID: ${req.params.id}`);
    const { id } = req.params;
    const result = await database.deleteService(id);
    
    if (result.deletedCount > 0) {
      console.log(`✅ [DEBUG] Successfully deleted service with ID: ${id}`);
      // Update dashboard stats after deleting service
      await database.updateDashboardStats();
      res.json({ status: 1, message: 'Service deleted successfully!' });
    } else {
      console.log(`❌ [DEBUG] Service not found with ID: ${id}`);
      res.status(404).json({ status: 0, message: 'Service not found' });
    }
  } catch (error) {
    console.error('❌ [DEBUG] Error deleting service:', error);
    res.status(500).json({ status: 0, message: 'Error deleting service' });
  }
});

app.delete('/delete-api/:id', async (req, res) => {
  try {
    console.log(`🗑️ [DEBUG] Deleting API with ID: ${req.params.id}`);
    const { id } = req.params;
    const result = await database.deleteApi(id);
    
    if (result.deletedCount > 0) {
      console.log(`✅ [DEBUG] Successfully deleted API with ID: ${id}`);
      res.json({ status: 1, message: 'API deleted successfully!' });
    } else {
      console.log(`❌ [DEBUG] API not found with ID: ${id}`);
      res.status(404).json({ status: 0, message: 'API not found' });
    }
  } catch (error) {
    console.error('❌ [DEBUG] Error deleting API:', error);
    res.status(500).json({ status: 0, message: 'Error deleting API' });
  }
});

// Flag management endpoints
app.post('/add-flag', async (req, res) => {
  try {
    const { country, flag } = req.body;
    
    if (!country || !flag) {
      return res.status(400).json({ 
        status: 0, 
        message: 'Country and flag are required' 
      });
    }

    const flagData = {
      country,
      flag
    };

    const result = await database.addFlag(flagData);
    
    res.json({ 
      status: 1, 
      message: 'Flag added successfully!',
      data: result
    });
  } catch (error) {
    console.error('Error adding flag:', error);
    res.status(500).json({ 
      status: 0, 
      message: 'Error adding flag' 
    });
  }
});

app.put('/update-flag/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { country, flag } = req.body;
    
    if (!country || !flag) {
      return res.status(400).json({ 
        status: 0, 
        message: 'Country and flag are required' 
      });
    }

    const flagData = {
      country,
      flag
    };

    const result = await database.updateFlag(id, flagData);
    
    if (result.modifiedCount > 0) {
      res.json({ 
        status: 1, 
        message: 'Flag updated successfully!',
        data: result
      });
    } else {
      res.status(404).json({ status: 0, message: 'Flag not found' });
    }
  } catch (error) {
    console.error('Error updating flag:', error);
    res.status(500).json({ 
      status: 0, 
      message: 'Error updating flag' 
    });
  }
});

app.delete('/delete-flag/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await database.deleteFlag(id);
    
    if (result.deletedCount > 0) {
      res.json({ status: 1, message: 'Flag deleted successfully!' });
    } else {
      res.status(404).json({ status: 0, message: 'Flag not found' });
    }
  } catch (error) {
    console.error('Error deleting flag:', error);
    res.status(500).json({ status: 0, message: 'Error deleting flag' });
  }
});

// Promocode management endpoints
app.post('/add-promocode', async (req, res) => {
  try {
    const { code, max_uses, amount } = req.body;
    
    if (!code || !max_uses || !amount) {
      return res.status(400).json({ 
        status: 0, 
        message: 'All fields are required' 
      });
    }

    const promocodeData = {
      code: code.toUpperCase(),
      max_uses: parseInt(max_uses),
      current_uses: 0,
      amount: parseFloat(amount),
      is_active: true
    };

    const result = await database.addPromocode(promocodeData);
    
    res.json({ 
      status: 1, 
      message: 'Promocode added successfully!',
      data: result
    });
  } catch (error) {
    console.error('Error adding promocode:', error);
    res.status(500).json({ 
      status: 0, 
      message: 'Error adding promocode' 
    });
  }
});

app.delete('/delete-promocode/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await database.deletePromocode(id);
    
    if (result.deletedCount > 0) {
      res.json({ status: 1, message: 'Promocode deleted successfully!' });
    } else {
      res.status(404).json({ status: 0, message: 'Promocode not found' });
    }
  } catch (error) {
    console.error('Error deleting promocode:', error);
    res.status(500).json({ status: 0, message: 'Error deleting promocode' });
  }
});

// Bot Stats API - Get real data from bot's MongoDB
app.get('/api/bot-stats', async (req, res) => {
  try {
    console.log('🔍 [DEBUG] /api/bot-stats endpoint accessed');
    
    // Get bot statistics from database
    const botStats = await database.getBotStats();
    
    console.log('✅ [DEBUG] Bot stats retrieved for API:', botStats);
    
    res.json({
      success: true,
      data: botStats,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ [DEBUG] Error in /api/bot-stats:', error);
          res.status(500).json({
        success: false,
        error: error.message,
        data: {
          totalUsers: 0,
          todaysUsers: 0,
          totalBalance: 0,
          todaysTransactions: 0,
          totalTransactions: 0,
          todaysNumbersSold: 0,
          totalNumbersSold: 0
        }
      });
  }
});

// Initialize database connection and start server
async function startServer() {
  try {
    await database.connect();
    
    app.listen(port, () => {
      console.log(`🚀 Website running at: http://localhost:${port}`);
      console.log(`📱 Admin Dashboard: http://localhost:${port}/admin-dashboard`);
      console.log(`➕ Add Server: http://localhost:${port}/add-server`);
      console.log(`➕ Add Service: http://localhost:${port}/add-service`);
      console.log(`🔌 Connect API: http://localhost:${port}/connect-api`);
      console.log(`⚙️ Bot Settings: http://localhost:${port}/bot-settings`);
      console.log(`📊 My Services: http://localhost:${port}/my-services`);
      console.log(`💳 QR Code: http://localhost:${port}/qr-code`);
      console.log(`🏁 Manage Flags: http://localhost:${port}/manage-flags`);
      console.log(`💾 Database: MongoDB Connected`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down server...');
  await database.disconnect();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Shutting down server...');
  await database.disconnect();
  process.exit(0);
});

startServer();
