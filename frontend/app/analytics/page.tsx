'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  TrendingUp, 
  PieChart, 
  Activity,
  DollarSign,
  Users,
  Target,
  Calendar,
  MapPin,
  Clock
} from 'lucide-react'

// Mock analytics data
const mockAnalyticsData = {
  revenueMetrics: {
    totalRevenue: 2345678.90,
    monthlyGrowth: 12.5,
    avgOrderValue: 51.40,
    customerLifetimeValue: 450.25
  },
  userMetrics: {
    totalUsers: 15420,
    activeUsers: 8920,
    newUsers: 1250,
    churnRate: 2.3
  },
  bettingMetrics: {
    totalBets: 45678,
    winRate: 68.5,
    avgBetSize: 51.40,
    topSport: "Football"
  },
  geographicData: [
    { state: "California", users: 3200, revenue: 450000, growth: 15.2 },
    { state: "Texas", users: 2800, revenue: 380000, growth: 12.8 },
    { state: "Florida", users: 2500, revenue: 320000, growth: 18.5 },
    { state: "New York", users: 2200, revenue: 290000, growth: 8.9 },
    { state: "Illinois", users: 1800, revenue: 240000, growth: 11.3 }
  ],
  timeSeriesData: [
    { date: '2024-01-01', revenue: 45000, users: 1200, bets: 850 },
    { date: '2024-01-02', revenue: 52000, users: 1350, bets: 920 },
    { date: '2024-01-03', revenue: 48000, users: 1280, bets: 880 },
    { date: '2024-01-04', revenue: 61000, users: 1450, bets: 1050 },
    { date: '2024-01-05', revenue: 55000, users: 1380, bets: 950 },
    { date: '2024-01-06', revenue: 72000, users: 1600, bets: 1250 },
    { date: '2024-01-07', revenue: 68000, users: 1550, bets: 1180 }
  ],
  sportPerformance: [
    { sport: "Football", bets: 12500, revenue: 850000, winRate: 72.5, avgOdds: 2.1 },
    { sport: "Basketball", bets: 9800, revenue: 650000, winRate: 68.3, avgOdds: 1.9 },
    { sport: "Baseball", bets: 7200, revenue: 480000, winRate: 65.8, avgOdds: 2.3 },
    { sport: "Hockey", bets: 5400, revenue: 320000, winRate: 62.1, avgOdds: 2.5 },
    { sport: "Tennis", bets: 3800, revenue: 250000, winRate: 58.9, avgOdds: 2.8 }
  ]
}

