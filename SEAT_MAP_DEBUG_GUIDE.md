# 🪑 Seat Map Debug Guide

## Issue: Seat map page at `localhost:5173/seats/2` showing blank/empty

## ✅ Backend Status: WORKING
- All APIs are functioning correctly
- Flight ID 2 exists with 180 available seats
- Authentication endpoints working
- Seat data includes all required fields (id, row, col, seat_number, seat_class, status)

## 🔍 Debugging Steps

### Step 1: Check Authentication
The seat map page requires authentication. Follow these steps:

1. **Go to** `http://localhost:5173/login`
2. **Login with:**
   - Email: `test@safetravelapp.com`
   - Password: `testpass123`
3. **After login**, navigate to `http://localhost:5173/seats/2`

### Step 2: Check Browser Console
1. **Open browser developer tools** (F12)
2. **Go to Console tab**
3. **Look for any JavaScript errors** (red text)
4. **Common errors to look for:**
   - Network errors (failed to fetch)
   - Authentication errors (401 Unauthorized)
   - Component rendering errors

### Step 3: Check Network Tab
1. **Open browser developer tools** (F12)
2. **Go to Network tab**
3. **Refresh the seats page**
4. **Check if these API calls are made:**
   - `GET /seats/available/2` - should return 200 with seat data
   - `GET /booking/allocation-options/2` - should return 200 with options
5. **If API calls fail:**
   - Check if they return 401 (authentication required)
   - Check if they return 404 (not found)
   - Check response data for error messages

### Step 4: Test Direct API Access
Open a new browser tab and test these URLs directly:
- `http://localhost:8000/seats/available/2` - should show JSON with 180 seats
- `http://localhost:8000/booking/allocation-options/2` - should show allocation options

### Step 5: Check Authentication State
1. **Open browser developer tools** (F12)
2. **Go to Application/Storage tab**
3. **Check Local Storage** for `token` key
4. **If no token exists**, you need to login first

## 🚀 Quick Test Flow

1. **Start fresh:**
   ```bash
   # Clear browser cache and local storage
   # Or use incognito/private browsing mode
   ```

2. **Login first:**
   - Go to `http://localhost:5173/login`
   - Use: `test@safetravelapp.com` / `testpass123`
   - Verify you see user menu in header (not Sign In/Sign Up buttons)

3. **Then access seats:**
   - Go to `http://localhost:5173/seats/2`
   - Should show seat selection interface

## 🔧 Expected Behavior

When working correctly, the seats page should show:
- ✈️ Auto-allocation section at the top
- 🤖 ML recommendations section
- 🗺️ Manual seat map (when expanded)
- 🪑 Grid of seats with colors:
  - Green: Available
  - Red: Unavailable/Booked
  - Yellow: Selected

## 📊 Backend Test Results

All backend APIs tested successfully:
- ✅ Login: Working
- ✅ Auth verification: Working  
- ✅ Seats API: Returns 180 seats
- ✅ Allocation options: Working
- ✅ Flight ID 2: Exists (Delhi → Lucknow)

## 🆘 If Still Not Working

If the page is still blank after following all steps:

1. **Check browser console** for specific error messages
2. **Try a different flight ID**: `http://localhost:5173/seats/1`
3. **Try different browser** or incognito mode
4. **Restart frontend server**:
   ```bash
   cd frontend
   npm run dev
   ```

## 📞 Next Steps

If you're still seeing a blank page, please:
1. Share any console error messages
2. Confirm you can login successfully
3. Let me know what you see in the Network tab when accessing the seats page

The backend is confirmed working, so this is likely a frontend authentication or rendering issue.