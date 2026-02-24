import { http, HttpResponse } from 'msw'

const API_BASE = 'http://127.0.0.1:8000'

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/auth/register`, () => {
    return HttpResponse.json({
      access_token: 'mock-token',
      token_type: 'bearer',
      user: {
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
        last_login: null
      }
    })
  }),

  http.post(`${API_BASE}/auth/login`, () => {
    return HttpResponse.json({
      access_token: 'mock-token',
      token_type: 'bearer',
      user: {
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
    })
  }),

  http.get(`${API_BASE}/auth/me`, () => {
    return HttpResponse.json({
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
    })
  }),

  // Booking endpoints
  http.get(`${API_BASE}/booking/my-bookings`, () => {
    return HttpResponse.json([
      {
        id: 1,
        user_id: 1,
        flight_id: 1,
        seat_id: 1,
        passenger_name: 'Test User',
        passenger_email: 'test@example.com',
        passenger_phone: '+1234567890',
        price: 299.99,
        status: 'CONFIRMED',
        created_at: '2024-01-01T00:00:00Z',
        expires_at: null,
        flight: {
          id: 1,
          from_city: 'Mumbai',
          to_city: 'Delhi',
          departure_time: '2024-01-02T10:30:00Z',
          arrival_time: '2024-01-02T12:30:00Z',
          price: 299.99
        },
        seat: {
          id: 1,
          seat_number: '12A',
          seat_class: 'ECONOMY',
          row: 12,
          col: 'A'
        }
      }
    ])
  }),

  http.post(`${API_BASE}/booking/hold`, () => {
    return HttpResponse.json({
      id: 1,
      user_id: 1,
      flight_id: 1,
      seat_id: 1,
      status: 'HOLD',
      created_at: '2024-01-01T00:00:00Z',
      expires_at: '2024-01-01T00:10:00Z'
    })
  }),

  http.post(`${API_BASE}/booking/auto-allocate`, () => {
    return HttpResponse.json({
      booking: {
        id: 1,
        user_id: 1,
        flight_id: 1,
        seat_id: 1,
        status: 'HOLD',
        created_at: '2024-01-01T00:00:00Z',
        expires_at: '2024-01-01T00:10:00Z'
      },
      seat: {
        id: 1,
        seat_number: '12A',
        seat_class: 'ECONOMY',
        row: 12,
        col: 'A'
      },
      allocation_reason: 'Auto-allocated using BEST_AVAILABLE strategy with WINDOW preference'
    })
  }),

  http.get(`${API_BASE}/booking/allocation-options/:flightId`, () => {
    return HttpResponse.json({
      total_available: 150,
      by_class: {
        'FIRST': 12,
        'BUSINESS': 24,
        'ECONOMY': 114
      },
      by_position: {
        'WINDOW': 50,
        'AISLE': 50,
        'MIDDLE': 50
      },
      recommendations: [
        {
          type: 'best_overall',
          seat: {
            id: 1,
            seat_number: '1A',
            seat_class: 'FIRST',
            position: 'WINDOW'
          },
          description: 'Best available seat overall'
        }
      ]
    })
  }),

  // Seats endpoints
  http.get(`${API_BASE}/seats/available/:flightId`, () => {
    return HttpResponse.json([
      {
        id: 1,
        seat_number: '12A',
        seat_class: 'ECONOMY',
        row: 12,
        col: 'A',
        status: 'AVAILABLE'
      },
      {
        id: 2,
        seat_number: '12B',
        seat_class: 'ECONOMY',
        row: 12,
        col: 'B',
        status: 'AVAILABLE'
      }
    ])
  })
]