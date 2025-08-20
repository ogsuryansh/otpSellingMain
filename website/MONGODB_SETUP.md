# MongoDB Integration Setup

## 🎯 Overview
This application has been successfully integrated with MongoDB to replace all hardcoded data. The database connection uses the MongoDB Atlas cluster provided in your environment variables.

## 🔧 Configuration

### Environment Variables
The following environment variables are configured in `.env`:

```env
MONGODB_URI=mongodb+srv://vishalgiri0044:kR9oUspxQUtYdund@cluster0.zdudgbg.mongodb.net/otp_bot?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=otp_bot
MONGODB_COLLECTION=users
PORT=3001
HOST=localhost
NODE_ENV=development
```

### Database Collections
The application uses the following MongoDB collections:

- **`stats`** - Dashboard statistics and metrics
- **`servers`** - Server information and configurations
- **`services`** - Service definitions and pricing
- **`apis`** - API connections and configurations
- **`settings`** - Bot settings and configurations

## 🚀 Features

### ✅ What's Working
- **Real Database Storage** - All data is now stored in MongoDB
- **CRUD Operations** - Create, Read, Update, Delete for all entities
- **Form Submissions** - All forms now save data to MongoDB
- **Dashboard Data** - Real-time data from database
- **Error Handling** - Proper error handling for database operations
- **Graceful Shutdown** - Proper database connection cleanup

### 📊 Data Structure

#### Servers Collection
```javascript
{
  _id: ObjectId,
  server_name: String,
  country: String,
  flag: String,
  createdAt: Date,
  updatedAt: Date
}
```

#### Services Collection
```javascript
{
  _id: ObjectId,
  server_id: String,
  server_name: String,
  service_id: String,
  name: String,
  code: String,
  description: String,
  price: String,
  cancel_disable: String,
  users: Number,
  createdAt: Date,
  updatedAt: Date
}
```

#### APIs Collection
```javascript
{
  _id: ObjectId,
  server_id: String,
  server_name: String,
  api_url: String,
  api_key: String,
  api_type: String,
  status: Boolean,
  createdAt: Date,
  updatedAt: Date
}
```

#### Settings Collection
```javascript
{
  _id: ObjectId,
  type: "bot_settings",
  channel: String,
  supportUrl: String,
  smmPanel: Boolean,
  smmUrl: String,
  smmProfit: Number,
  manual: Boolean,
  manualUpi: String,
  manualQr: String,
  paytm: Boolean,
  paytmMid: String,
  paytmUpi: String,
  bharatpe: Boolean,
  bharatpeMid: String,
  bharatpeMtoken: String,
  bharatpeUpi: String,
  bharatpeQr: String,
  crypto: Boolean,
  cryptoHash: String,
  upi: Boolean,
  upiApi: String,
  upiPostback: String,
  upiIp: String,
  createdAt: Date,
  updatedAt: Date
}
```

## 🛠️ API Endpoints

### GET Endpoints
- `GET /admin-dashboard` - Load dashboard data from MongoDB
- `GET /add-server` - Load server form with flags
- `GET /add-service` - Load service form with servers from DB
- `GET /connect-api` - Load API form with servers from DB
- `GET /bot-settings` - Load settings from MongoDB
- `GET /my-services` - Load servers and services from DB

### POST Endpoints
- `POST /add-server` - Save new server to MongoDB
- `POST /add-service` - Save new service to MongoDB
- `POST /connect-api` - Save new API connection to MongoDB
- `POST /bot-settings` - Update settings in MongoDB

### DELETE Endpoints
- `DELETE /delete-server/:id` - Delete server from MongoDB
- `DELETE /delete-service/:id` - Delete service from MongoDB

## 🔄 Migration from Mock Data

The application has been completely migrated from hardcoded mock data to MongoDB:

### Before (Mock Data)
- Static data in `simple-server.js`
- No persistence
- Data lost on server restart

### After (MongoDB)
- Dynamic data from database
- Full persistence
- Data survives server restarts
- Real CRUD operations

## 🚀 Running the Application

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run simple:dev
   ```

3. **Access the Application**
   - Main URL: http://localhost:3001
   - Dashboard: http://localhost:3001/admin-dashboard
   - Add Server: http://localhost:3001/add-server
   - Add Service: http://localhost:3001/add-service
   - Connect API: http://localhost:3001/connect-api
   - Bot Settings: http://localhost:3001/bot-settings
   - My Services: http://localhost:3001/my-services

## 🔍 Database Operations

### Adding Data
- All forms now save data to MongoDB
- Automatic timestamps (createdAt, updatedAt)
- Validation and error handling

### Viewing Data
- Dashboard shows real-time statistics
- My Services page displays actual database records
- All data is fetched from MongoDB collections

### Updating Data
- Settings are saved to database
- Form submissions update MongoDB records
- Real-time data persistence

### Deleting Data
- Delete buttons work with MongoDB
- Proper cleanup of database records
- Confirmation dialogs for safety

## 🛡️ Error Handling

- Database connection errors are handled gracefully
- Form validation with proper error messages
- Fallback to default data if database is unavailable
- User-friendly error pages

## 📈 Benefits

1. **Data Persistence** - All data is now saved permanently
2. **Scalability** - MongoDB can handle large amounts of data
3. **Real-time Updates** - Changes are immediately reflected
4. **Data Integrity** - Proper validation and error handling
5. **Professional Setup** - Production-ready database integration

## 🎉 Success!

Your application is now fully integrated with MongoDB and ready for production use! All hardcoded data has been replaced with real database operations.
