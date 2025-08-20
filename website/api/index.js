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
      '/admin-dashboard'
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

  app.get('/add-server', (req, res) => {
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
      '/add-server'
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
