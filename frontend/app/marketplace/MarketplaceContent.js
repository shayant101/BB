'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser, useClerk } from '@clerk/nextjs';
import VendorMarketplace from '../../src/components/VendorMarketplace';

export default function MarketplaceContent() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();
  const [userRole, setUserRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (isLoaded) {
      if (!isSignedIn) {
        router.push('/');
        return;
      }
      
      // For now, we'll use a default role since we need to implement role management
      // In a real app, you'd fetch this from your backend or store it in Clerk metadata
      const role = 'restaurant'; // Default role for testing
      
      // Only restaurants can access marketplace
      if (role !== 'restaurant') {
        router.push('/dashboard');
        return;
      }
      
      setUserRole(role);
      setLoading(false);
    }
  }, [isLoaded, isSignedIn, router]);

  const handleCreateOrder = (vendor) => {
    // Navigate to dashboard with vendor pre-selected for order creation
    router.push(`/dashboard?create_order=true&vendor_id=${vendor.user_id}`);
  };

  if (loading || !isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading marketplace...</p>
        </div>
      </div>
    );
  }

  if (!isSignedIn || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                ← Back to Dashboard
              </button>
              <div className="h-6 border-l border-gray-300"></div>
              <h1 className="text-xl font-semibold text-gray-900">
                BistroBoard Marketplace
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user.firstName || user.emailAddresses[0]?.emailAddress}
              </span>
              <button
                onClick={async () => {
                  await signOut();
                  router.push('/');
                }}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <VendorMarketplace onCreateOrder={handleCreateOrder} />
      </main>
    </div>
  );
}