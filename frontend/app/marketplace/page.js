'use client';

import dynamic from 'next/dynamic';

// Dynamically import the marketplace content to avoid SSR issues
const MarketplaceContent = dynamic(() => import('./MarketplaceContent'), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading marketplace...</p>
      </div>
    </div>
  )
});

export default function MarketplacePage() {
  return <MarketplaceContent />;
}