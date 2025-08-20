'use client';

import { useState } from 'react';
import { authAPI, setAuthToken, setUser } from '../lib/api';

const EmailLoginForm = ({ onSuccess, onError, onSwitchToRegister }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
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
      // Call the email login API endpoint
      const response = await authAPI.emailLogin(formData.email, formData.password);

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
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.detail || 'Login failed. Please check your credentials and try again.';
      onError?.(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="login-card">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome back</h2>
          <p className="text-gray-600">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
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
              autoComplete="email"
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
              placeholder="Enter your password"
              disabled={isLoading}
              autoComplete="current-password"
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full btn-primary text-lg py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>{isLoading ? 'Signing in...' : 'Sign In'}</span>
            {isLoading && (
              <svg className="w-5 h-5 ml-2 loading-spinner" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 3v3l4-4-4-4v3c-4.42 0-8 3.58-8 8s3.58 8 8 8c1.57 0 3.04-.46 4.28-1.26l-1.45-1.45C11.76 12.53 10.92 13 10 13c-1.65 0-3-1.35-3-3s1.35-3 3-3z"></path>
              </svg>
            )}
          </button>
        </form>

        {/* Forgot Password Link */}
        <div className="mt-4 text-center">
          <button
            type="button"
            className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
            disabled={isLoading}
          >
            Forgot your password?
          </button>
        </div>

        {/* Switch to Register */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
              disabled={isLoading}
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