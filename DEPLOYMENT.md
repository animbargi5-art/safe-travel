# 🚀 Deployment Guide - Safe Travel Flight Booking System

## Quick Local Development Setup

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- Git installed

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/safe-travel-flight-booking.git
cd safe-travel-flight-booking
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python setup_database.py

# Start backend server
python start_server.py
```

Backend will be running at: http://localhost:8000

### 3. Frontend Setup (New Terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be running at: http://localhost:5173

### 4. Access the Application
- **Main App**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:5173/admin
- **Live Monitoring**: http://localhost:5173/live-monitoring

### 5. Test User Credentials
- **Email**: test@safetravelapp.com
- **Password**: testpassword123
- **Role**: Admin (full access to all features)

## Production Deployment Options

### Option 1: Docker Deployment (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./flight_booking.db
    volumes:
      - ./backend:/app
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

Deploy:
```bash
docker-compose up -d
```

### Option 2: Cloud Deployment

#### Heroku
```bash
# Backend
heroku create safe-travel-api
git subtree push --prefix backend heroku main

# Frontend
heroku create safe-travel-app
git subtree push --prefix frontend heroku main
```

#### Vercel (Frontend)
```bash
cd frontend
vercel --prod
```

#### Railway (Backend)
```bash
cd backend
railway login
railway init
railway up
```

### Option 3: VPS Deployment

#### Ubuntu Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Node.js
sudo apt install python3 python3-pip nodejs npm -y

# Install PM2 for process management
sudo npm install -g pm2

# Clone repository
git clone https://github.com/YOUR_USERNAME/safe-travel-flight-booking.git
cd safe-travel-flight-booking

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup_database.py

# Start backend with PM2
pm2 start "python start_server.py" --name "safe-travel-api"

# Frontend setup
cd ../frontend
npm install
npm run build

# Serve frontend with PM2
pm2 serve dist 3000 --name "safe-travel-app"

# Setup Nginx reverse proxy
sudo apt install nginx -y
```

Nginx configuration (`/etc/nginx/sites-available/safe-travel`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/safe-travel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=sqlite:///./flight_booking.db
SECRET_KEY=your-super-secret-key-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
# For production:
# VITE_API_URL=https://your-api-domain.com
```

## Performance Optimization

### Backend Optimizations
- Use PostgreSQL for production instead of SQLite
- Enable Redis for caching
- Configure Gunicorn with multiple workers
- Set up database connection pooling

### Frontend Optimizations
- Enable gzip compression
- Use CDN for static assets
- Implement service worker for caching
- Optimize bundle size with code splitting

## Monitoring & Logging

### Application Monitoring
- Set up error tracking (Sentry)
- Configure performance monitoring
- Enable health check endpoints
- Set up log aggregation

### System Monitoring
- CPU and memory usage
- Database performance
- API response times
- WebSocket connection health

## Security Checklist

- [ ] HTTPS enabled with SSL certificate
- [ ] Environment variables secured
- [ ] Database credentials encrypted
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation enabled
- [ ] SQL injection protection
- [ ] XSS protection headers

## Backup Strategy

### Database Backup
```bash
# SQLite backup
cp flight_booking.db flight_booking_backup_$(date +%Y%m%d).db

# Automated daily backup
echo "0 2 * * * cp /path/to/flight_booking.db /backups/flight_booking_backup_\$(date +\%Y\%m\%d).db" | crontab -
```

### Code Backup
- GitHub repository (primary)
- Automated deployments from main branch
- Tagged releases for version control

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process on port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Database connection error**
   ```bash
   # Recreate database
   python setup_database.py
   ```

3. **Frontend build fails**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **WebSocket connection fails**
   - Check firewall settings
   - Verify proxy configuration
   - Ensure WebSocket support in load balancer

### Performance Issues

1. **Slow API responses**
   - Check database query performance
   - Enable query logging
   - Add database indexes
   - Implement caching

2. **High memory usage**
   - Monitor Python memory leaks
   - Optimize database connections
   - Implement pagination for large datasets

## Support

For deployment issues:
- Check logs: `pm2 logs` or `docker logs`
- Review error messages in browser console
- Verify environment variables
- Test API endpoints directly

---

**Your Safe Travel Flight Booking System is ready for the world! 🌍✈️**