# Complete Environment Variables for Vercel Deployment

## 🔧 Required Environment Variables

Add these to your Vercel dashboard under **Settings > Environment Variables**:

### MongoDB Configuration (Already Added ✅)
```bash
MONGODB_URI=mongodb+srv://vishalgiri0044:kR9oUspxQUtYdund@cluster0.zdudgbg.mongodb.net/otp_bot?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=otp_bot
MONGODB_COLLECTION=users
```

### Application Settings
```bash
NODE_ENV=production
PORT=3000
HOST=0.0.0.0
APP_URL=https://your-app.vercel.app
SESSION_SECRET=your_very_secure_session_secret_here
```

### Default Dashboard Values
```bash
DEFAULT_TODAYS_EARNINGS=₹0
DEFAULT_TOTAL_EARNINGS=₹0
DEFAULT_TODAYS_USERS=0
DEFAULT_TOTAL_USERS=0
DEFAULT_TODAYS_SOLD=0
DEFAULT_TOTAL_SOLD=0
```

### Default Flags/Settings
```bash
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
UPI_POSTBACK_URL=https://your-app.vercel.app/webhook
UPI_IP_ADDRESS=127.0.0.1
```

## 🚀 Quick Setup

### Step 1: Add to Vercel Dashboard
1. Go to your Vercel project dashboard
2. Click **Settings** tab
3. Click **Environment Variables**
4. Add each variable above

### Step 2: Deploy
```bash
vercel --prod
```

## 📝 Environment Variables Explanation

### Core Database
- `MONGODB_URI` - Your MongoDB connection string ✅
- `MONGODB_DATABASE` - Database name ✅
- `MONGODB_COLLECTION` - Default collection name ✅

### Application
- `NODE_ENV` - Set to "production" for Vercel
- `PORT` - Vercel will set this automatically
- `HOST` - Set to "0.0.0.0" for Vercel
- `APP_URL` - Your Vercel app URL
- `SESSION_SECRET` - Secret for session management

### Dashboard Defaults
- `DEFAULT_TODAYS_EARNINGS` - Default earnings display
- `DEFAULT_TOTAL_EARNINGS` - Default total earnings
- `DEFAULT_TODAYS_USERS` - Default users count
- `DEFAULT_TOTAL_USERS` - Default total users
- `DEFAULT_TODAYS_SOLD` - Default items sold today
- `DEFAULT_TOTAL_SOLD` - Default total items sold

### Payment Settings
- `DEFAULT_CHANNEL` - Telegram channel URL
- `DEFAULT_SUPPORT_URL` - Support contact URL
- `DEFAULT_SMM_PANEL` - Enable/disable SMM panel
- `DEFAULT_SMM_URL` - SMM panel URL
- `DEFAULT_SMM_PROFIT` - SMM profit percentage
- `DEFAULT_MANUAL` - Enable manual payments
- `DEFAULT_MANUAL_UPI` - Manual UPI ID
- `DEFAULT_MANUAL_QR` - Manual QR code URL
- `DEFAULT_PAYTM` - Enable Paytm payments
- `DEFAULT_PAYTM_MID` - Paytm merchant ID
- `DEFAULT_PAYTM_UPI` - Paytm UPI ID
- `DEFAULT_BHARATPE` - Enable BharatPe payments
- `DEFAULT_BHARATPE_MID` - BharatPe merchant ID
- `DEFAULT_BHARATPE_MTOKEN` - BharatPe merchant token
- `DEFAULT_BHARATPE_UPI` - BharatPe UPI ID
- `DEFAULT_BHARATPE_QR` - BharatPe QR code URL
- `DEFAULT_CRYPTO` - Enable crypto payments
- `DEFAULT_CRYPTO_HASH` - Crypto wallet address
- `DEFAULT_UPI` - Enable UPI payments
- `DEFAULT_UPI_API` - UPI API endpoint
- `UPI_POSTBACK_URL` - UPI webhook URL
- `UPI_IP_ADDRESS` - UPI IP whitelist

## 🎯 Minimum Required Variables

If you want to start with just the essentials:

```bash
MONGODB_URI=mongodb+srv://vishalgiri0044:kR9oUspxQUtYdund@cluster0.zdudgbg.mongodb.net/otp_bot?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=otp_bot
MONGODB_COLLECTION=users
NODE_ENV=production
APP_URL=https://your-app.vercel.app
SESSION_SECRET=your_secure_secret_here
```

## 🔍 Verification

After adding environment variables:

1. **Deploy**: `vercel --prod`
2. **Test Health**: Visit `/api/health`
3. **Check Logs**: Look for database connection success
4. **Test Dashboard**: Visit `/admin-dashboard`

## ⚠️ Important Notes

- Replace `your-app.vercel.app` with your actual Vercel domain
- Use a strong, unique `SESSION_SECRET`
- The `UPI_POSTBACK_URL` should point to your Vercel app
- Most payment settings can be left empty initially
- Database connection will be tested on first request

## 🆘 Troubleshooting

If you get database errors:
1. Check MongoDB Atlas network access (allow all IPs: 0.0.0.0/0)
2. Verify connection string format
3. Check Vercel logs for specific error messages
4. Test database connection locally first
