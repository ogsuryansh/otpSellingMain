const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
const port = process.env.PORT || 3000;

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(limiter);

// Set EJS as templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views/v3'));

// Serve static files
app.use('/styles', express.static(path.join(__dirname, 'public/styles')));
app.use('/public', express.static(path.join(__dirname, 'public')));

// Parse JSON and URL-encoded bodies
app.use(express.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    message: 'Server is running optimally!'
  });
});

// Test route
app.get('/test', (req, res) => {
  res.json({ 
    message: 'Test route working!',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString()
  });
});

// Basic route
app.get('/', (req, res) => {
  res.json({ 
    message: 'OTP Bot Web Interface',
    status: 'success',
    timestamp: new Date().toISOString(),
    routes: [
      '/api/health',
      '/test',
      '/admin-dashboard',
      '/add-server',
      '/my-services'
    ]
  });
});

// Try to load database and add routes
let database = null;
try {
  database = require('./config/database');
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
      console.error('❌ Error loading dashboard:', error);
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

  app.get('/my-services', async (req, res) => {
    if (!dbInitialized) {
      return res.status(500).json({ 
        error: 'Database connection not available' 
      });
    }
    
    try {
      const myServicesData = await database.getMyServicesData();
      const flags = await database.getFlags();
      
      res.render('my-services', { 
        myServicesData,
        flags,
        page: 'my-services'
      });
    } catch (error) {
      console.error('Error loading my-services page:', error);
      res.status(500).json({ 
        error: 'Error loading page',
        message: error.message
      });
    }
  });

  // API endpoints
  app.get('/api/servers', async (req, res) => {
    try {
      const servers = await database.getServers();
      res.json({ success: true, data: servers });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  app.get('/api/services', async (req, res) => {
    try {
      const services = await database.getServices();
      res.json({ success: true, data: services });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  app.get('/api/apis', async (req, res) => {
    try {
      const apis = await database.getApis();
      res.json({ success: true, data: apis });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

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

  app.get('/my-services', (req, res) => {
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
      '/test',
      '/admin-dashboard',
      '/add-server',
      '/my-services'
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

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  if (database) {
    database.disconnect().then(() => {
      process.exit(0);
    });
  } else {
    process.exit(0);
  }
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  if (database) {
    database.disconnect().then(() => {
      process.exit(0);
    });
  } else {
    process.exit(0);
  }
});

// Only start the server if this file is run directly
if (require.main === module) {
  app.listen(port, () => {
    console.log(`🚀 Optimized server running on port ${port}`);
    console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`📊 Database: ${database ? 'Available' : 'Not available'}`);
  });
}

// Export for Vercel
module.exports = app;
