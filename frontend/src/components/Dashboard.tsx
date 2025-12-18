'use client'

import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { Car, Gauge, Palette, TrendingUp } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/stats`)
      return response.data
    },
    refetchInterval: 5000, // Refetch every 5 seconds
  })

  if (isLoading || !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-400">Loading statistics...</div>
      </div>
    )
  }

  const vehicleTypeData = Object.entries(stats.vehicle_types).map(([name, count]) => ({
    name,
    count
  }))

  const colorData = Object.entries(stats.vehicle_colors).map(([name, count]) => ({
    name,
    count
  }))

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<Car className="w-6 h-6" />}
          title="Total Vehicles"
          value={stats.total_vehicles.toString()}
          color="text-blue-400"
          bgColor="bg-blue-500/10"
        />
        
        <StatCard
          icon={<TrendingUp className="w-6 h-6" />}
          title="Vehicle Types"
          value={Object.keys(stats.vehicle_types).length.toString()}
          color="text-green-400"
          bgColor="bg-green-500/10"
        />
        
        <StatCard
          icon={<Palette className="w-6 h-6" />}
          title="Color Variety"
          value={Object.keys(stats.vehicle_colors).length.toString()}
          color="text-purple-400"
          bgColor="bg-purple-500/10"
        />
        
        <StatCard
          icon={<Gauge className="w-6 h-6" />}
          title="Avg Speed"
          value={`${stats.average_speed} km/h`}
          color="text-orange-400"
          bgColor="bg-orange-500/10"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Vehicle Types Chart */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
          <h3 className="text-lg font-bold text-white mb-4">Vehicle Types Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={vehicleTypeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '0.5rem',
                  color: '#fff'
                }}
              />
              <Legend />
              <Bar dataKey="count" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Color Distribution Chart */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
          <h3 className="text-lg font-bold text-white mb-4">Color Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={colorData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="count"
              >
                {colorData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '0.5rem',
                  color: '#fff'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Vehicle Types Breakdown */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
          <h3 className="text-lg font-bold text-white mb-4">Vehicle Types Breakdown</h3>
          <div className="space-y-3">
            {Object.entries(stats.vehicle_types).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <span className="text-gray-300 capitalize">{type}</span>
                <span className="text-white font-semibold">{String(count)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Colors Breakdown */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
          <h3 className="text-lg font-bold text-white mb-4">Colors Breakdown</h3>
          <div className="space-y-3">
            {Object.entries(stats.vehicle_colors).map(([color, count]) => (
              <div key={color} className="flex items-center justify-between">
                <span className="text-gray-300 capitalize">{color}</span>
                <span className="text-white font-semibold">{String(count)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({
  icon,
  title,
  value,
  color,
  bgColor
}: {
  icon: React.ReactNode
  title: string
  value: string
  color: string
  bgColor: string
}) {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
      <div className="flex items-center gap-4">
        <div className={`${bgColor} ${color} p-3 rounded-lg`}>
          {icon}
        </div>
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
        </div>
      </div>
    </div>
  )
}
