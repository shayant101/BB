'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import PriceComparisonTool from '../../../src/components/PriceComparisonTool';
import {
  ArrowLeftIcon,
  ScaleIcon
} from '@heroicons/react/24/outline';

export default function ComparePage() {
  const router = useRouter();

  // Hardcoded user for demonstration until new auth is implemented
  const user = {
    id: 'user_placeholder_id',
    name: 'Demo Restaurant',
    email: 'demo@bistroboard.com',
    role: 'restaurant'
  };

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