'use client';

import { useState } from 'react';
import { authAPI, setAuthToken, setUser } from '../lib/api';

const EmailRegistrationForm = ({ onSuccess, onError, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    accountType: 'restaurant'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    // Full name validation
    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters long';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Account type validation
    if (!formData.accountType) {
      newErrors.accountType = 'Please select an account type';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call the registration API endpoint
      const response = await authAPI.register({
        full_name: formData.fullName,
        email: formData.email,
        password: formData.password,
        role: formData.accountType
      });

      // Store token and user info
      if (response.access_token) {
        setAuthToken(response.access_token);
        setUser({
          id: response.user_id,
          role: response.role,
          name: response.name,
          email: response.email
        });
      }

      onSuccess?.(response);
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
      onError?.(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="login-card">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Create Account</h2>
          <p className="text-gray-600">Join BistroBoard to get started</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Full Name Field */}
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <input
              id="fullName"
              name="fullName"
              type="text"
              value={formData.fullName}
              onChange={handleInputChange}
              className={`input-field ${errors.fullName ? 'border-red-500' : ''}`}
              placeholder="Enter your full name"
              disabled={isLoading}
            />
            {errors.fullName && (
              <p className="mt-1 text-sm text-red-600">{errors.fullName}</p>
            )}
          </div>

          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              className={`input-field ${errors.email ? 'border-red-500' : ''}`}
              placeholder="Enter your email address"
              disabled={isLoading}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email}</p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              className={`input-field ${errors.password ? 'border-red-500' : ''}`}
              placeholder="Create a password"
              disabled={isLoading}
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password}</p>
            )}
          </div>

          {/* Confirm Password Field */}
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              className={`input-field ${errors.confirmPassword ? 'border-red-500' : ''}`}
              placeholder="Confirm your password"
              disabled={isLoading}
            />
            {errors.confirmPassword && (
              <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
            )}
          </div>

          {/* Account Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Account Type
            </label>
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={() => handleInputChange({ target: { name: 'accountType', value: 'restaurant' } })}
                className={`flex-1 px-4 py-3 text-sm font-medium rounded-lg border transition-colors ${
                  formData.accountType === 'restaurant'
                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
                disabled={isLoading}
              >
                <div className="flex flex-col items-center">
                  <svg className="w-6 h-6 mb-1" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
                  </svg>
                  Restaurant
                </div>
              </button>
              <button
                type="button"
                onClick={() => handleInputChange({ target: { name: 'accountType', value: 'vendor' } })}
                className={`flex-1 px-4 py-3 text-sm font-medium rounded-lg border transition-colors ${
                  formData.accountType === 'vendor'
                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
                disabled={isLoading}
              >
                <div className="flex flex-col items-center">
                  <svg className="w-6 h-6 mb-1" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
                    <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1V8a1 1 0 00-1-1h-3z" />
                  </svg>
                  Vendor
                </div>
              </button>
            </div>
            {errors.accountType && (
              <p className="mt-1 text-sm text-red-600">{errors.accountType}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-primary text-lg py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>{isLoading ? 'Creating Account...' : 'Create Account'}</span>
            {isLoading && (
              <svg className="w-5 h-5 ml-2 loading-spinner" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 3v3l4-4-4-4v3c-4.42 0-8 3.58-8 8s3.58 8 8 8c1.57 0 3.04-.46 4.28-1.26l-1.45-1.45C11.76 12.53 10.92 13 10 13c-1.65 0-3-1.35-3-3s1.35-3 3-3z"></path>
              </svg>
            )}
          </button>
        </form>

        {/* Switch to Login */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
              disabled={isLoading}
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