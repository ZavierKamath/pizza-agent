'use client'

import { Clock, MapPin, Phone, Check } from 'lucide-react'

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

interface ActiveOrdersPanelProps {
  orders: Order[]
  onMarkComplete: (orderId: number) => void
}

export default function ActiveOrdersPanel({ orders, onMarkComplete }: ActiveOrdersPanelProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getTimeElapsed = (timestamp: string) => {
    const now = new Date()
    const orderTime = new Date(timestamp)
    const diffMinutes = Math.floor((now.getTime() - orderTime.getTime()) / (1000 * 60))
    return diffMinutes
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-accent text-accent-foreground'
      case 'in_preparation':
        return 'bg-primary text-primary-foreground'
      case 'ready':
        return 'bg-secondary text-secondary-foreground'
      default:
        return 'bg-muted text-muted-foreground'
    }
  }

  const getItemsSummary = (items: any[]) => {
    const summary = items.slice(0, 2).map(item => {
      if (item.type === 'pizza') {
        return `${item.quantity}x ${item.name}`
      }
      return `${item.quantity}x ${item.name}`
    })
    
    if (items.length > 2) {
      summary.push(`+${items.length - 2} more`)
    }
    
    return summary.join(', ')
  }

  return (
    <div className="space-y-6">
      {/* Panel Title */}
      <div className="pixel-card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="retro-title">ACTIVE ORDERS</h2>
          <div className="retro-subtitle">
            {orders.length} order{orders.length !== 1 ? 's' : ''} pending
          </div>
        </div>

        {/* Orders Grid */}
        {orders.length === 0 ? (
          <div className="pixel-card bg-muted text-center py-12">
            <div className="retro-subtitle text-muted-foreground">
              No orders need preparation
            </div>
            <div className="font-pixel text-xs text-muted-foreground mt-2">
              All caught up! 🍕
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            {orders.map((order) => {
              const timeElapsed = getTimeElapsed(order.timestamp)
              const isUrgent = timeElapsed > 20

              return (
                <div 
                  key={order.id} 
                  className={`pixel-card relative ${isUrgent ? 'bg-destructive text-destructive-foreground animate-pulse' : 'bg-card'}`}
                >
                  {/* Order Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="font-pixel text-lg">
                        #{order.id.toString().padStart(3, '0')}
                      </div>
                      <div className={`px-2 py-1 pixel-border text-xs font-pixel uppercase ${getStatusColor(order.kitchen_status)}`}>
                        {order.kitchen_status.replace('_', ' ')}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-pixel text-xs">
                        {formatTime(order.timestamp)}
                      </div>
                      <div className={`font-pixel text-xs ${isUrgent ? 'text-secondary' : 'text-muted-foreground'}`}>
                        {timeElapsed}m ago
                      </div>
                    </div>
                  </div>

                  {/* Customer Info */}
                  <div className="mb-3">
                    <div className="font-pixel text-sm font-bold">
                      {order.customer_name}
                    </div>
                    <div className="flex items-center space-x-4 mt-1">
                      <div className="flex items-center space-x-1 text-xs">
                        <Phone size={12} />
                        <span className="font-pixel">{order.phone}</span>
                      </div>
                      {order.order_type === 'delivery' && order.address && (
                        <div className="flex items-center space-x-1 text-xs">
                          <MapPin size={12} />
                          <span className="font-pixel truncate max-w-32">
                            {order.address}
                          </span>
                        </div>
                      )}
                      {order.order_type === 'pickup' && (
                        <div className="pixel-border px-2 py-1 text-xs font-pixel bg-secondary text-secondary-foreground">
                          PICKUP
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Items Summary */}
                  <div className="mb-3">
                    <div className="font-pixel text-xs text-muted-foreground uppercase">
                      Items:
                    </div>
                    <div className="font-pixel text-xs mt-1">
                      {getItemsSummary(order.items)}
                    </div>
                  </div>

                  {/* Order Details */}
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-pixel text-sm">
                        ${order.total_price.toFixed(2)}
                      </div>
                      <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                        <Clock size={12} />
                        <span className="font-pixel">{order.estimated_time}</span>
                      </div>
                    </div>

                    {/* Complete Button */}
                    <button
                      onClick={() => onMarkComplete(order.id)}
                      className="pixel-button bg-primary text-primary-foreground hover:bg-primary/90 flex items-center space-x-2"
                    >
                      <Check size={16} />
                      <span>COMPLETE</span>
                    </button>
                  </div>

                  {/* Urgent Indicator */}
                  {isUrgent && (
                    <div className="absolute top-2 right-2">
                      <div className="w-3 h-3 bg-secondary rounded-full animate-ping"></div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="pixel-card bg-muted">
        <h3 className="retro-subtitle mb-3">STATUS LEGEND</h3>
        <div className="grid grid-cols-2 gap-3 font-pixel text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-accent pixel-border"></div>
            <span>Pending</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-primary pixel-border"></div>
            <span>In Preparation</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-secondary pixel-border"></div>
            <span>Ready</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-destructive pixel-border"></div>
            <span>Urgent (20m+)</span>
          </div>
        </div>
      </div>
    </div>
  )
}