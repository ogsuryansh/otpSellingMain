# Removed Hardcoded Data - MongoDB Integration

## Changes Made

### 1. Removed Hardcoded Flags
- **Before**: Flags were hardcoded in `simple-server.js` as a static object
- **After**: Flags are now stored in MongoDB `flags` collection
- **New Features**:
  - Added `/manage-flags` page to add, edit, delete flags
  - Added API endpoints: `/add-flag`, `/update-flag/:id`, `/delete-flag/:id`
  - Flags are dynamically loaded from database on each page load

### 2. Removed Hardcoded URLs
- **Before**: Localhost URLs were hardcoded throughout the application
- **After**: All URLs now use environment variables with fallbacks
- **Updated Files**:
  - `simple-server.js`: Uses `process.env.POSTBACK_URL`, `process.env.IPV6_ADDRESS`
  - `config/database.js`: Uses `process.env.UPI_POSTBACK_URL`, `process.env.UPI_IP_ADDRESS`
  - `config.local.js`: Uses `process.env.MONGODB_URI`

### 3. Removed Hardcoded MongoDB URI
- **Before**: MongoDB connection string was hardcoded
- **After**: Uses `process.env.MONGODB_URI` with localhost fallback
- **Updated Files**:
  - `config/database.js`
  - `config.local.js`

### 4. Dynamic QR Code URLs
- **Before**: QR code URL was hardcoded to placeholder.com
- **After**: QR code URL comes from settings or environment variable
- **Updated**: `/qr-code` route now fetches URL from database settings

### 5. Removed Hardcoded Payment and Stats Values
- **Before**: Payment amounts, user counts, and stats were hardcoded
- **After**: All values come from environment variables or database
- **Updated**: Dashboard stats, service defaults, and bot settings all use environment variables

### 6. Removed Hardcoded Default Values
- **Before**: Service descriptions, cancel times, API types were hardcoded
- **After**: All default values come from environment variables
- **Updated**: Service creation, API creation, and settings initialization use environment variables

## Environment Variables Required

Create a `.env` file in the root directory with the following variables:

```env
# Server Configuration
PORT=3001
HOST=localhost

# Application Settings
APP_URL=http://localhost:3001
SESSION_SECRET=your_session_secret_here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/otp_bot
MONGODB_DATABASE=otp_bot
MONGODB_COLLECTION=users

# UPI Configuration
UPI_POSTBACK_URL=http://localhost:3001/webhook
UPI_IP_ADDRESS=127.0.0.1

# QR Code Configuration
DEFAULT_QR_URL=https://via.placeholder.com/300x300/00D4AA/FFFFFF?text=QR+Code

# Postback Configuration
POSTBACK_URL=http://localhost:3001/webhook
IPV6_ADDRESS=127.0.0.1

# Default Dashboard Stats
DEFAULT_TODAYS_EARNINGS=₹0
DEFAULT_TOTAL_EARNINGS=₹0
DEFAULT_TODAYS_USERS=0
DEFAULT_TOTAL_USERS=0
DEFAULT_TODAYS_SOLD=0
DEFAULT_TOTAL_SOLD=0

# Default Service Settings
DEFAULT_SERVER_NAME=Unknown Server
DEFAULT_SERVICE_DESCRIPTION=
DEFAULT_CANCEL_DISABLE=5
DEFAULT_SERVICE_USERS=0
DEFAULT_API_TYPE=GET

# Default Bot Settings
DEFAULT_CHANNEL=
DEFAULT_SUPPORT_URL=
DEFAULT_SMM_PANEL=false
DEFAULT_SMM_URL=
DEFAULT_SMM_PROFIT=0
DEFAULT_MANUAL=false
DEFAULT_MANUAL_UPI=
DEFAULT_MANUAL_QR=
DEFAULT_PAYTM=false
DEFAULT_PAYTM_MID=
DEFAULT_PAYTM_UPI=
DEFAULT_BHARATPE=false
DEFAULT_BHARATPE_MID=
DEFAULT_BHARATPE_MTOKEN=
DEFAULT_BHARATPE_UPI=
DEFAULT_BHARATPE_QR=
DEFAULT_CRYPTO=false
DEFAULT_CRYPTO_HASH=
DEFAULT_UPI=false
DEFAULT_UPI_API=
```

## New Database Collections

### Flags Collection
```javascript
{
  _id: ObjectId,
  country: String,    // e.g., "India"
  flag: String,       // e.g., "🇮🇳"
  createdAt: Date,
  updatedAt: Date
}
```

## New API Endpoints

### Flag Management
- `POST /add-flag` - Add a new flag
- `PUT /update-flag/:id` - Update an existing flag
- `DELETE /delete-flag/:id` - Delete a flag

### Request Format for Flags
```json
{
  "country": "Country Name",
  "flag": "🇺🇸"
}
```

## New Pages

### Manage Flags Page
- **URL**: `/manage-flags`
- **Features**: 
  - Add new flags
  - Edit existing flags
  - Delete flags
  - View all flags in a table

## Database Methods Added

### In `config/database.js`
- `getFlags()` - Get all flags as an object
- `addFlag(flagData)` - Add a new flag
- `updateFlag(id, flagData)` - Update a flag
- `deleteFlag(id)` - Delete a flag

## Benefits

1. **No Hardcoded Data**: All data now comes from MongoDB or environment variables
2. **Fully Configurable**: All URLs, settings, and default values can be changed via environment variables
3. **Dynamic**: Flags, services, and settings can be managed without code changes
4. **Scalable**: Easy to add new countries, flags, and services
5. **Maintainable**: Centralized data management
6. **Production Ready**: All hardcoded values replaced with configurable environment variables
7. **Zero Default Values**: No hardcoded payment amounts, user counts, or service defaults

## Migration Notes

- Default flags (India, USA, UK, Canada, Australia) will be automatically created when the application starts
- All default values (payments, users, settings) are now configurable via environment variables
- Existing functionality remains unchanged
- All hardcoded values have been replaced with database-driven or environment-based values
- Payment amounts, user counts, and service defaults are no longer hardcoded
- Bot settings initialization uses environment variables for all default values
