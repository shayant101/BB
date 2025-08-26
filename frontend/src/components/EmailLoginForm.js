'use client';

import { SignIn } from '@clerk/nextjs';

const EmailLoginForm = ({ onSuccess, onError, onSwitchToRegister }) => {
  return (
    <div className="w-full max-w-md">
      <div className="login-card">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome back</h2>
          <p className="text-gray-600">Sign in to your account</p>
        </div>

        <SignIn 
          appearance={{
            elements: {
              formButtonPrimary: 'btn-primary',
              card: 'shadow-none border-none',
              headerTitle: 'hidden',
              headerSubtitle: 'hidden',
            }
          }}
          redirectUrl="/dashboard"
          signUpUrl="/register"
        />

        {/* Switch to Register */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
            >
              Create one here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmailLoginForm;