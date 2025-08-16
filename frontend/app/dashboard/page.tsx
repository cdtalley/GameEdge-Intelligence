'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Users, 
  DollarSign, 
  Activity,
  BarChart3,
  PieChart,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react'

// Mock data for demonstration
const mockDashboardData = {
  metrics: {
    totalUsers: 15420,
    activeUsers: 8920,
    totalBets: 45678,
    totalRevenue: 2345678.90,
    averageBetSize: 51.40,
    winRate: 68.5,
    sentimentScore: 0.72,
    churnRisk: 0.23
  },
  recentActivity: [
    { id: 1, type: 'bet', user: 'JohnDoe', action: 'placed a bet', amount: 100, sport: 'Football', time: '2 min ago' },
    { id: 2, type: 'withdrawal', user: 'BetMaster', action: 'withdrew', amount: 500, sport: 'N/A', time: '5 min ago' },
    { id: 3, type: 'bet', user: 'SportsFan', action: 'won a bet', amount: 250, sport: 'Basketball', time: '8 min ago' },
    { id: 4, type: 'deposit', user: 'LuckyGuy', action: 'deposited', amount: 1000, sport: 'N/A', time: '12 min ago' }
  ],
  topSports: [
    { sport: 'Football', bets: 12500, revenue: 850000, growth: 12.5 },
    { sport: 'Basketball', bets: 9800, revenue: 650000, growth: 8.3 },
    { sport: 'Baseball', bets: 7200, revenue: 480000, growth: 15.2 },
    { sport: 'Hockey', bets: 5400, revenue: 320000, growth: 6.7 }
  ],
  sentimentTrends: [
    { date: '2024-01-01', positive: 65, negative: 20, neutral: 15 },
    { date: '2024-01-02', positive: 70, negative: 18, neutral: 12 },
    { date: '2024-01-03', positive: 68, negative: 22, neutral: 10 },
    { date: '2024-01-04', positive: 72, negative: 19, neutral: 9 },
    { date: '2024-01-05', positive: 75, negative: 17, neutral: 8 }
  ]
}

export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [data, setData] = useState(mockDashboardData)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

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
              <h1 className="text-2xl font-bold text-gradient">GameEdge Intelligence</h1>
              <p className="text-neutral-600 dark:text-neutral-400">Sports Betting Analytics Dashboard</p>
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
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          {/* Key Metrics */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="dashboard-card"
          >
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                <Users className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Total Users</p>
                <p className="text-2xl font-bold">{data.metrics.totalUsers.toLocaleString()}</p>
              </div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="dashboard-card"
          >
            <div className="flex items-center">
              <div className="p-2 bg-success-100 dark:bg-success-900 rounded-lg">
                <Activity className="h-6 w-6 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Active Users</p>
                <p className="text-2xl font-bold">{data.metrics.activeUsers.toLocaleString()}</p>
              </div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="dashboard-card"
          >
            <div className="flex items-center">
              <div className="p-2 bg-warning-100 dark:bg-warning-900 rounded-lg">
                <DollarSign className="h-6 w-6 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Total Revenue</p>
                <p className="text-2xl font-bold">${(data.metrics.totalRevenue / 1000000).toFixed(1)}M</p>
              </div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="dashboard-card"
          >
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                <TrendingUp className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Win Rate</p>
                <p className="text-2xl font-bold">{data.metrics.winRate}%</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Charts and Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Sentiment Analysis */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="dashboard-card"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Sentiment Analysis</h3>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Positive</span>
                <div className="w-3 h-3 bg-danger-500 rounded-full"></div>
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Negative</span>
                <div className="w-3 h-3 bg-neutral-500 rounded-full"></div>
                <span className="text-sm text-neutral-600 dark:text-neutral-400">Neutral</span>
              </div>
            </div>
            <div className="chart-container">
              <div className="flex items-end justify-between h-48">
                {data.sentimentTrends.map((trend, index) => (
                  <div key={index} className="flex flex-col items-center">
                    <div className="flex flex-col items-center space-y-1">
                      <div 
                        className="w-8 bg-success-500 rounded-t"
                        style={{ height: `${trend.positive * 0.6}px` }}
                      ></div>
                      <div 
                        className="w-8 bg-danger-500"
                        style={{ height: `${trend.negative * 0.6}px` }}
                      ></div>
                      <div 
                        className="w-8 bg-neutral-500 rounded-b"
                        style={{ height: `${trend.neutral * 0.6}px` }}
                      ></div>
                    </div>
                    <span className="text-xs text-neutral-600 dark:text-neutral-400 mt-2">
                      {new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Top Sports Performance */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="dashboard-card"
          >
            <h3 className="text-lg font-semibold mb-4">Top Sports Performance</h3>
            <div className="space-y-4">
              {data.topSports.map((sport, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                    <span className="font-medium">{sport.sport}</span>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">${(sport.revenue / 1000).toFixed(0)}K</p>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      {sport.bets.toLocaleString()} bets
                    </p>
                  </div>
                  <div className={`text-sm ${sport.growth > 0 ? 'text-success-600' : 'text-danger-600'}`}>
                    {sport.growth > 0 ? '+' : ''}{sport.growth}%
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Recent Activity */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="dashboard-card"
        >
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {data.recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  {activity.type === 'bet' && (
                    <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                      <Target className="h-4 w-4 text-primary-600" />
                    </div>
                  )}
                  {activity.type === 'withdrawal' && (
                    <div className="p-2 bg-danger-100 dark:bg-danger-900 rounded-lg">
                      <XCircle className="h-4 w-4 text-danger-600" />
                    </div>
                  )}
                  {activity.type === 'deposit' && (
                    <div className="p-2 bg-success-100 dark:bg-success-900 rounded-lg">
                      <CheckCircle className="h-4 w-4 text-success-600" />
                    </div>
                  )}
                  <div>
                    <p className="font-medium">{activity.user}</p>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      {activity.action} {activity.sport !== 'N/A' ? `on ${activity.sport}` : ''}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">${activity.amount}</p>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </main>
    </div>
  )
}
