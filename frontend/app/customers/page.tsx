'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  PieChart, 
  Target, 
  TrendingUp,
  BarChart3,
  Activity,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Clock,
  MapPin,
  Calendar
} from 'lucide-react'

// Mock customer segmentation data
const mockCustomerData = {
  segments: [
    {
      id: 1,
      name: "High Value Customers",
      userCount: 1250,
      avgLifetimeValue: 2500.0,
      churnRisk: 0.15,
      avgBetSize: 150.0,
      winRate: 72.5,
      topSports: ["Football", "Basketball"],
      description: "Premium customers with high betting volume and loyalty"
    },
    {
      id: 2,
      name: "Active Bettors",
      userCount: 3200,
      avgLifetimeValue: 800.0,
      churnRisk: 0.25,
      avgBetSize: 75.0,
      winRate: 68.3,
      topSports: ["Football", "Baseball", "Hockey"],
      description: "Regular bettors with consistent activity"
    },
    {
      id: 3,
      name: "At Risk Customers",
      userCount: 890,
      avgLifetimeValue: 150.0,
      churnRisk: 0.75,
      avgBetSize: 25.0,
      winRate: 45.2,
      topSports: ["All Sports"],
      description: "Customers showing signs of churn"
    },
    {
      id: 4,
      name: "New Users",
      userCount: 2100,
      avgLifetimeValue: 50.0,
      churnRisk: 0.40,
      avgBetSize: 30.0,
      winRate: 55.8,
      topSports: ["Football", "Basketball"],
      description: "Recently registered users"
    },
    {
      id: 5,
      name: "Weekend Warriors",
      userCount: 1800,
      avgLifetimeValue: 400.0,
      churnRisk: 0.30,
      avgBetSize: 60.0,
      winRate: 62.1,
      topSports: ["Football", "Basketball"],
      description: "Weekend-focused bettors"
    }
  ],
  rfmAnalysis: {
    recency: [
      { score: "5", count: 3200, percentage: 25.8 },
      { score: "4", count: 2800, percentage: 22.6 },
      { score: "3", count: 2400, percentage: 19.4 },
      { score: "2", count: 2200, percentage: 17.7 },
      { score: "1", count: 1800, percentage: 14.5 }
    ],
    frequency: [
      { score: "5", count: 1500, percentage: 12.1 },
      { score: "4", count: 2800, percentage: 22.6 },
      { score: "3", count: 3500, percentage: 28.2 },
      { score: "2", count: 2800, percentage: 22.6 },
      { score: "1", count: 1800, percentage: 14.5 }
    ],
    monetary: [
      { score: "5", count: 1200, percentage: 9.7 },
      { score: "4", count: 2500, percentage: 20.2 },
      { score: "3", count: 3800, percentage: 30.6 },
      { score: "2", count: 3200, percentage: 25.8 },
      { score: "1", count: 1700, percentage: 13.7 }
    ]
  },
  churnPredictions: [
    { risk: "Low", count: 6800, percentage: 54.8 },
    { risk: "Medium", count: 3200, percentage: 25.8 },
    { risk: "High", count: 2400, percentage: 19.4 }
  ]
}

