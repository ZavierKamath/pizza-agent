'use client'

import { Clock } from 'lucide-react'
import { useState, useEffect } from 'react'

interface HeaderProps {
  totalOrdersToday: number
}

export default function Header({ totalOrdersToday }: HeaderProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <header className="pixel-border bg-primary text-primary-foreground p-6">
      <div className="container mx-auto flex items-center justify-between">
        {/* Main Title */}
        <div className="flex items-center space-x-4">
          <div className="retro-title text-white">
            🍕 ZAVIER'S PIZZA
          </div>
          <div className="retro-subtitle text-secondary">
            KITCHEN DASHBOARD
          </div>
        </div>

        {/* Stats and Time */}
        <div className="flex items-center space-x-8">
          {/* Orders Counter */}
          <div className="pixel-card bg-secondary text-secondary-foreground">
            <div className="text-xs font-pixel uppercase tracking-wider">
              Orders Today
            </div>
            <div className="text-2xl font-pixel text-center mt-1">
              {totalOrdersToday.toString().padStart(3, '0')}
            </div>
          </div>

          {/* Current Time */}
          <div className="pixel-card bg-accent text-accent-foreground">
            <div className="flex items-center space-x-2">
              <Clock size={16} />
              <div className="font-pixel text-lg">
                {formatTime(currentTime)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}