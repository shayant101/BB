'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import PriceComparisonTool from '../../../src/components/PriceComparisonTool';
import {
  ArrowLeftIcon,
  ScaleIcon
} from '@heroicons/react/24/outline';

export default function ComparePage() {
  const { isLoaded, isSignedIn, user: clerkUser } = useUser();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (isLoaded) {
      if (!isSignedIn) {
        router.push('/');
        return;
      }

      // Create user object from Clerk data
      const userData = {
        id: clerkUser.id,
        name: clerkUser.fullName || clerkUser.firstName || 'User',
        email: clerkUser.primaryEmailAddress?.emailAddress || '',
        role: 'restaurant' // Default role for now
      };

      setUser(userData);
      setLoading(false);
    }
  }, [isLoaded, isSignedIn, clerkUser, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading price comparison tool...</p>
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
              <button
                onClick={() => router.push('/dashboard')}
                className="mr-4 p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div className="flex items-center">
                <ScaleIcon className="h-8 w-8 text-primary mr-3" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Price Comparison</h1>
                  <p className="text-sm text-gray-600">Compare prices across vendors</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.name}</span>
              <span className="px-3 py-1 bg-primary text-white text-sm rounded-full">
                {user.role === 'restaurant' ? 'Restaurant' : 'Vendor'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <PriceComparisonTool user={user} />
      </main>
    </div>
  );
}