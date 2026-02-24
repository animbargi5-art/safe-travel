# Safe Travel Frontend - Startup Guide

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation & Startup
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: **http://localhost:5173**

## 🌟 Available Features

### Core Pages
- **Home** (`/`) - Landing page with flight search
- **Flight Search** (`/flights`) - Advanced flight search with filters
- **Seat Selection** (`/seats/:flightId`) - AI-powered seat allocation
- **Payment** (`/payment`) - Secure Stripe payment processing
- **Bookings** (`/bookings`) - User booking history

### Advanced Features
- **Admin Dashboard** (`/admin`) - System overview and management
- **Group Bookings** (`/group-booking`) - Multi-passenger bookings
- **User Insights** (`/insights`) - ML-powered user analytics
- **Business Intelligence** (`/business-intelligence`) - Executive dashboard
- **Real-time Demo** (`/realtime-demo`) - WebSocket notifications demo
- **Payment Dashboard** (`/payment-dashboard`) - Payment analytics

### Components
- **NotificationCenter** - Real-time notifications with WebSocket
- **PaymentAnalytics** - Advanced payment insights
- **BusinessIntelligenceDashboard** - Executive BI dashboard
- **MLRecommendations** - AI-powered recommendations
- **RealTimeBookingStatus** - Live booking status updates

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# Stripe Configuration
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key

# WebSocket URL
VITE_WS_URL=ws://localhost:8000
```

### Backend Integration
The frontend expects the backend to be running on `http://localhost:8000`

## 🧪 Testing Features

### 1. Basic Booking Flow
1. Go to `/flights`
2. Search for flights
3. Select a flight
4. Choose seat (try AI allocation)
5. Enter passenger details
6. Complete payment (use test card: 4242 4242 4242 4242)

### 2. Real-time Notifications
1. Go to `/realtime-demo`
2. Click "Send Test Notification"
3. Watch for real-time updates in notification center

### 3. Admin Features
1. Go to `/admin`
2. View system statistics
3. Manage bookings and users

### 4. Business Intelligence
1. Go to `/business-intelligence`
2. Explore revenue analytics
3. View customer insights
4. Check predictive analytics

### 5. Group Bookings
1. Go to `/group-booking`
2. Add multiple passengers
3. See intelligent seat allocation for groups

## 🔗 API Integration

### Authentication
- Login/Register through `/auth/login` and `/auth/register`
- JWT tokens stored in localStorage
- Automatic token refresh

### WebSocket Connection
- Real-time notifications via WebSocket
- Automatic reconnection handling
- Connection status indicators

### Payment Processing
- Stripe Elements integration
- Real-time payment status updates
- Secure payment intent flow

## 🎨 UI/UX Features

### Design System
- Tailwind CSS for styling
- Framer Motion for animations
- Responsive design for all devices
- Dharma-aligned messaging throughout

### Interactive Elements
- Real-time charts and graphs
- Dynamic data visualization
- Live status indicators
- Smooth page transitions

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend is running on port 8000
   - Check CORS configuration in backend

2. **WebSocket Connection Failed**
   - Verify WebSocket URL in environment
   - Check authentication token

3. **Payment Issues**
   - Use Stripe test keys
   - Test card: 4242 4242 4242 4242

4. **API Errors**
   - Check backend server status
   - Verify API endpoints are available

### Development Tools
- React Developer Tools
- Redux DevTools (if using Redux)
- Network tab for API debugging
- Console for WebSocket messages

## 📱 Mobile Testing

The app is fully responsive. Test on:
- Mobile browsers (Chrome, Safari)
- Tablet devices
- Different screen sizes

## 🚀 Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎯 Key Testing Scenarios

1. **Complete Booking Flow** - End-to-end booking process
2. **Real-time Updates** - WebSocket notifications
3. **Payment Processing** - Stripe integration
4. **Admin Functions** - Dashboard and management
5. **Mobile Experience** - Responsive design
6. **Performance** - Loading times and responsiveness

---

**Ready to test? Start the backend first, then run `npm run dev`!** 🚀