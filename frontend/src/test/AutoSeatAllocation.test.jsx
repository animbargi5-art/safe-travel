import { describe, it, expect, vi } from 'vitest'
import { screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from './utils'
import AutoSeatAllocation from '../components/AutoSeatAllocation'

const mockAllocationOptions = {
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
    },
    {
      type: 'best_window',
      seat: {
        id: 2,
        seat_number: '12A',
        seat_class: 'ECONOMY',
        position: 'WINDOW'
      },
      description: 'Best window seat'
    }
  ]
}

describe('AutoSeatAllocation Component', () => {
  const mockOnAutoAllocate = vi.fn()

  beforeEach(() => {
    mockOnAutoAllocate.mockClear()
  })

  it('renders allocation options', () => {
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    expect(screen.getByText('Smart Seat Selection')).toBeInTheDocument()
    expect(screen.getByText('150 seats available')).toBeInTheDocument()
    expect(screen.getByText('Best Available')).toBeInTheDocument()
    expect(screen.getByText('Window Seat')).toBeInTheDocument()
    expect(screen.getByText('Aisle Seat')).toBeInTheDocument()
  })

  it('shows statistics correctly', () => {
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    expect(screen.getByText('50')).toBeInTheDocument() // Window count
    expect(screen.getByText('24')).toBeInTheDocument() // Business count
    expect(screen.getByText('12')).toBeInTheDocument() // First count
  })

  it('displays AI recommendations', () => {
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    expect(screen.getByText('AI Recommendations')).toBeInTheDocument()
    expect(screen.getByText('Seat 1A')).toBeInTheDocument()
    expect(screen.getByText('Best available seat overall')).toBeInTheDocument()
    expect(screen.getByText('Seat 12A')).toBeInTheDocument()
    expect(screen.getByText('Best window seat')).toBeInTheDocument()
  })

  it('calls onAutoAllocate when best available is clicked', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    const bestAvailableButton = screen.getByText('Best Available').closest('button')
    await user.click(bestAvailableButton)
    
    expect(mockOnAutoAllocate).toHaveBeenCalledWith('ANY', 'ECONOMY')
  })

  it('calls onAutoAllocate when window seat is clicked', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    const windowButton = screen.getByText('Window Seat').closest('button')
    await user.click(windowButton)
    
    expect(mockOnAutoAllocate).toHaveBeenCalledWith('WINDOW', 'ECONOMY')
  })

  it('calls onAutoAllocate when aisle seat is clicked', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    const aisleButton = screen.getByText('Aisle Seat').closest('button')
    await user.click(aisleButton)
    
    expect(mockOnAutoAllocate).toHaveBeenCalledWith('AISLE', 'ECONOMY')
  })

  it('shows advanced options when toggled', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    const advancedToggle = screen.getByText('Advanced Options')
    await user.click(advancedToggle)
    
    expect(screen.getByText('Seat Class')).toBeInTheDocument()
    expect(screen.getByText('Position Preference')).toBeInTheDocument()
    expect(screen.getByText('Strategy')).toBeInTheDocument()
  })

  it('disables buttons when loading', () => {
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={true}
      />
    )
    
    const bestAvailableButton = screen.getByText('Best Available').closest('button')
    expect(bestAvailableButton).toBeDisabled()
  })

  it('displays dharma message', () => {
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    expect(screen.getByText(/the right seat appears when the intention is clear/i)).toBeInTheDocument()
  })

  it('handles recommendation clicks', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <AutoSeatAllocation
        allocationOptions={mockAllocationOptions}
        onAutoAllocate={mockOnAutoAllocate}
        isLoading={false}
      />
    )
    
    const recommendationButton = screen.getByText('Seat 1A').closest('button')
    await user.click(recommendationButton)
    
    expect(mockOnAutoAllocate).toHaveBeenCalledWith('WINDOW', 'FIRST')
  })
})