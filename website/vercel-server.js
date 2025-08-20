const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const database = require('./config/database');

const app = express();
const port = process.env.PORT || 3000;

// Set EJS as templating engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views/v3'));

// Serve static files
app.use('/styles', express.static(path.join(__dirname, 'public/styles')));
app.use('/public', express.static(path.join(__dirname, 'public')));

// Parse JSON and URL-encoded bodies
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize database connection
let dbInitialized = false;

// Middleware to ensure database is connected
app.use(async (req, res, next) => {
  if (!dbInitialized) {
    try {
      await database.connect();
      dbInitialized = true;
    } catch (error) {
      console.error('Database connection failed:', error);
      return res.status(500).json({ error: 'Database connection failed' });
    }
  }
  next();
});

// Routes
app.get('/', (req, res) => {
  res.redirect('/admin-dashboard');
});

app.get('/admin-dashboard', async (req, res) => {
  console.log('🌐 [DEBUG] /admin-dashboard route accessed');
  
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
    const flags = await database.getFlags();
    res.render('connect-api', { 
      flags,
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

app.get('/my-services', async (req, res) => {
  try {
    const services = await database.getServices();
    const flags = await database.getFlags();
    
    res.render('my-services', { 
      services,
      flags,
      page: 'my-services'
    });
  } catch (error) {
    console.error('Error loading my-services page:', error);
    res.status(500).render('error', { 
      message: 'Error loading services',
      page: 'my-services'
    });
  }
});

app.get('/bot-settings', async (req, res) => {
  try {
    const flags = await database.getFlags();
    res.render('bot-settings', { 
      flags,
      page: 'bot-settings'
    });
  } catch (error) {
    console.error('Error loading bot-settings page:', error);
    res.status(500).render('error', { 
      message: 'Error loading page',
      page: 'bot-settings'
    });
  }
});

app.get('/qr-code', async (req, res) => {
  try {
    const flags = await database.getFlags();
    res.render('qr-code', { 
      flags,
      page: 'qr-code'
    });
  } catch (error) {
    console.error('Error loading qr-code page:', error);
    res.status(500).render('error', { 
      message: 'Error loading page',
      page: 'qr-code'
    });
  }
});

app.get('/all-users', async (req, res) => {
  try {
    const users = await database.getUsers();
    const flags = await database.getFlags();
    
    res.render('all-users', { 
      users,
      flags,
      page: 'all-users'
    });
  } catch (error) {
    console.error('Error loading all-users page:', error);
    res.status(500).render('error', { 
      message: 'Error loading users',
      page: 'all-users'
    });
  }
});

app.get('/user-details/:userId', async (req, res) => {
  try {
    const userId = req.params.userId;
    const user = await database.getUserById(userId);
    const flags = await database.getFlags();
    
    if (!user) {
      return res.status(404).render('not-found', { 
        flags,
        page: 'not-found'
      });
    }
    
    res.render('user-details', { 
      user,
      flags,
      page: 'user-details'
    });
  } catch (error) {
    console.error('Error loading user details:', error);
    res.status(500).render('error', { 
      message: 'Error loading user details',
      page: 'user-details'
    });
  }
});

// API routes for AJAX requests
app.post('/api/add-server', async (req, res) => {
  try {
    const result = await database.addServer(req.body);
    res.json({ success: true, data: result });
  } catch (error) {
    console.error('Error adding server:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/add-service', async (req, res) => {
  try {
    const result = await database.addService(req.body);
    res.json({ success: true, data: result });
  } catch (error) {
    console.error('Error adding service:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/update-flags', async (req, res) => {
  try {
    const result = await database.updateFlags(req.body);
    res.json({ success: true, data: result });
  } catch (error) {
    console.error('Error updating flags:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Health check endpoint for Vercel
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).render('not-found', { 
    page: 'not-found'
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).render('error', { 
    message: 'Internal server error',
    page: 'error'
  });
});

// Only start the server if this file is run directly
if (require.main === module) {
  app.listen(port, () => {
    console.log(`🚀 Server running on port ${port}`);
    console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
  });
}

// Export for Vercel
module.exports = app;
