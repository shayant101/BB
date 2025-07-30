'use client';
console.log("--- Rendering DashboardPage ---");

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getUser, getAuthToken, removeAuthToken } from '../../src/lib/api';
import RestaurantDashboard from '../../src/components/RestaurantDashboard';
import VendorDashboard from '../../src/components/VendorDashboard';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const initializeAuth = async () => {
      const token = getAuthToken();
      const userData = getUser();

      if (!token || !userData) {
        router.push('/');
        return;
      }

      // Ensure token is set in axios instance before proceeding
      if (token) {
        const api = (await import('../../src/lib/api')).default;
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      }

      setUser(userData);
      setLoading(false);
    };

    initializeAuth();
  }, [router]);

  const handleLogout = () => {
    removeAuthToken();
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user) {
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
                {user.role === 'restaurant' ? 'Restaurant' : 'Vendor'}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.name}</span>
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
        {user.role === 'restaurant' ? (
          <RestaurantDashboard user={user} />
        ) : (
          <VendorDashboard user={user} />
        )}
      </main>
    </div>
  );
}