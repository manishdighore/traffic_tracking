'use client'

import { useState } from 'react'
import { VideoFeed } from '@/components/VideoFeed'
import { Dashboard } from '@/components/Dashboard'
import { VehicleHistory } from '@/components/VehicleHistory'
import { Header } from '@/components/Header'
import { Activity, BarChart3, History } from 'lucide-react'

type Tab = 'live' | 'dashboard' | 'history'

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('live')

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Header />
      
      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex space-x-1 rounded-xl bg-gray-800/50 p-1 backdrop-blur-sm">
          <button
            onClick={() => setActiveTab('live')}
            className={`flex-1 flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-medium transition-all ${
              activeTab === 'live'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
            }`}
          >
            <Activity className="w-4 h-4" />
            Live Feed
          </button>
          
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex-1 flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-medium transition-all ${
              activeTab === 'dashboard'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            Dashboard
          </button>
          
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-medium transition-all ${
              activeTab === 'history'
                ? 'bg-primary-600 text-white shadow-lg'
                : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
            }`}
          >
            <History className="w-4 h-4" />
            History
          </button>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {activeTab === 'live' && <VideoFeed />}
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'history' && <VehicleHistory />}
      </main>
    </div>
  )
}
