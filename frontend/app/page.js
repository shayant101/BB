'use client';

import { useUser, SignInButton, UserButton } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function HomePage() {
  const { isSignedIn, user, isLoaded } = useUser();
  const router = useRouter();

  // No automatic redirect - let users stay on home page if they want

  // Show loading state while Clerk is initializing
  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <svg className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 3v3l4-4-4-4v3c-4.42 0-8 3.58-8 8s3.58 8 8 8c1.57 0 3.04-.46 4.28-1.26l-1.45-1.45C11.76 12.53 10.92 13 10 13c-1.65 0-3-1.35-3-3s1.35-3 3-3z" />
          </svg>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If user is signed in, show user button and quick access
  if (isSignedIn) {
    return (
      <div className="min-h-screen flex">
        {/* Left Side - Branding */}
        <div className="hidden lg:flex lg:w-1/2 login-gradient relative overflow-hidden">
          <div className="absolute inset-0 bg-black opacity-20"></div>
          <div className="relative z-10 flex flex-col justify-center px-12 text-white">
            <div className="mb-8">
              <h1 className="text-5xl font-bold mb-4">BistroBoard</h1>
              <p className="text-xl text-blue-100 leading-relaxed">
                Welcome back! Ready to manage your restaurant-supplier relationships.
              </p>
            </div>
            <div className="space-y-4 text-blue-100">
              <div className="flex items-center space-x-3">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                </svg>
                <span>Real-time order tracking</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                </svg>
                <span>Seamless communication</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                </svg>
                <span>Professional order management</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - User Dashboard */}
        <div className="w-full lg:w-1/2 flex items-center justify-center px-8 py-12">
          <div className="w-full max-w-md">
            <div className="text-center mb-8 lg:hidden">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">BistroBoard</h1>
              <p className="text-gray-600">Restaurant-Supplier Management</p>
            </div>

            <div className="login-card">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome back, {user?.firstName || 'User'}!</h2>
                <p className="text-gray-600">Manage your account and access your dashboard</p>
              </div>

              <div className="space-y-6">
                {/* User Button for account management */}
                <div className="flex justify-center">
                  <UserButton 
                    appearance={{
                      elements: {
                        avatarBox: 'w-12 h-12',
                        userButtonPopoverCard: 'shadow-lg',
                        userButtonPopoverActionButton: 'hover:bg-gray-50'
                      }
                    }}
                    afterSignOutUrl="/"
                  />
                </div>

                {/* Quick Access Buttons */}
                <div className="space-y-3">
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="w-full btn-primary text-lg py-3"
                  >
                    Go to Dashboard
                  </button>
                  
                  <button
                    onClick={() => router.push('/marketplace')}
                    className="w-full btn-secondary text-lg py-3"
                  >
                    Browse Marketplace
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Landing page for non-authenticated users
  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 login-gradient relative overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <div className="mb-8">
            <h1 className="text-5xl font-bold mb-4">BistroBoard</h1>
            <p className="text-xl text-blue-100 leading-relaxed">
              Streamline your restaurant-supplier relationships with modern order management.
            </p>
          </div>
          <div className="space-y-4 text-blue-100">
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
              </svg>
              <span>Real-time order tracking</span>
            </div>
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
              </svg>
              <span>Seamless communication</span>
            </div>
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
              </svg>
              <span>Professional order management</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Sign In Options */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-8 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8 lg:hidden">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">BistroBoard</h1>
            <p className="text-gray-600">Restaurant-Supplier Management</p>
          </div>

          <div className="login-card">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to BistroBoard</h2>
              <p className="text-gray-600">Sign in to manage your restaurant or supplier business</p>
            </div>

            <div className="space-y-6">
              {/* Clerk Sign In Button */}
              <SignInButton mode="modal">
                <button className="w-full btn-primary text-lg py-3">
                  Sign In
                </button>
              </SignInButton>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">New to BistroBoard?</span>
                </div>
              </div>

              <button
                onClick={() => router.push('/sign-up')}
                className="w-full btn-secondary text-lg py-3"
              >
                Create Account
              </button>

              {/* Admin Command Center Button */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Admin Access</span>
                </div>
              </div>

              <button
                onClick={() => router.push('/backend-login')}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clipRule="evenodd" />
                </svg>
                <span>🛡️ Admin Command Center</span>
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}