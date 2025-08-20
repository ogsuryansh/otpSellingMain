const http = require('http');

// Test the server
const testServer = () => {
  const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/',
    method: 'GET'
  };

  const req = http.request(options, (res) => {
    console.log(`✅ Status: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      try {
        const response = JSON.parse(data);
        console.log('✅ Response:', response);
        console.log('🎉 Server is working correctly!');
      } catch (error) {
        console.log('📄 Response (not JSON):', data);
      }
    });
  });

  req.on('error', (error) => {
    console.error('❌ Error testing server:', error.message);
  });

  req.end();
};

// Wait a moment for server to start, then test
setTimeout(testServer, 2000);
