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
app.get('/', (req, res) => {
  res.json({ 
    message: 'Hello from Vercel!',
    status: 'success',
    timestamp: new Date().toISOString(),
    routes: [
      '/api/health',
      '/api/test',
      '/admin-dashboard',
      '/dashboard',
      '/services',
      '/servers',
      '/users'
    ]
  });
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

  app.get('/services', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const services = await database.getServices();
      const flags = await database.getFlags();
      
      res.render('my-services', { 
        services,
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
      res.render('connect-api', { 
        flags,
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
      res.render('connect-api', { 
        flags,
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
