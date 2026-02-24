import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../context/AuthContext'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

describe('AuthContext', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
  })

  it('should initialize with no user', () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    })

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('should login successfully', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    })

    await act(async () => {
      const loginResult = await result.current.login('test@example.com', 'password')
      expect(loginResult.success).toBe(true)
    })

    await waitFor(() => {
      expect(result.current.user).toBeTruthy()
      expect(result.current.isAuthenticated).toBe(true)
    })

    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'mock-token')
  })

  it('should register successfully', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    })

    const userData = {
      email: 'test@example.com',
      username: 'testuser',
      full_name: 'Test User',
      password: 'password123'
    }

    await act(async () => {
      const registerResult = await result.current.register(userData)
      expect(registerResult.success).toBe(true)
    })

    await waitFor(() => {
      expect(result.current.user).toBeTruthy()
      expect(result.current.isAuthenticated).toBe(true)
    })

    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'mock-token')
  })

  it('should logout successfully', async () => {
    localStorageMock.getItem.mockReturnValue('mock-token')
    
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    })

    // Wait for initial auth check
    await waitFor(() => {
      expect(result.current.user).toBeTruthy()
    })

    act(() => {
      result.current.logout()
    })

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
  })

  it('should update preferences', async () => {
    localStorageMock.getItem.mockReturnValue('mock-token')
    
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    })

    // Wait for initial auth check
    await waitFor(() => {
      expect(result.current.user).toBeTruthy()
    })

    const preferences = {
      preferred_seat_class: 'BUSINESS',
      preferred_seat_position: 'AISLE'
    }

    await act(async () => {
      const updateResult = await result.current.updatePreferences(preferences)
      expect(updateResult.success).toBe(true)
    })

    // Note: In a real test, you'd mock the API response to return updated user data
  })
})