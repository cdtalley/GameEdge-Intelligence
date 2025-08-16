import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'GameEdge Intelligence - Sports Betting Analytics Platform',
  description: 'Advanced sentiment analysis and customer segmentation platform for sports betting and fantasy sports with enterprise-grade ML capabilities.',
  keywords: [
    'sports betting',
    'analytics',
    'sentiment analysis',
    'customer segmentation',
    'machine learning',
    'dashboard',
    'business intelligence'
  ],
  authors: [{ name: 'GameEdge Intelligence Team' }],
  creator: 'GameEdge Intelligence',
  publisher: 'GameEdge Intelligence',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'GameEdge Intelligence - Sports Betting Analytics Platform',
    description: 'Advanced sentiment analysis and customer segmentation platform for sports betting and fantasy sports with enterprise-grade ML capabilities.',
    url: '/',
    siteName: 'GameEdge Intelligence',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'GameEdge Intelligence Dashboard',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GameEdge Intelligence - Sports Betting Analytics Platform',
    description: 'Advanced sentiment analysis and customer segmentation platform for sports betting and fantasy sports with enterprise-grade ML capabilities.',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <meta name="theme-color" content="#0ea5e9" />
        <meta name="msapplication-TileColor" content="#0ea5e9" />
      </head>
      <body className={`${inter.className} antialiased bg-neutral-50 dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100 min-h-screen`}>
        <div className="flex min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
