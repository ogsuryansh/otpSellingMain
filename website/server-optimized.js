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
      styleSrc: ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.tailwindcss.com"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com"],
      scriptSrcAttr: ["'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      fontSrc: ["'self'", "https://cdnjs.cloudflare.com"],
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
    message: 'SERVER-OPTIMIZED.JS is running!',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString(),
    server: 'server-optimized.js',
    routes: {
      'GET /test': 'This route',
      'POST /clear-all-services': 'Clear all services',
      'POST /clear-dashboard-stats': 'Clear dashboard stats',
      'POST /add-server': 'Add server',
      'POST /add-service': 'Add service',
      'DELETE /delete-server/:id': 'Delete server',
      'DELETE /delete-service/:id': 'Delete service',
      'DELETE /delete-all-servers': 'Delete all servers'
    }
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
      const data = await database.getMyServicesData();
      const flags = await database.getFlags();
      
      res.render('my-services', { 
        data,
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

  // Clear all services route
  app.post('/clear-all-services', async (req, res) => {
    console.log('🗑️ [DEBUG] /clear-all-services route accessed');
    
    try {
      const result = await database.clearAllServices();
      
      console.log('✅ [DEBUG] All services cleared successfully via API');
      res.json({ 
        status: 1, 
        message: `All services cleared successfully! (${result.deletedCount} services removed)` 
      });
    } catch (error) {
      console.error('❌ [DEBUG] Error clearing all services:', error);
      res.status(500).json({ 
        status: 0, 
        message: 'Error clearing all services' 
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

  // Add server route
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

  // Add service route
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

  // Delete server route
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

  // Delete service route
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

  // Delete all servers route
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
      '/my-services',
      '/clear-all-services',
      '/clear-dashboard-stats',
      '/delete-server/:id',
      '/delete-service/:id',
      '/delete-all-servers'
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
    console.log(`🚀 SERVER-OPTIMIZED.JS running on port ${port}`);
    console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`📊 Database: ${database ? 'Available' : 'Not available'}`);
    console.log(`✅ Clear-all-services route: POST /clear-all-services`);
  });
}

// Export for Vercel
module.exports = app;
