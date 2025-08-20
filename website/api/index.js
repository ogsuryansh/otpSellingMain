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
try {
  database = require('../config/database');
  console.log('✅ Database module loaded successfully');
} catch (error) {
  console.error('❌ Failed to load database module:', error);
}

// Add database-dependent routes only if database is available
if (database) {
  // Initialize database connection
  let dbInitialized = false;

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
      const servers = await database.getServers();
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
      
      res.render('my-services', { 
        data: myServicesData,
        flags,
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
      res.render('promocode', { 
        flags,
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
      
      res.render('qr-code', { 
        flags,
        type,
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

  app.get('/services', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const myServicesData = await database.getMyServicesData(); // Get actual data from database
      const flags = await database.getFlags();
      
      res.render('my-services', { 
        data: myServicesData,
        flags,
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
      '/test-api'
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
