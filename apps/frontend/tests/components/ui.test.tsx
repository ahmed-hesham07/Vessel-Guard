import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { jest } from '@jest/globals'
import '@testing-library/jest-dom'
import { Button } from '@/components/ui/button'
import { Loading } from '@/components/ui/loading'

describe('Button Component', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })

  it('handles click events', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies variant styles correctly', () => {
    render(<Button variant="destructive">Delete</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-destructive')
  })

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})

describe('Loading Component', () => {
  it('shows loading state when loading is true', () => {
    render(<Loading loading={true}>Submit</Loading>)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('shows normal state when loading is false', () => {
    render(<Loading loading={false}>Submit</Loading>)
    expect(screen.getByText('Submit')).toBeInTheDocument()
    expect(screen.getByRole('button')).not.toBeDisabled()
  })

  it('shows custom loading text', () => {
    render(<Loading loading={true} loadingText="Processing...">Submit</Loading>)
    expect(screen.getByText('Processing...')).toBeInTheDocument()
  })
})