export default function AnalyticsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [data, setData] = useState(mockAnalyticsData)
  const [selectedMetric, setSelectedMetric] = useState('revenue')

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900">
      {/* Header */}
      <header className="bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gradient">Analytics Dashboard</h1>
              <p className="text-neutral-600 dark:text-neutral-400">Comprehensive business intelligence and performance metrics</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Last Updated</p>
                <p className="text-sm font-medium">{new Date().toLocaleTimeString()}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="dashboard-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Total Revenue</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(data.revenueMetrics.totalRevenue)}</p>
              </div>
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              +{data.revenueMetrics.monthlyGrowth}% this month
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="dashboard-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Active Users</p>
                <p className="text-2xl font-bold text-blue-600">{formatNumber(data.userMetrics.activeUsers)}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-blue-600">
              <Users className="w-4 h-4 mr-1" />
              +{formatNumber(data.userMetrics.newUsers)} new this month
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="dashboard-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Win Rate</p>
                <p className="text-2xl font-bold text-purple-600">{data.bettingMetrics.winRate}%</p>
              </div>
              <Target className="w-8 h-8 text-purple-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-purple-600">
              <Target className="w-4 h-4 mr-1" />
              {formatNumber(data.bettingMetrics.totalBets)} total bets
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="dashboard-card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Avg Bet Size</p>
                <p className="text-2xl font-bold text-orange-600">{formatCurrency(data.bettingMetrics.avgBetSize)}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-orange-600" />
            </div>
            <div className="mt-2 flex items-center text-sm text-orange-600">
              <BarChart3 className="w-4 h-4 mr-1" />
              Top sport: {data.bettingMetrics.topSport}
            </div>
          </motion.div>
        </div>

        {/* Charts and Detailed Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Trend Chart */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="dashboard-card"
          >
            <div className="flex items-center space-x-2 mb-4">
              <TrendingUp className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold">Revenue Trend (7 Days)</h2>
            </div>
            
            <div className="h-64 flex items-center justify-center text-neutral-500">
              <div className="text-center">
                <BarChart3 className="w-16 h-16 mx-auto mb-4 text-neutral-400" />
                <p>Revenue trend chart will be displayed here</p>
                <p className="text-sm">Integration with Recharts/D3.js</p>
              </div>
            </div>
          </motion.div>

          {/* Geographic Distribution */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="dashboard-card"
          >
            <div className="flex items-center space-x-2 mb-4">
              <MapPin className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold">Geographic Performance</h2>
            </div>
            
            <div className="space-y-3">
              {data.geographicData.map((state, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <MapPin className="w-4 h-4 text-neutral-500" />
                    <span className="font-medium">{state.state}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{formatNumber(state.users)} users</div>
                    <div className="text-sm text-neutral-500">{formatCurrency(state.revenue)}</div>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    state.growth > 15 ? 'text-green-600 bg-green-100 dark:bg-green-900/20' :
                    state.growth > 10 ? 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20' :
                    'text-red-600 bg-red-100 dark:bg-red-900/20'
                  }`}>
                    +{state.growth}%
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Sport Performance Table */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="dashboard-card"
        >
          <div className="flex items-center space-x-2 mb-4">
            <BarChart3 className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold">Sport Performance Analysis</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200 dark:border-neutral-700">
                  <th className="text-left py-3 px-4 font-medium">Sport</th>
                  <th className="text-right py-3 px-4 font-medium">Total Bets</th>
                  <th className="text-right py-3 px-4 font-medium">Revenue</th>
                  <th className="text-right py-3 px-4 font-medium">Win Rate</th>
                  <th className="text-right py-3 px-4 font-medium">Avg Odds</th>
                </tr>
              </thead>
              <tbody>
                {data.sportPerformance.map((sport, index) => (
                  <tr key={index} className="border-b border-neutral-100 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-800">
                    <td className="py-3 px-4 font-medium">{sport.sport}</td>
                    <td className="py-3 px-4 text-right">{formatNumber(sport.bets)}</td>
                    <td className="py-3 px-4 text-right">{formatCurrency(sport.revenue)}</td>
                    <td className="py-3 px-4 text-right">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        sport.winRate > 70 ? 'text-green-600 bg-green-100 dark:bg-green-900/20' :
                        sport.winRate > 60 ? 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20' :
                        'text-red-600 bg-red-100 dark:bg-red-900/20'
                      }`}>
                        {sport.winRate}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">{sport.avgOdds}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Additional Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="dashboard-card"
          >
            <div className="flex items-center space-x-2 mb-4">
              <Clock className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-semibold">Time Analysis</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Peak Hours:</span>
                <span className="font-medium">7-9 PM EST</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Weekend Activity:</span>
                <span className="font-medium">+45%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Seasonal Peak:</span>
                <span className="font-medium">NFL Season</span>
              </div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="dashboard-card"
          >
            <div className="flex items-center space-x-2 mb-4">
              <Users className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-semibold">User Behavior</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Avg Session:</span>
                <span className="font-medium">24 min</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Mobile Usage:</span>
                <span className="font-medium">68%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Return Rate:</span>
                <span className="font-medium">73%</span>
              </div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="dashboard-card"
          >
            <div className="flex items-center space-x-2 mb-4">
              <Target className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-semibold">Performance KPIs</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Conversion Rate:</span>
                <span className="font-medium">3.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Customer LTV:</span>
                <span className="font-medium">${data.revenueMetrics.customerLifetimeValue}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Churn Rate:</span>
                <span className="font-medium">{data.userMetrics.churnRate}%</span>
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
