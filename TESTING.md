# Flight Booking System - Testing Guide

## 🧪 Testing Overview

Our flight booking system includes comprehensive testing at multiple levels:
- **Unit Tests** - Individual component and function testing
- **Integration Tests** - Complete workflow testing
- **Frontend Tests** - React component and context testing
- **API Tests** - Backend endpoint testing
- **Dharma Tests** - Business rule validation

## 🏗️ Test Architecture

### Backend Testing Stack
- **pytest** - Test framework
- **FastAPI TestClient** - API testing
- **SQLAlchemy** - In-memory database for tests
- **pytest-cov** - Coverage reporting
- **faker** - Test data generation

### Frontend Testing Stack
- **Vitest** - Test framework (Vite-native)
- **React Testing Library** - Component testing
- **MSW (Mock Service Worker)** - API mocking
- **jsdom** - DOM environment for tests

## 🚀 Running Tests

### Backend Tests

```bash
# Install test dependencies
cd backend
pip install -r requirements-test.txt

# Run all tests
python test_runner.py

# Run specific test file
python test_runner.py tests/test_auth.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Frontend Tests

```bash
# Install dependencies
cd frontend
npm install

# Run all tests
npm run test

# Run tests with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test
npm run test -- Login.test.jsx
```

## 📋 Test Categories

### 1. Authentication Tests (`test_auth.py`)
- User registration validation
- Login/logout functionality
- JWT token handling
- Password security
- User preferences management

**Key Test Cases:**
- ✅ Successful user registration
- ✅ Duplicate email/username handling
- ✅ Login with correct/incorrect credentials
- ✅ Token-based authentication
- ✅ User preference updates

### 2. Booking System Tests (`test_booking.py`)
- Seat holding and confirmation
- Booking status transitions
- User authorization
- Booking retrieval

**Key Test Cases:**
- ✅ Hold available seat
- ✅ Prevent double booking
- ✅ Confirm held booking
- ✅ Retrieve user bookings
- ✅ Authorization checks

### 3. Auto-Allocation Tests (`test_auto_allocation.py`)
- Seat scoring algorithm
- Position detection (window/aisle/middle)
- Allocation strategies
- Preference handling

**Key Test Cases:**
- ✅ Seat position type detection
- ✅ Scoring algorithm accuracy
- ✅ Best available strategy
- ✅ Class and position preferences
- ✅ Different allocation strategies
- ✅ No available seats handling

### 4. Dharma Tests (`test_dharma.py`)
- Business rule enforcement
- Valid/invalid state transitions
- Booking integrity

**Key Test Cases:**
- ✅ Valid transitions (HOLD → CONFIRMED)
- ✅ Invalid transitions (CONFIRMED → HOLD)
- ✅ Dharma violation messages
- ✅ State machine integrity

### 5. Integration Tests (`test_integration.py`)
- Complete booking workflows
- Multi-user scenarios
- Concurrent booking attempts
- User preference integration

**Key Test Cases:**
- ✅ End-to-end booking flow
- ✅ Booking expiry process
- ✅ Concurrent seat booking
- ✅ User preferences in auto-allocation

### 6. Frontend Component Tests
- React component rendering
- User interactions
- Context state management
- API integration

**Key Test Cases:**
- ✅ Login form validation
- ✅ Auto-allocation component
- ✅ Authentication context
- ✅ Booking flow components

## 📊 Test Coverage Goals

### Backend Coverage Targets
- **Overall Coverage**: 80%+
- **Critical Paths**: 95%+
- **Business Logic**: 90%+
- **API Endpoints**: 85%+

### Frontend Coverage Targets
- **Components**: 80%+
- **Context/Hooks**: 90%+
- **Utils/Services**: 85%+
- **Critical User Flows**: 95%+

## 🔧 Test Configuration

### Backend Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
addopts = 
    -v
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

### Frontend Configuration (`vitest.config.js`)
```javascript
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    coverage: {
      reporter: ['text', 'json', 'html'],
    },
  },
})
```

## 🎯 Test Data Management

### Backend Test Fixtures
- **test_user** - Authenticated user with preferences
- **test_aircraft** - Sample aircraft with seats
- **test_flight** - Flight for booking tests
- **test_seats** - Variety of seat types and classes
- **auth_headers** - Authentication headers for API calls

### Frontend Test Mocks
- **MSW handlers** - API response mocking
- **Mock user data** - Consistent test user
- **Mock booking data** - Sample booking scenarios
- **Provider wrappers** - Context providers for components

## 🚨 Test Best Practices

### Backend Testing
1. **Isolation** - Each test uses fresh database
2. **Realistic Data** - Use representative test data
3. **Error Cases** - Test both success and failure paths
4. **Security** - Verify authentication and authorization
5. **Performance** - Test with reasonable data volumes

### Frontend Testing
1. **User-Centric** - Test from user perspective
2. **Accessibility** - Use semantic queries
3. **Async Handling** - Proper async/await patterns
4. **Mock External** - Mock API calls and external services
5. **Component Isolation** - Test components independently

## 🐛 Debugging Tests

### Backend Debugging
```bash
# Run with verbose output
pytest -v -s

# Run single test with debugging
pytest tests/test_auth.py::test_login_success -v -s

# Debug with pdb
pytest --pdb tests/test_auth.py::test_login_success
```

### Frontend Debugging
```bash
# Run with debug output
npm run test -- --reporter=verbose

# Run single test
npm run test -- Login.test.jsx

# Debug in browser
npm run test:ui
```

## 📈 Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backend Tests
        run: |
          cd backend
          python test_runner.py
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm ci
          npm run test:coverage
```

## 🎉 Test Results

### Sample Test Output
```
🧪 Running Flight Booking System Tests
==================================================
📦 Installing test dependencies...
🔬 Running tests...

tests/test_auth.py ✅ 8 passed
tests/test_booking.py ✅ 6 passed  
tests/test_auto_allocation.py ✅ 10 passed
tests/test_dharma.py ✅ 7 passed
tests/test_integration.py ✅ 4 passed

Coverage: 87% (target: 80%)
✅ All tests passed!
📊 Coverage report generated in htmlcov/index.html
```

## 🔮 Future Testing Enhancements

- **Load Testing** - Performance under high concurrent users
- **Security Testing** - Penetration testing and vulnerability scans
- **E2E Testing** - Full browser automation with Playwright
- **Visual Testing** - Screenshot comparison testing
- **API Contract Testing** - OpenAPI specification validation
- **Chaos Engineering** - Fault injection and resilience testing

---

**Testing Philosophy**: "Test with dharma - ensure every path serves the user's journey with reliability and grace."