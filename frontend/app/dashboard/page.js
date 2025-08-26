'use client';
console.log("--- Rendering DashboardPage ---");

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser, useClerk } from '@clerk/nextjs';
import RestaurantDashboard from '../../src/components/RestaurantDashboard';
import VendorDashboard from '../../src/components/VendorDashboard';

export default function Dashboard() {
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
      setUserRole('restaurant'); // Default role for testing
      setLoading(false);
    }
  }, [isLoaded, isSignedIn, router]);

  const handleLogout = async () => {
    await signOut();
    router.push('/');
  };

  if (loading || !isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
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
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">BistroBoard</h1>
              <span className="ml-4 px-3 py-1 bg-primary text-white text-sm rounded-full">
                {userRole === 'restaurant' ? 'Restaurant' : 'Vendor'}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.firstName || user.emailAddresses[0]?.emailAddress}</span>
              <button
                onClick={handleLogout}
                className="btn-secondary"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Dashboard Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {userRole === 'restaurant' ? (
          <RestaurantDashboard user={{ ...user, role: userRole }} />
        ) : (
          <VendorDashboard user={{ ...user, role: userRole }} />
        )}
      </main>
    </div>
  );
}