export default function CustomersPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [data, setData] = useState(mockCustomerData)
  const [selectedSegment, setSelectedSegment] = useState(null)
  const [activeTab, setActiveTab] = useState('segments')

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const getChurnRiskColor = (risk: number) => {
    if (risk < 0.3) return 'text-green-600 bg-green-100 dark:bg-green-900/20'
    if (risk < 0.6) return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
    return 'text-red-600 bg-red-100 dark:bg-red-900/20'
  }

  const getChurnRiskLabel = (risk: number) => {
    if (risk < 0.3) return 'Low'
    if (risk < 0.6) return 'Medium'
    return 'High'
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
              <h1 className="text-2xl font-bold text-gradient">Customer Segmentation</h1>
              <p className="text-neutral-600 dark:text-neutral-400">Advanced customer analytics and segmentation</p>
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
        {/* Tab Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-1 bg-neutral-100 dark:bg-neutral-800 p-1 rounded-lg">
            {[
              { id: 'segments', label: 'Segments', icon: Users },
              { id: 'rfm', label: 'RFM Analysis', icon: PieChart },
              { id: 'churn', label: 'Churn Risk', icon: AlertTriangle }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-white dark:bg-neutral-700 text-primary-600 shadow-sm'
                      : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'segments' && (
          <div className="space-y-6">
            {/* Segment Overview */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
              {data.segments.map((segment) => (
                <div
                  key={segment.id}
                  onClick={() => setSelectedSegment(segment)}
                  className={`dashboard-card cursor-pointer transition-all hover:shadow-medium ${
                    selectedSegment?.id === segment.id ? 'ring-2 ring-primary-500' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-lg">{segment.name}</h3>
                    <Users className="w-5 h-5 text-primary-600" />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-neutral-600 dark:text-neutral-400">Users:</span>
                      <span className="font-medium">{segment.userCount.toLocaleString()}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-neutral-600 dark:text-neutral-400">Avg LTV:</span>
                      <span className="font-medium">${segment.avgLifetimeValue.toLocaleString()}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-neutral-600 dark:text-neutral-400">Churn Risk:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getChurnRiskColor(segment.churnRisk)}`}>
                        {getChurnRiskLabel(segment.churnRisk)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </motion.div>

            {/* Selected Segment Details */}
            {selectedSegment && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="dashboard-card"
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">{selectedSegment.name}</h2>
                  <button
                    onClick={() => setSelectedSegment(null)}
                    className="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
                  >
                    ×
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary-600">{selectedSegment.userCount.toLocaleString()}</div>
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">Total Users</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">${selectedSegment.avgLifetimeValue.toLocaleString()}</div>
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">Avg Lifetime Value</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{selectedSegment.winRate}%</div>
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">Win Rate</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">${selectedSegment.avgBetSize}</div>
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">Avg Bet Size</div>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h3 className="font-medium mb-2">Description</h3>
                  <p className="text-neutral-600 dark:text-neutral-400">{selectedSegment.description}</p>
                </div>
                
                <div className="mt-4">
                  <h3 className="font-medium mb-2">Top Sports</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedSegment.topSports.map((sport, index) => (
                      <span key={index} className="px-3 py-1 bg-primary-100 dark:bg-primary-900/20 text-primary-800 dark:text-primary-200 text-sm rounded-full">
                        {sport}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        )}

        {activeTab === 'rfm' && (
          <div className="space-y-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6"
            >
              {/* Recency */}
              <div className="dashboard-card">
                <div className="flex items-center space-x-2 mb-4">
                  <Calendar className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold">Recency Score</h3>
                </div>
                <div className="space-y-3">
                  {data.rfmAnalysis.recency.map((item) => (
                    <div key={item.score} className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                      <span className="font-medium">Score {item.score}</span>
                      <div className="text-right">
                        <div className="font-medium">{item.count.toLocaleString()}</div>
                        <div className="text-sm text-neutral-500">{item.percentage}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Frequency */}
              <div className="dashboard-card">
                <div className="flex items-center space-x-2 mb-4">
                  <Activity className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold">Frequency Score</h3>
                </div>
                <div className="space-y-3">
                  {data.rfmAnalysis.frequency.map((item) => (
                    <div key={item.score} className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                      <span className="font-medium">Score {item.score}</span>
                      <div className="text-right">
                        <div className="font-medium">{item.count.toLocaleString()}</div>
                        <div className="text-sm text-neutral-500">{item.percentage}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Monetary */}
              <div className="dashboard-card">
                <div className="flex items-center space-x-2 mb-4">
                  <DollarSign className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold">Monetary Score</h3>
                </div>
                <div className="space-y-3">
                  {data.rfmAnalysis.monetary.map((item) => (
                    <div key={item.score} className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                      <span className="font-medium">Score {item.score}</span>
                      <div className="text-right">
                        <div className="font-medium">{item.count.toLocaleString()}</div>
                        <div className="text-sm text-neutral-500">{item.percentage}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {activeTab === 'churn' && (
          <div className="space-y-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
              {/* Churn Risk Distribution */}
              <div className="dashboard-card">
                <div className="flex items-center space-x-2 mb-4">
                  <AlertTriangle className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold">Churn Risk Distribution</h3>
                </div>
                <div className="space-y-3">
                  {data.churnPredictions.map((item) => (
                    <div key={item.risk} className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                      <span className="font-medium">{item.risk} Risk</span>
                      <div className="text-right">
                        <div className="font-medium">{item.count.toLocaleString()}</div>
                        <div className="text-sm text-neutral-500">{item.percentage}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Churn Prevention Actions */}
              <div className="dashboard-card">
                <div className="flex items-center space-x-2 mb-4">
                  <Target className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold">Recommended Actions</h3>
                </div>
                <div className="space-y-3">
                  <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <h4 className="font-medium text-red-800 dark:text-red-200 mb-1">High Risk Customers</h4>
                    <p className="text-sm text-red-700 dark:text-red-300">Implement retention campaigns, personalized offers, and proactive support</p>
                  </div>
                  
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <h4 className="font-medium text-yellow-800 dark:text-yellow-200 mb-1">Medium Risk Customers</h4>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">Engage with targeted content and moderate incentives</p>
                  </div>
                  
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                    <h4 className="font-medium text-green-800 dark:text-green-200 mb-1">Low Risk Customers</h4>
                    <p className="text-sm text-green-700 dark:text-green-300">Focus on upselling and referral programs</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </main>
    </div>
  )
}
