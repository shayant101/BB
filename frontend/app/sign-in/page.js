'use client';

import dynamic from 'next/dynamic';

const EmailLoginForm = dynamic(() => import('../../src/components/EmailLoginForm'), { ssr: false });

export default function SignInPage() {
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
        </div>
      </div>

      {/* Right Side - Sign In Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-8 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8 lg:hidden">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">BistroBoard</h1>
            <p className="text-gray-600">Restaurant-Supplier Management</p>
          </div>

          <EmailLoginForm />
        </div>
      </div>
    </div>
  )
}