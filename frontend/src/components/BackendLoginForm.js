'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const BackendLoginForm = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();
      
      // Store the token and user info in the format expected by the admin page
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify({
        id: data.user_id,
        name: data.name,
        role: data.role
      }));

      // Redirect based on role
      if (data.role === 'admin') {
        router.push('/admin');
      } else {
        router.push('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-lg rounded-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Backend Login</h2>
          <p className="text-gray-600">Sign in with backend credentials</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Username/Email
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              required
              suppressHydrationWarning
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter username or email"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
              suppressHydrationWarning
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 p-4 bg-gray-50 rounded-md">
          <p className="text-sm text-gray-600 font-medium mb-2">Admin Credentials:</p>
          <p className="text-sm text-gray-500">Username: <code className="bg-gray-200 px-1 rounded">admin</code></p>
          <p className="text-sm text-gray-500">Password: <code className="bg-gray-200 px-1 rounded">admin123</code></p>
        </div>
      </div>
    </div>
  );
};

export default BackendLoginForm;