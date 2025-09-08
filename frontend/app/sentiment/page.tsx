'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  MessageSquare, 
  TrendingUp, 
  BarChart3, 
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Target,
  Zap
} from 'lucide-react'

// Mock sentiment data
const mockSentimentData = {
  recentAnalyses: [
    {
      id: 1,
      text: "The new betting interface is amazing! Much better than before.",
      sentiment: "positive",
      score: 0.89,
      confidence: 0.92,
      aspects: ["user_interface", "platform"],
      timestamp: "2 min ago"
    },
    {
      id: 2,
      text: "Terrible customer service, been waiting for hours.",
      sentiment: "negative",
      score: -0.76,
      confidence: 0.88,
      aspects: ["customer_service"],
      timestamp: "5 min ago"
    },
    {
      id: 3,
      text: "Odds are decent but could be better for football games.",
      sentiment: "neutral",
      score: 0.12,
      confidence: 0.85,
      aspects: ["odds", "sports"],
      timestamp: "8 min ago"
    }
  ],
  sentimentTrends: [
    { date: '2024-01-01', positive: 65, negative: 20, neutral: 15, total: 1000 },
    { date: '2024-01-02', positive: 70, negative: 18, neutral: 12, total: 1200 },
    { date: '2024-01-03', positive: 68, negative: 22, neutral: 10, total: 1100 },
    { date: '2024-01-04', positive: 72, negative: 19, neutral: 9, total: 1300 },
    { date: '2024-01-05', positive: 75, negative: 17, neutral: 8, total: 1400 }
  ],
  topAspects: [
    { aspect: "user_interface", count: 1250, sentiment: 0.78 },
    { aspect: "odds", count: 980, sentiment: 0.45 },
    { aspect: "customer_service", count: 720, sentiment: -0.23 },
    { aspect: "mobile_app", count: 650, sentiment: 0.82 },
    { aspect: "payouts", count: 520, sentiment: 0.67 }
  ]
}

export default function SentimentPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [inputText, setInputText] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [data, setData] = useState(mockSentimentData)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  const analyzeSentiment = async () => {
    if (!inputText.trim()) return
    
    setIsLoading(true)
    
    try {
      // Mock API call - replace with actual API endpoint
      const response = await fetch('/api/v1/sentiment/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      })
      
      if (response.ok) {
        const result = await response.json()
        setAnalysisResult(result)
      } else {
        // Fallback to mock analysis for demo
        const mockResult = {
          text: inputText,
          sentiment_label: inputText.toLowerCase().includes('great') ? 'positive' : 
                          inputText.toLowerCase().includes('terrible') ? 'negative' : 'neutral',
          sentiment_score: inputText.toLowerCase().includes('great') ? 0.8 : 
                          inputText.toLowerCase().includes('terrible') ? -0.7 : 0.1,
          confidence_score: 0.85,
          aspects: ['general'],
          timestamp: new Date().toISOString()
        }
        setAnalysisResult(mockResult)
      }
    } catch (error) {
      console.error('Error analyzing sentiment:', error)
      // Fallback mock result
      const mockResult = {
        text: inputText,
        sentiment_label: 'neutral',
        sentiment_score: 0.0,
        confidence_score: 0.75,
        aspects: ['general'],
        timestamp: new Date().toISOString()
      }
      setAnalysisResult(mockResult)
    } finally {
      setIsLoading(false)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100 dark:bg-green-900/20'
      case 'negative': return 'text-red-600 bg-red-100 dark:bg-red-900/20'
      default: return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
    }
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'negative': return <XCircle className="w-5 h-5 text-red-600" />
      default: return <AlertTriangle className="w-5 h-5 text-yellow-600" />
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900">
      {/* Header */}
      <header className="bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gradient">Sentiment Analysis</h1>
              <p className="text-neutral-600 dark:text-neutral-400">Real-time sentiment monitoring for sports betting</p>
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sentiment Analysis Input */}
          <div className="lg:col-span-1">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="dashboard-card"
            >
              <div className="flex items-center space-x-2 mb-4">
                <MessageSquare className="w-5 h-5 text-primary-600" />
                <h2 className="text-lg font-semibold">Analyze Sentiment</h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Enter text to analyze
                  </label>
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Enter customer feedback, reviews, or social media posts..."
                    className="input-field h-32 resize-none"
                    rows={5}
                  />
                </div>
                
                <button
                  onClick={analyzeSentiment}
                  disabled={isLoading || !inputText.trim()}
                  className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Zap className="w-4 h-4" />
                      <span>Analyze Sentiment</span>
                    </div>
                  )}
                </button>
              </div>

              {/* Analysis Result */}
              {analysisResult && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg border"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium">Analysis Result</h3>
                    {getSentimentIcon(analysisResult.sentiment_label)}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-neutral-600 dark:text-neutral-400">Sentiment:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(analysisResult.sentiment_label)}`}>
                        {analysisResult.sentiment_label}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-neutral-600 dark:text-neutral-400">Score:</span>
                      <span className="font-medium">{analysisResult.sentiment_score.toFixed(2)}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-neutral-600 dark:text-neutral-400">Confidence:</span>
                      <span className="font-medium">{(analysisResult.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                    
                    {analysisResult.aspects && (
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-neutral-600 dark:text-neutral-400">Aspects:</span>
                        <div className="flex flex-wrap gap-1">
                          {analysisResult.aspects.map((aspect, index) => (
                            <span key={index} className="px-2 py-1 bg-primary-100 dark:bg-primary-900/20 text-primary-800 dark:text-primary-200 text-xs rounded">
                              {aspect}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </motion.div>
          </div>

          {/* Sentiment Trends & Analytics */}
          <div className="lg:col-span-2">
            <div className="grid grid-cols-1 gap-6">
              {/* Sentiment Trends Chart */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="dashboard-card"
              >
                <div className="flex items-center space-x-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-primary-600" />
                  <h2 className="text-lg font-semibold">Sentiment Trends</h2>
                </div>
                
                <div className="h-64 flex items-center justify-center text-neutral-500">
                  <div className="text-center">
                    <BarChart3 className="w-16 h-16 mx-auto mb-4 text-neutral-400" />
                    <p>Sentiment trends chart will be displayed here</p>
                    <p className="text-sm">Integration with Recharts/D3.js</p>
                  </div>
                </div>
              </motion.div>

              {/* Top Aspects & Recent Analyses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Top Aspects */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="dashboard-card"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    <Target className="w-5 h-5 text-primary-600" />
                    <h2 className="text-lg font-semibold">Top Aspects</h2>
                  </div>
                  
                  <div className="space-y-3">
                    {data.topAspects.map((aspect, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                        <div>
                          <p className="font-medium capitalize">{aspect.aspect.replace('_', ' ')}</p>
                          <p className="text-sm text-neutral-600 dark:text-neutral-400">
                            {aspect.count} mentions
                          </p>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                          aspect.sentiment > 0.3 ? 'text-green-600 bg-green-100 dark:bg-green-900/20' :
                          aspect.sentiment < -0.3 ? 'text-red-600 bg-red-100 dark:bg-red-900/20' :
                          'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
                        }`}>
                          {aspect.sentiment > 0.3 ? 'Positive' : 
                           aspect.sentiment < -0.3 ? 'Negative' : 'Neutral'}
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* Recent Analyses */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="dashboard-card"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    <Activity className="w-5 h-5 text-primary-600" />
                    <h2 className="text-lg font-semibold">Recent Analyses</h2>
                  </div>
                  
                  <div className="space-y-3">
                    {data.recentAnalyses.map((analysis) => (
                      <div key={analysis.id} className="p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(analysis.sentiment)}`}>
                            {analysis.sentiment}
                          </div>
                          <span className="text-xs text-neutral-500">{analysis.timestamp}</span>
                        </div>
                        
                        <p className="text-sm text-neutral-700 dark:text-neutral-300 mb-2 line-clamp-2">
                          {analysis.text}
                        </p>
                        
                        <div className="flex items-center justify-between text-xs text-neutral-500">
                          <span>Score: {analysis.score.toFixed(2)}</span>
                          <span>Confidence: {(analysis.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
