import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import { BookingProvider } from '../context/BookingContext'

// Custom render function that includes providers
export function renderWithProviders(ui, options = {}) {
  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        <AuthProvider>
          <BookingProvider>
            {children}
          </BookingProvider>
        </AuthProvider>
      </BrowserRouter>
    )
  }

  return render(ui, { wrapper: Wrapper, ...options })
}

// Mock user for testing
export const mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  full_name: 'Test User',
  phone: '+1234567890',
  is_active: true,
  is_verified: true,
  preferred_seat_class: 'ECONOMY',
  preferred_seat_position: 'WINDOW',
  created_at: '2024-01-01T00:00:00Z',
  last_login: '2024-01-01T12:00:00Z'
}

// Mock booking data
export const mockBookingData = {
  flight: {
    id: 1,
    from_city: 'Mumbai',
    to_city: 'Delhi',
    departure_time: '2024-01-02T10:30:00Z',
    price: 299.99
  },
  seat: {
    id: 1,
    seat_number: '12A',
    seat_class: 'ECONOMY',
    row: 12,
    col: 'A'
  },
  booking: {
    id: 1,
    status: 'HOLD',
    expires_at: '2024-01-01T00:10:00Z'
  },
  passenger: {
    passenger_name: 'Test User',
    passenger_email: 'test@example.com',
    passenger_phone: '+1234567890'
  }
}