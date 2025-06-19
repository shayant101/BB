'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI, setAuthToken, setUser } from '../lib/api';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(username, password);
      
      // Store token and user info
      setAuthToken(response.access_token);
      setUser({
        id: response.user_id,
        role: response.role,
        name: response.name
      });

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCredentials = (role) => {
    if (role === 'restaurant') {
      setUsername('restaurant1');
      setPassword('demo123');
    } else if (role === 'vendor') {
      setUsername('vendor1');
      setPassword('demo123');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">BistroBoard</h1>
          <p className="text-gray-600">Restaurant-Supplier Order Management</p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="form-input"
                placeholder="Enter your username"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                placeholder="Enter your password"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-4 text-center">Demo Accounts:</p>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => fillDemoCredentials('restaurant')}
                className="btn-secondary text-sm"
              >
                Restaurant Demo
              </button>
              <button
                type="button"
                onClick={() => fillDemoCredentials('vendor')}
                className="btn-secondary text-sm"
              >
                Vendor Demo
              </button>
            </div>
            <div className="mt-3 text-xs text-gray-500 text-center">
              <p>Restaurant: Mario's Pizzeria</p>
              <p>Vendor: Fresh Valley Produce</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}