'use client';

import { SignUp } from '@clerk/nextjs';

const EmailRegistrationForm = ({ onSuccess, onError, onSwitchToLogin }) => {
  return (
    <div className="w-full max-w-md">
      <div className="login-card">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Create Account</h2>
          <p className="text-gray-600">Join BistroBoard to get started</p>
        </div>

        <SignUp 
          appearance={{
            elements: {
              formButtonPrimary: 'btn-primary',
              card: 'shadow-none border-none',
              headerTitle: 'hidden',
              headerSubtitle: 'hidden',
            }
          }}
          redirectUrl="/dashboard"
          signInUrl="/login"
        />

        {/* Switch to Login */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
            >
              Sign in here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmailRegistrationForm;