'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  MessageSquare, 
  Users, 
  Settings,
  Menu,
  X,
  Home,
  TrendingUp,
  Target
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Sentiment Analysis', href: '/sentiment', icon: MessageSquare },
  { name: 'Customer Segmentation', href: '/customers', icon: Users },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Predictions', href: '/predictions', icon: TrendingUp },
  { name: 'Settings', href: '/settings', icon: Settings }
]

export default function Navigation() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const pathname = usePathname()

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden">
        <button
          type="button"
          className="text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu className="w-6 h-6" />
        </button>
      </div>

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center">
            <Target className="w-8 h-8 text-primary-600" />
            <span className="ml-2 text-xl font-bold text-gradient">GameEdge</span>
          </div>
          <button
            type="button"
            className="lg:hidden text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                      : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-neutral-100'
                  }`}
                >
                  <Icon className={`mr-3 w-5 h-5 ${
                    isActive ? 'text-primary-500' : 'text-neutral-400 group-hover:text-neutral-500'
                  }`} />
                  {item.name}
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute right-3 w-2 h-2 bg-primary-500 rounded-full"
                      initial={false}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  )}
                </Link>
              )
            })}
          </div>
        </nav>

        {/* User section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900/20 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-primary-700 dark:text-primary-300">AI</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">AI Assistant</p>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">GameEdge Intelligence</p>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </>
  )
}
