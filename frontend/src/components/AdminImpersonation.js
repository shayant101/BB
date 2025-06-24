'use client';

import { useState, useEffect } from 'react';

export default function AdminImpersonation() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeSession, setActiveSession] = useState(null);
  const [impersonationHistory, setImpersonationHistory] = useState([]);

  useEffect(() => {
    fetchUsers();
    fetchImpersonationHistory();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await fetch(`http://localhost:8000/api/admin/users?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        // Filter out admin users for impersonation
        setUsers(data.filter(user => user.role !== 'admin'));
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching users:', error);
      setLoading(false);
    }
  };

  const fetchImpersonationHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/admin/audit-logs?action=impersonation_started&limit=10', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setImpersonationHistory(data);
      }
    } catch (error) {
      console.error('Error fetching impersonation history:', error);
    }
  };

  const startImpersonation = async (user, reason) => {
    if (!reason.trim()) {
      alert('Please provide a reason for impersonation');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/admin/users/${user.id}/impersonate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          target_user_id: user.id,
          reason: reason
        })
      });

      if (response.ok) {
        const data = await response.json();
        setActiveSession({
          ...data,
          startTime: new Date(),
          user: user
        });
        
        // Store impersonation token temporarily
        sessionStorage.setItem('impersonation_token', data.impersonation_token);
        sessionStorage.setItem('impersonation_user', JSON.stringify(user));
        
        alert(`Impersonation session started for ${user.name}. Session expires in 5 minutes.`);
        fetchImpersonationHistory(); // Refresh history
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'Failed to start impersonation'}`);
      }
    } catch (error) {
      console.error('Error starting impersonation:', error);
      alert('Error starting impersonation session');
    }
  };

  const endImpersonation = () => {
    sessionStorage.removeItem('impersonation_token');
    sessionStorage.removeItem('impersonation_user');
    setActiveSession(null);
    alert('Impersonation session ended');
  };

  const openUserInterface = () => {
    if (activeSession) {
      // Open new window/tab with impersonation token
      const impersonationToken = sessionStorage.getItem('impersonation_token');
      const newWindow = window.open('/dashboard', '_blank');
      
      // Set the impersonation token in the new window
      setTimeout(() => {
        if (newWindow) {
          newWindow.localStorage.setItem('token', impersonationToken);
          newWindow.location.reload();
        }
      }, 1000);
    }
  };

  const getRoleBadge = (role) => {
    const colors = {
      restaurant: 'bg-blue-100 text-blue-800',
      vendor: 'bg-purple-100 text-purple-800'
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[role] || 'bg-gray-100 text-gray-800'}`}>
        {role.charAt(0).toUpperCase() + role.slice(1)}
      </span>
    );
  };

  const getStatusBadge = (status, isActive) => {
    if (!isActive) {
      return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Inactive</span>;
    }
    
    switch (status) {
      case 'active':
        return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Active</span>;
      case 'pending_approval':
        return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">Pending</span>;
      default:
        return <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Active Session Alert */}
      {activeSession && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-yellow-400 text-xl">⚠️</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Active Impersonation Session
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>Currently impersonating: <strong>{activeSession.user.name}</strong> ({activeSession.user.username})</p>
                  <p>Session expires at: <strong>{new Date(activeSession.expires_at).toLocaleTimeString()}</strong></p>
                </div>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={openUserInterface}
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
              >
                Open User Interface
              </button>
              <button
                onClick={endImpersonation}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
              >
                End Session
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Security Warning */}
      <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-red-400 text-xl">🔒</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Security Notice</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>User impersonation is a powerful admin tool. Use responsibly:</p>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li>Only impersonate users for legitimate support purposes</li>
                <li>Sessions automatically expire after 5 minutes</li>
                <li>All impersonation activities are logged and audited</li>
                <li>Always provide a clear reason for impersonation</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Search and User Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Start Impersonation Session</h2>
        
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search users to impersonate..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              fetchUsers();
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                          <span className="text-sm font-medium text-gray-700">
                            {user.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{user.name}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                        <div className="text-xs text-gray-400">@{user.username}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getRoleBadge(user.role)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(user.status, user.is_active)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        const reason = prompt(`Reason for impersonating ${user.name}:`);
                        if (reason) startImpersonation(user, reason);
                      }}
                      disabled={!user.is_active || activeSession}
                      className={`px-3 py-1 rounded text-sm ${
                        user.is_active && !activeSession
                          ? 'bg-blue-600 hover:bg-blue-700 text-white'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      {activeSession ? 'Session Active' : 'Impersonate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Impersonation History */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Impersonation History</h3>
        
        {impersonationHistory.length > 0 ? (
          <div className="space-y-4">
            {impersonationHistory.map((log) => (
              <div key={log.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-900">
                        {log.admin_name}
                      </span>
                      <span className="text-sm text-gray-500">impersonated</span>
                      <span className="text-sm font-medium text-blue-600">
                        {log.target_user_name}
                      </span>
                    </div>
                    <div className="mt-1 text-sm text-gray-600">
                      <strong>Reason:</strong> {log.details?.reason || 'No reason provided'}
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                      {log.details?.expires_at && (
                        <span className="ml-2">
                          • Expired: {new Date(log.details.expires_at).toLocaleTimeString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                      Completed
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No impersonation history found</p>
        )}
      </div>

      {/* Best Practices */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-blue-400 text-xl">💡</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Impersonation Best Practices</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc list-inside space-y-1">
                <li><strong>Document everything:</strong> Always provide a clear, specific reason</li>
                <li><strong>Minimize duration:</strong> Complete your investigation quickly</li>
                <li><strong>Respect privacy:</strong> Only access information relevant to the issue</li>
                <li><strong>Communicate:</strong> Inform the user if appropriate after resolution</li>
                <li><strong>Follow up:</strong> Document findings and actions taken</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}