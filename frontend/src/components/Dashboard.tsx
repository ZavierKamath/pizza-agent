'use client'

import { useState, useEffect } from 'react'
import Header from './Header'
import CallQueuePanel from './CallQueuePanel'
import ActiveOrdersPanel from './ActiveOrdersPanel'

interface Order {
  id: number
  customer_name: string
  phone: string
  order_type: string
  address?: string
  items: any[]
  total_price: number
  status: string
  estimated_time: string
  timestamp: string
  kitchen_status: string
}

interface CallQueue {
  active_calls: number
  customers_waiting: number
}

interface DashboardData {
  call_queue: CallQueue
  active_orders: Order[]
  total_orders_today: number
}

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/dashboard')
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data')
      }
      const data = await response.json()
      setDashboardData(data)
      setError(null)
    } catch (err) {
      setError('Failed to connect to server')
      console.error('Dashboard fetch error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const markOrderComplete = async (orderId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/orders/${orderId}/complete`, {
        method: 'POST',
      })
      
      if (!response.ok) {
        throw new Error('Failed to mark order as complete')
      }
      
      // Refresh dashboard data
      await fetchDashboardData()
    } catch (err) {
      console.error('Error marking order complete:', err)
      setError('Failed to update order status')
    }
  }

  useEffect(() => {
    fetchDashboardData()
    
    // Set up auto-refresh every 5 seconds
    const interval = setInterval(fetchDashboardData, 5000)
    
    return () => clearInterval(interval)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="retro-title">Loading Kitchen Dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="pixel-card text-center">
          <div className="retro-title text-destructive mb-4">Connection Error</div>
          <p className="retro-subtitle mb-4">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="pixel-button"
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Header 
        totalOrdersToday={dashboardData?.total_orders_today || 0}
      />
      
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Call Queue Panel - takes 1 column */}
          <div className="lg:col-span-1">
            <CallQueuePanel 
              callQueue={dashboardData?.call_queue || { active_calls: 0, customers_waiting: 0 }}
            />
          </div>
          
          {/* Active Orders Panel - takes 2 columns */}
          <div className="lg:col-span-2">
            <ActiveOrdersPanel 
              orders={dashboardData?.active_orders || []}
              onMarkComplete={markOrderComplete}
            />
          </div>
        </div>
      </main>
    </div>
  )
}