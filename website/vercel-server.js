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
    const servers = await database.getServers();
    const flags = await database.getFlags();
    res.render('connect-api', { 
      servers,
      myApi: null,
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

app.get('/edit-api/:id', async (req, res) => {
  try {
    const apiId = req.params.id;
    const api = await database.getApiById(apiId);
    const servers = await database.getServers();
    const flags = await database.getFlags();
    
    if (!api) {
      return res.status(404).render('not-found', { 
        flags,
        page: 'not-found'
      });
    }
    
    res.render('edit-api', { 
      api,
      servers,
      flags,
      page: 'edit-api'
    });
  } catch (error) {
    console.error('Error loading edit-api page:', error);
    res.status(500).render('error', { 
      message: 'Error loading page',
      page: 'edit-api'
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

// Add server route (non-API version)
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

// Add service route (non-API version)
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

app.post('/api/update-flags', async (req, res) => {
  try {
    const result = await database.updateFlags(req.body);
    res.json({ success: true, data: result });
  } catch (error) {
    console.error('Error updating flags:', error);
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

// API endpoints for CRUD operations
app.post('/connect-api', async (req, res) => {
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

app.put('/update-api/:id', async (req, res) => {
  try {
    const apiId = req.params.id;
    const apiData = req.body;
    const result = await database.updateApi(apiId, apiData);
    
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

app.delete('/delete-api/:id', async (req, res) => {
  try {
    const apiId = req.params.id;
    const result = await database.deleteApi(apiId);
    
    res.json({
      status: 1,
      message: 'API deleted successfully',
      data: result,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error deleting API:', error);
    res.status(500).json({ 
      status: 0,
      message: error.message
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
