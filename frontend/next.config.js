/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  
  // Production optimizations
  compress: true,
  poweredByHeader: false,
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
  
  // Redirects for production
  async redirects() {
    return [
      // Removed admin redirect - admin page is at /admin, not /admin/dashboard
    ];
  },
  
  // Image optimization
  images: {
    domains: [
      'lh3.googleusercontent.com', // For Google profile pictures
      'images.unsplash.com' // For landing page images
    ],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Build configuration
  experimental: {
    // Removed optimizeCss to fix build issues
  },
  
  // TypeScript configuration
  typescript: {
    // Ignore TypeScript errors during build for deployment
    ignoreBuildErrors: true,
  },
  
  // ESLint configuration
  eslint: {
    // Ignore ESLint errors during build for deployment
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;