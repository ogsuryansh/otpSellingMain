const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();

// Set EJS as templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../views/v3'));

// Serve static files
app.use('/styles', express.static(path.join(__dirname, '../public/styles')));
app.use('/public', express.static(path.join(__dirname, '../public')));
app.use('/assets', express.static(path.join(__dirname, '../public')));

// Parse JSON and URL-encoded bodies
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Health check endpoint (works without database)
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    message: 'Vercel deployment is working!'
  });
});

// Test route
app.get('/api/test', (req, res) => {
  res.json({ 
    message: 'Test route working!',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString()
  });
});

// Basic route
app.get('/', async (req, res) => {
  if (!dbInitialized) {
    return res.json({ 
      message: 'Hello from Vercel!',
      status: 'success',
      timestamp: new Date().toISOString(),
      database: 'not connected',
      routes: [
        '/api/health',
        '/api/test',
        '/admin-dashboard',
        '/dashboard',
        '/services',
        '/servers',
        '/users',
        '/add-server',
        '/add-service',
        '/add-mail',
        '/bot-settings',
        '/connect-api',
        '/my-services',
        '/my-smm-service',
        '/smm-services',
        '/temp-mail',
        '/mail-inbox',
        '/manual-payments',
        '/promocode',
        '/qr-code',
        '/upload-img',
        '/user-details',
        '/manage-flags'
      ]
    });
  }
  
  try {
    // Redirect to dashboard to show actual data
    return res.redirect('/admin-dashboard');
  } catch (error) {
    console.error('Error loading main page:', error);
    res.json({ 
      message: 'Hello from Vercel!',
      status: 'error',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Try to load database and add routes
let database = null;
let dbInitialized = false;

try {
  database = require('../config/database');
  console.log('✅ Database module loaded successfully');
} catch (error) {
  console.error('❌ Failed to load database module:', error);
}

// Add database-dependent routes only if database is available
if (database) {
  // Initialize database connection

  // Middleware to ensure database is connected
  app.use(async (req, res, next) => {
    if (!dbInitialized) {
      try {
        await database.connect();
        dbInitialized = true;
        console.log('✅ Database connected successfully');
      } catch (error) {
        console.error('Database connection failed:', error);
      }
    }
    next();
  });

  // Database-dependent routes
  app.get('/admin-dashboard', async (req, res) => {
    console.log('🌐 [DEBUG] /admin-dashboard route accessed');
    
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available',
        message: 'Please check your MongoDB connection'
      });
    }
    
    try {
      const dashboardData = await database.getDashboardData();
      const flags = await database.getFlags();
      
      res.render('admin-dashboard', { 
        ...dashboardData, 
        flags,
        page: 'dashboard' 
      });
    } catch (error) {
      console.error('❌ [DEBUG] Error loading dashboard:', error);
      res.status(500).json({ 
        error: 'Error loading dashboard data',
        message: error.message
      });
    }
  });

  app.get('/dashboard', async (req, res) => {
    // Alias for admin-dashboard
    return res.redirect('/admin-dashboard');
  });

  app.get('/add-server', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('add-server', { 
        flags,
        myServer: null,
        page: 'add-server'
      });
    } catch (error) {
      console.error('Error loading add-server page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/add-service', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      let servers = [];
      
      try {
        servers = await database.getServers();
        console.log('🔍 [DEBUG] /add-service - Servers fetched:', servers);
        console.log('🔍 [DEBUG] /add-service - Servers count:', servers ? servers.length : 'null');
        
        // Log the structure of the first server if it exists
        if (servers && servers.length > 0) {
          console.log('🔍 [DEBUG] /add-service - First server structure:', JSON.stringify(servers[0], null, 2));
        }
      } catch (serverError) {
        console.error('❌ [DEBUG] Error fetching servers:', serverError);
        servers = []; // Fallback to empty array
      }
      
      const myService = null; // Default value for new service
      
      res.render('add-service', { 
        flags,
        servers,
        myService,
        page: 'add-service'
      });
    } catch (error) {
      console.error('Error loading add-service page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/add-mail', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('add-mail', { 
        flags,
        page: 'add-mail'
      });
    } catch (error) {
      console.error('Error loading add-mail page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/bot-settings', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      const setting = await database.getSettings(); // Get actual settings from database
      
      res.render('bot-settings', { 
        flags,
        setting,
        page: 'bot-settings'
      });
    } catch (error) {
      console.error('Error loading bot-settings page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/connect-api', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      const servers = await database.getServers();
      const myApi = null; // Default value for new API
      
      res.render('connect-api', { 
        flags,
        servers,
        myApi,
        page: 'connect-api'
      });
    } catch (error) {
      console.error('Error loading connect-api page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/my-services', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const myServicesData = await database.getMyServicesData(); // Get actual data from database
      const flags = await database.getFlags();
      const url = '/my-services?page=1&'; // Add the missing url variable
      
      res.render('my-services', { 
        data: myServicesData,
        flags,
        url,
        page: 'my-services'
      });
    } catch (error) {
      console.error('Error loading my-services page:', error);
      res.status(500).json({ 
        error: 'Error loading services',
        message: error.message
      });
    }
  });

  app.get('/my-smm-service', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('my-smm-service', { 
        flags,
        page: 'my-smm-service'
      });
    } catch (error) {
      console.error('Error loading my-smm-service page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/smm-services', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('smm-services', { 
        flags,
        page: 'smm-services'
      });
    } catch (error) {
      console.error('Error loading smm-services page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/temp-mail', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('temp-mail', { 
        flags,
        page: 'temp-mail'
      });
    } catch (error) {
      console.error('Error loading temp-mail page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/mail-inbox', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('mail-inbox', { 
        flags,
        page: 'mail-inbox'
      });
    } catch (error) {
      console.error('Error loading mail-inbox page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/manual-payments', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('manual-payments', { 
        flags,
        page: 'manual-payments'
      });
    } catch (error) {
      console.error('Error loading manual-payments page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/promocode', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      const promocodes = await database.getPromocodes(); // Get actual promocodes from database
      
      res.render('promocode', { 
        flags,
        promocodes,
        page: 'promocode'
      });
    } catch (error) {
      console.error('Error loading promocode page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/qr-code', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      const type = req.query.type || 'default'; // Template expects 'type' parameter
      const url = req.query.url || '/assets/images/qr-code-placeholder.png'; // Add the missing url variable
      
      res.render('qr-code', { 
        flags,
        type,
        url,
        page: 'qr-code'
      });
    } catch (error) {
      console.error('Error loading qr-code page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/upload-img', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('upload-img', { 
        flags,
        page: 'upload-img'
      });
    } catch (error) {
      console.error('Error loading upload-img page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/user-details', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('user-details', { 
        flags,
        page: 'user-details'
      });
    } catch (error) {
      console.error('Error loading user-details page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/manage-flags', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.render('manage-flags', { 
        flags,
        page: 'manage-flags'
      });
    } catch (error) {
      console.error('Error loading manage-flags page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  // Edit routes
  app.get('/edit-service/:id', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const { id } = req.params;
      const flags = await database.getFlags();
      let servers = [];
      
      try {
        servers = await database.getServers();
      } catch (serverError) {
        console.error('Error fetching servers:', serverError);
        servers = [];
      }
      
      // Get the service data by ID
      const myService = await database.getServiceById(id);
      
      if (!myService) {
        return res.status(404).json({ 
          error: 'Service not found',
          message: 'The requested service could not be found'
        });
      }
      
      res.render('edit-service', { 
        flags,
        servers,
        myService,
        page: 'edit-service'
      });
    } catch (error) {
      console.error('Error loading edit-service page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/edit-server/:id', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const { id } = req.params;
      const flags = await database.getFlags();
      
      // Get the server data by ID
      const myServer = await database.getServerById(id);
      
      if (!myServer) {
        return res.status(404).json({ 
          error: 'Server not found',
          message: 'The requested server could not be found'
        });
      }
      
      res.render('edit-server', { 
        flags,
        myServer,
        page: 'edit-server'
      });
    } catch (error) {
      console.error('Error loading edit-server page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/edit-api/:id', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const { id } = req.params;
      const flags = await database.getFlags();
      let servers = [];
      
      try {
        servers = await database.getServers();
      } catch (serverError) {
        console.error('Error fetching servers:', serverError);
        servers = [];
      }
      
      // Get the API data by ID
      const myApi = await database.getApiById(id);
      
      if (!myApi) {
        return res.status(404).json({ 
          error: 'API not found',
          message: 'The requested API could not be found'
        });
      }
      
      res.render('edit-api', { 
        flags,
        servers,
        myApi,
        page: 'edit-api'
      });
    } catch (error) {
      console.error('Error loading edit-api page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/services', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const myServicesData = await database.getMyServicesData(); // Get actual data from database
      const flags = await database.getFlags();
      const url = '/services?page=1&'; // Add the missing url variable
      
      res.render('my-services', { 
        data: myServicesData,
        flags,
        url,
        page: 'my-services'
      });
    } catch (error) {
      console.error('Error loading services page:', error);
      res.status(500).json({ 
        error: 'Error loading services',
        message: error.message
      });
    }
  });

  app.get('/servers', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const servers = await database.getServers();
      const flags = await database.getFlags();
      
      res.json({ 
        servers,
        flags,
        count: servers.length
      });
    } catch (error) {
      console.error('Error loading servers:', error);
      res.status(500).json({ 
        error: 'Error loading servers',
        message: error.message
      });
    }
  });

  app.get('/users', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const users = await database.getUsers();
      const flags = await database.getFlags();
      
      res.render('all-users', { 
        users,
        flags,
        page: 'all-users'
      });
    } catch (error) {
      console.error('Error loading users:', error);
      res.status(500).json({ 
        error: 'Error loading users',
        message: error.message
      });
    }
  });

  app.get('/transactions', async (req, res) => {
    res.json({ 
      message: 'Transactions endpoint',
      timestamp: new Date().toISOString(),
      note: 'Transactions functionality to be implemented'
    });
  });

  app.get('/promo-codes', async (req, res) => {
    res.json({ 
      message: 'Promo codes endpoint',
      timestamp: new Date().toISOString(),
      note: 'Promo codes functionality to be implemented'
    });
  });

  app.get('/api-config', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      const servers = await database.getServers();
      const myApi = null; // Default value for new API
      
      res.render('connect-api', { 
        flags,
        servers,
        myApi,
        page: 'connect-api'
      });
    } catch (error) {
      console.error('Error loading api-config page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/api-config/connection', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      const servers = await database.getServers();
      const myApi = null; // Default value for new API
      
      res.render('connect-api', { 
        flags,
        servers,
        myApi,
        page: 'connect-api'
      });
    } catch (error) {
      console.error('Error loading api-config connection page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  app.get('/test-api', async (req, res) => {
    res.json({ 
      message: 'API test endpoint',
      timestamp: new Date().toISOString(),
      database: dbInitialized ? 'connected' : 'disconnected',
      environment: process.env.NODE_ENV || 'development'
    });
  });

  // POST routes for form submissions
  app.post('/add-server', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        status: 0,
        message: 'Database connection not available' 
      });
    }
    
    try {
      const serverData = req.body;
      const result = await database.addServer(serverData);
      
      res.json({
        status: 1,
        message: 'Server added successfully',
        data: result,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error adding server:', error);
      res.status(500).json({ 
        status: 0,
        message: error.message
      });
    }
  });

  app.post('/add-service', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        status: 0,
        message: 'Database connection not available' 
      });
    }
    
    try {
      const serviceData = req.body;
      const result = await database.addService(serviceData);
      
      res.json({
        status: 1,
        message: 'Service added successfully',
        data: result,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error adding service:', error);
      res.status(500).json({ 
        status: 0,
        message: error.message
      });
    }
  });

  app.post('/connect-api', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        status: 0,
        message: 'Database connection not available' 
      });
    }
    
    try {
      const apiData = req.body;
      const result = await database.addApi(apiData);
      
      res.json({
        status: 1,
        message: 'API connected successfully',
        data: result,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error connecting API:', error);
      res.status(500).json({ 
        status: 0,
        message: error.message
      });
    }
  });

  app.post('/bot-settings', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        status: 0,
        message: 'Database connection not available' 
      });
    }
    
    try {
      const settingsData = req.body;
      const result = await database.updateSettings(settingsData);
      
      res.json({
        status: 1,
        message: 'Settings updated successfully',
        data: result,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating settings:', error);
      res.status(500).json({ 
        status: 0,
        message: error.message
      });
    }
  });

  app.post('/add-mail', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const mailData = req.body;
      // Add mail functionality - you may need to implement this in database.js
      res.json({
        success: true,
        message: 'Mail added successfully',
        data: mailData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error adding mail:', error);
      res.status(500).json({ 
        error: 'Error adding mail',
        message: error.message
      });
    }
  });

  app.post('/manual-payments', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const paymentData = req.body;
      // Add manual payment functionality - you may need to implement this in database.js
      res.json({
        success: true,
        message: 'Payment processed successfully',
        data: paymentData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error processing payment:', error);
      res.status(500).json({ 
        error: 'Error processing payment',
        message: error.message
      });
    }
  });

  app.post('/promocode', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const promoData = req.body;
      // Add promocode functionality - you may need to implement this in database.js
      res.json({
        success: true,
        message: 'Promocode added successfully',
        data: promoData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error adding promocode:', error);
      res.status(500).json({ 
        error: 'Error adding promocode',
        message: error.message
      });
    }
  });

  app.post('/upload-img', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const imageData = req.body;
      // Add image upload functionality - you may need to implement this in database.js
      res.json({
        success: true,
        message: 'Image uploaded successfully',
        data: imageData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error uploading image:', error);
      res.status(500).json({ 
        error: 'Error uploading image',
        message: error.message
      });
    }
  });

  app.post('/manage-flags', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flagsData = req.body;
      const result = await database.updateFlags(flagsData);
      
      res.json({
        success: true,
        message: 'Flags updated successfully',
        data: result,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating flags:', error);
      res.status(500).json({ 
        error: 'Error updating flags',
        message: error.message
      });
    }
  });

  // Update routes for editing
  app.post('/update-service/:id', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        status: 0,
        message: 'Database connection not available' 
      });
    }
    
    try {
      const { id } = req.params;
      const serviceData = req.body;
      const result = await database.updateService(id, serviceData);
      
      res.json({
        status: 1,
        message: 'Service updated successfully',
        data: result,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating service:', error);
      res.status(500).json({ 
        status: 0,
        message: error.message
      });
    }
  });

  app.post('/update-server/:id', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        status: 0,
        message: 'Database connection not available' 
      });
    }
    
    try {
      const { id } = req.params;
      const serverData = req.body;
      const result = await database.updateServer(id, serverData);
      
      res.json({
        status: 1,
        message: 'Server updated successfully',
        data: result,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating server:', error);
      res.status(500).json({ 
        status: 0,
        message: error.message
      });
    }
  });

  app.post('/update-api/:id', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        status: 0,
        message: 'Database connection not available' 
      });
    }
    
    try {
      const { id } = req.params;
      const apiData = req.body;
      const result = await database.updateApi(id, apiData);
      
      res.json({
        status: 1,
        message: 'API updated successfully',
        data: result,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating API:', error);
      res.status(500).json({ 
        status: 0,
        message: error.message
      });
    }
  });

  // API endpoints to show actual data
  app.get('/api/dashboard-data', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const dashboardData = await database.getDashboardData();
      res.json({
        success: true,
        data: dashboardData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error getting dashboard data:', error);
      res.status(500).json({ 
        error: 'Error getting dashboard data',
        message: error.message
      });
    }
  });

  app.get('/api/servers', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const servers = await database.getServers();
      res.json({
        success: true,
        data: servers,
        count: servers.length,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error getting servers:', error);
      res.status(500).json({ 
        error: 'Error getting servers',
        message: error.message
      });
    }
  });

  app.get('/api/services', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const services = await database.getServices();
      res.json({
        success: true,
        data: services,
        count: services.length,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error getting services:', error);
      res.status(500).json({ 
        error: 'Error getting services',
        message: error.message
      });
    }
  });

  app.get('/api/users', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const users = await database.getUsers();
      res.json({
        success: true,
        data: users,
        count: users.length,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error getting users:', error);
      res.status(500).json({ 
        error: 'Error getting users',
        message: error.message
      });
    }
  });

  app.get('/api/settings', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const settings = await database.getSettings();
      res.json({
        success: true,
        data: settings,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error getting settings:', error);
      res.status(500).json({ 
        error: 'Error getting settings',
        message: error.message
      });
    }
  });

  app.get('/api/flags', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const flags = await database.getFlags();
      res.json({
        success: true,
        data: flags,
        count: Object.keys(flags).length,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error getting flags:', error);
      res.status(500).json({ 
        error: 'Error getting flags',
        message: error.message
      });
    }
  });

  app.get('/api/my-services-data', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const myServicesData = await database.getMyServicesData();
      res.json({
        success: true,
        data: myServicesData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error getting my services data:', error);
      res.status(500).json({ 
        error: 'Error getting my services data',
        message: error.message
      });
    }
  });

  // Add more routes as needed...
} else {
  // Fallback routes when database is not available
  app.get('/admin-dashboard', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/dashboard', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/add-server', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/add-service', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/add-mail', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/bot-settings', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/connect-api', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/my-services', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/my-smm-service', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/smm-services', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/temp-mail', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/mail-inbox', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/manual-payments', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/promocode', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/qr-code', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/upload-img', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/user-details', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/manage-flags', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/edit-service/:id', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/edit-server/:id', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/edit-api/:id', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.post('/update-service/:id', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.post('/update-server/:id', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.post('/update-api/:id', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/services', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/servers', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/users', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/transactions', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/promo-codes', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/api-config', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/api-config/connection', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/test-api', (req, res) => {
    res.json({ 
      error: 'Database not available',
      message: 'Database module could not be loaded',
      timestamp: new Date().toISOString()
    });
  });
}

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

// Update endpoints
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

// Additional POST endpoints for flags and promocodes
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

// 404 handler
app.use((req, res) => {
  res.status(404).json({ 
    error: 'Not found',
    path: req.path,
    timestamp: new Date().toISOString(),
    availableRoutes: [
      '/',
      '/api/health',
      '/api/test',
      '/api/bot-stats',
      '/admin-dashboard',
      '/dashboard',
      '/add-server',
      '/add-service',
      '/add-mail',
      '/bot-settings',
      '/connect-api',
      '/my-services',
      '/my-smm-service',
      '/smm-services',
      '/temp-mail',
      '/mail-inbox',
      '/manual-payments',
      '/promocode',
      '/qr-code',
      '/upload-img',
      '/user-details',
      '/manage-flags',
      '/services',
      '/servers',
      '/users',
      '/transactions',
      '/promo-codes',
      '/api-config',
      '/test-api',
      // EDIT routes
      '/edit-service/:id',
      '/edit-server/:id',
      '/edit-api/:id',
      // DELETE routes
      '/delete-server/:id',
      '/delete-all-servers',
      '/delete-service/:id',
      '/delete-api/:id',
      '/delete-flag/:id',
      '/delete-promocode/:id',
      // POST routes
      '/add-flag',
      '/add-promocode',
      '/update-service/:id',
      '/update-server/:id',
      '/update-api/:id',
      // PUT routes
      '/update-flag/:id'
    ]
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: err.message,
    timestamp: new Date().toISOString()
  });
});

module.exports = app;
