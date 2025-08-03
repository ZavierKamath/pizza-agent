'use client'

import { Phone, Users } from 'lucide-react'

interface CallQueue {
  active_calls: number
  customers_waiting: number
}

interface CallQueuePanelProps {
  callQueue: CallQueue
}

export default function CallQueuePanel({ callQueue }: CallQueuePanelProps) {
  const totalInQueue = callQueue.active_calls + callQueue.customers_waiting

  return (
    <div className="space-y-6">
      {/* Panel Title */}
      <div className="pixel-card">
        <h2 className="retro-title mb-4">CALL QUEUE</h2>
        
        {/* Active Calls */}
        <div className="pixel-card bg-primary text-primary-foreground mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Phone size={24} />
              <div>
                <div className="font-pixel text-sm">ACTIVE CALLS</div>
                <div className="font-pixel text-2xl">
                  {callQueue.active_calls.toString().padStart(2, '0')}
                </div>
              </div>
            </div>
            {callQueue.active_calls > 0 && (
              <div className="w-4 h-4 bg-secondary rounded-full animate-pulse"></div>
            )}
          </div>
        </div>

        {/* Customers Waiting */}
        <div className="pixel-card bg-accent text-accent-foreground mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Users size={24} />
              <div>
                <div className="font-pixel text-sm">WAITING</div>
                <div className="font-pixel text-2xl">
                  {callQueue.customers_waiting.toString().padStart(2, '0')}
                </div>
              </div>
            </div>
            {callQueue.customers_waiting > 0 && (
              <div className="w-4 h-4 bg-secondary rounded-full animate-pulse"></div>
            )}
          </div>
        </div>

        {/* Total Queue Summary */}
        <div className="pixel-card bg-secondary text-secondary-foreground">
          <div className="text-center">
            <div className="font-pixel text-sm uppercase tracking-wider">
              Total in Queue
            </div>
            <div className="font-pixel text-3xl mt-2">
              {totalInQueue.toString().padStart(2, '0')}
            </div>
          </div>
        </div>

        {/* Queue Status Indicator */}
        <div className="mt-4 text-center">
          {totalInQueue === 0 && (
            <div className="retro-subtitle text-muted-foreground">
              No customers in queue
            </div>
          )}
          {totalInQueue > 0 && totalInQueue <= 3 && (
            <div className="retro-subtitle text-primary">
              Normal queue level
            </div>
          )}
          {totalInQueue > 3 && totalInQueue <= 6 && (
            <div className="retro-subtitle text-accent">
              Busy period
            </div>
          )}
          {totalInQueue > 6 && (
            <div className="retro-subtitle text-destructive animate-pulse">
              High volume!
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="pixel-card bg-muted">
        <h3 className="retro-subtitle mb-3">INSTRUCTIONS</h3>
        <ul className="font-pixel text-xs space-y-2 text-muted-foreground">
          <li>• Monitor queue levels</li>
          <li>• Prepare for rush periods</li>
          <li>• Complete orders efficiently</li>
          <li>• Keep customers happy!</li>
        </ul>
      </div>
    </div>
  )
}