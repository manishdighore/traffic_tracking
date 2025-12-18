'use client'

import { useQuery } from '@tanstack/react-query'
import { Car, Clock, Gauge, Palette, Trash2 } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

interface Vehicle {
  id: number
  vehicle_type: string
  color: string
  speed: number | null
  direction: string | null
  size: string | null
  confidence: number
  detected_at: string
}

export function VehicleHistory() {
  const { data: vehicles, isLoading, refetch } = useQuery<Vehicle[]>({
    queryKey: ['vehicles'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/vehicles?limit=50`)
      return response.data
    },
    refetchInterval: 5000,
  })

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`${API_URL}/api/vehicles/${id}`)
      refetch()
    } catch (error) {
      console.error('Error deleting vehicle:', error)
    }
  }

  const handleClearAll = async () => {
    if (confirm('Are you sure you want to clear all data?')) {
      try {
        await axios.post(`${API_URL}/api/clear-data`)
        refetch()
      } catch (error) {
        console.error('Error clearing data:', error)
      }
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-400">Loading history...</div>
      </div>
    )
  }

  if (!vehicles || vehicles.length === 0) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-12 border border-gray-700 text-center">
        <Car className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">No Vehicles Detected Yet</h3>
        <p className="text-gray-400">Start the camera feed to begin tracking vehicles</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">
          Vehicle History <span className="text-gray-400 text-lg">({vehicles.length})</span>
        </h2>
        <button
          onClick={handleClearAll}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Clear All
        </button>
      </div>

      {/* Vehicle Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {vehicles.map((vehicle) => (
          <div
            key={vehicle.id}
            className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-5 border border-gray-700 hover:border-primary-500 transition-all group"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary-500/10 group-hover:bg-primary-500/20 transition-colors">
                  <Car className="w-6 h-6 text-primary-400" />
                </div>
                <div>
                  <h3 className="font-bold text-white capitalize">
                    {vehicle.vehicle_type}
                  </h3>
                  <p className="text-xs text-gray-400">ID: {vehicle.id}</p>
                </div>
              </div>
              <button
                onClick={() => handleDelete(vehicle.id)}
                className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-all"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            {/* Details */}
            <div className="space-y-2.5">
              <div className="flex items-center gap-2 text-sm">
                <Palette className="w-4 h-4 text-gray-400" />
                <span className="text-gray-400">Color:</span>
                <span className="text-white capitalize font-medium">
                  {vehicle.color}
                </span>
              </div>

              {vehicle.speed !== null && (
                <div className="flex items-center gap-2 text-sm">
                  <Gauge className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-400">Speed:</span>
                  <span className="text-green-400 font-mono font-medium">
                    {vehicle.speed} km/h
                  </span>
                </div>
              )}

              {vehicle.direction && (
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-4 h-4 flex items-center justify-center">
                    <div className={`w-0 h-0 border-l-4 border-r-4 border-b-4 border-l-transparent border-r-transparent border-b-gray-400 ${
                      vehicle.direction === 'down' ? '' :
                      vehicle.direction === 'up' ? 'rotate-180' :
                      vehicle.direction === 'left' ? 'rotate-90' :
                      '-rotate-90'
                    }`} />
                  </div>
                  <span className="text-gray-400">Direction:</span>
                  <span className="text-blue-400 capitalize font-medium">
                    {vehicle.direction}
                  </span>
                </div>
              )}

              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="text-gray-400">Detected:</span>
                <span className="text-gray-300 text-xs">
                  {new Date(vehicle.detected_at).toLocaleString()}
                </span>
              </div>

              {/* Confidence Badge */}
              <div className="pt-2 flex items-center gap-2">
                <span className="text-xs text-gray-400">Confidence:</span>
                <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary-500 to-green-500"
                    style={{ width: `${vehicle.confidence * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-300 font-mono">
                  {(vehicle.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
