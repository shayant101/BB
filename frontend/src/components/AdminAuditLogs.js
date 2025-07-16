'use client';

import { useState, useEffect } from 'react';
import { adminAPI } from '../lib/api';

export default function AdminAuditLogs() {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    action: '',
    admin_id: '',
    target_user_id: '',
    limit: 50
  });
  const [admins, setAdmins] = useState([]);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchAuditLogs();
    fetchAdmins();
    fetchUsers();
  }, [filters]);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      
      const params = {};
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params[key] = value;
      });
      
      const data = await adminAPI.getAuditLogs(params);
      setAuditLogs(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching audit logs:', error);
      setLoading(false);
    }
  };

  const fetchAdmins = async () => {
    try {
      const data = await adminAPI.getUsers({ role: 'admin' });
      setAdmins(data);
    } catch (error) {
      console.error('Error fetching admins:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const data = await adminAPI.getUsers({ limit: 100 });
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const getActionIcon = (action) => {
    const icons = {
      'system_initialized': '🚀',
      'user_created': '👤',
      'user_deactivated': '🚫',
      'user_reactivated': '✅',
      'impersonation_started': '👥',
      'user_status_updated': '🔄',
      'user_approved': '✅',
      'user_rejected': '❌'
    };
    return icons[action] || '📝';
  };

  const getActionColor = (action) => {
    const colors = {
      'system_initialized': 'bg-blue-100 text-blue-800',
      'user_created': 'bg-green-100 text-green-800',
      'user_deactivated': 'bg-red-100 text-red-800',
      'user_reactivated': 'bg-green-100 text-green-800',
      'impersonation_started': 'bg-yellow-100 text-yellow-800',
      'user_status_updated': 'bg-blue-100 text-blue-800',
      'user_approved': 'bg-green-100 text-green-800',
      'user_rejected': 'bg-red-100 text-red-800'
    };
    return colors[action] || 'bg-gray-100 text-gray-800';
  };

  const formatActionName = (action) => {
    return action.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const exportAuditLogs = () => {
    const csvContent = [
      ['Timestamp', 'Admin', 'Action', 'Target User', 'IP Address', 'Details'],
      ...auditLogs.map(log => [
        new Date(log.created_at).toISOString(),
        log.admin_name,
        formatActionName(log.action),
        log.target_user_name || 'N/A',
        log.ip_address || 'N/A',
        JSON.stringify(log.details || {})
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
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
      {/* Header with Export */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Admin Audit Logs</h2>
            <p className="text-sm text-gray-600 mt-1">
              Complete trail of all administrative actions performed on the platform
            </p>
          </div>
          <button
            onClick={exportAuditLogs}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center"
          >
            📊 Export CSV
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
            <select
              value={filters.action}
              onChange={(e) => setFilters({...filters, action: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Actions</option>
              <option value="system_initialized">System Initialized</option>
              <option value="user_created">User Created</option>
              <option value="user_deactivated">User Deactivated</option>
              <option value="user_reactivated">User Reactivated</option>
              <option value="impersonation_started">Impersonation Started</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Admin</label>
            <select
              value={filters.admin_id}
              onChange={(e) => setFilters({...filters, admin_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Admins</option>
              {admins.map(admin => (
                <option key={admin.id} value={admin.id}>{admin.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target User</label>
            <select
              value={filters.target_user_id}
              onChange={(e) => setFilters({...filters, target_user_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Users</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>{user.name} (@{user.username})</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Limit</label>
            <select
              value={filters.limit}
              onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={25}>25 entries</option>
              <option value={50}>50 entries</option>
              <option value={100}>100 entries</option>
              <option value={200}>200 entries</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Showing {auditLogs.length} audit log entries
          </div>
          <button
            onClick={() => setFilters({action: '', admin_id: '', target_user_id: '', limit: 50})}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Audit Logs Timeline */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Audit Trail</h3>
        </div>
        
        <div className="p-6">
          {auditLogs.length > 0 ? (
            <div className="space-y-6">
              {auditLogs.map((log, index) => (
                <div key={log.id} className="relative">
                  {/* Timeline line */}
                  {index < auditLogs.length - 1 && (
                    <div className="absolute left-6 top-12 w-0.5 h-16 bg-gray-200"></div>
                  )}
                  
                  <div className="flex items-start space-x-4">
                    {/* Timeline dot */}
                    <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-lg ${getActionColor(log.action)}`}>
                      {getActionIcon(log.action)}
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900">
                            {log.admin_name}
                          </span>
                          <span className="text-sm text-gray-500">performed</span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getActionColor(log.action)}`}>
                            {formatActionName(log.action)}
                          </span>
                          {log.target_user_name && (
                            <>
                              <span className="text-sm text-gray-500">on</span>
                              <span className="text-sm font-medium text-blue-600">
                                {log.target_user_name}
                              </span>
                            </>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(log.created_at).toLocaleString()}
                        </div>
                      </div>
                      
                      {/* Details */}
                      {log.details && Object.keys(log.details).length > 0 && (
                        <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                          <h4 className="text-xs font-medium text-gray-700 mb-2">Details:</h4>
                          <div className="space-y-1">
                            {Object.entries(log.details).map(([key, value]) => (
                              <div key={key} className="flex text-xs">
                                <span className="font-medium text-gray-600 w-24 flex-shrink-0">
                                  {key.replace(/_/g, ' ')}:
                                </span>
                                <span className="text-gray-800 break-all">
                                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Metadata */}
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                        {log.ip_address && (
                          <span>IP: {log.ip_address}</span>
                        )}
                        <span>ID: {log.id}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <span className="text-4xl">📋</span>
              <p className="text-gray-500 mt-2">No audit logs found matching your criteria</p>
            </div>
          )}
        </div>
      </div>

      {/* Security Notice */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-blue-400 text-xl">🔒</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Audit Log Security</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc list-inside space-y-1">
                <li><strong>Immutable Records:</strong> Audit logs cannot be modified or deleted</li>
                <li><strong>Complete Traceability:</strong> Every admin action is automatically logged</li>
                <li><strong>Compliance Ready:</strong> Logs include timestamps, IP addresses, and full context</li>
                <li><strong>Export Capability:</strong> Download logs for external analysis or compliance</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold">📊</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Actions</p>
              <p className="text-2xl font-bold text-gray-900">{auditLogs.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">👥</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Unique Admins</p>
              <p className="text-2xl font-bold text-gray-900">
                {new Set(auditLogs.map(log => log.admin_name)).size}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-bold">🕒</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Latest Action</p>
              <p className="text-sm font-bold text-gray-900">
                {auditLogs.length > 0 
                  ? new Date(auditLogs[0].created_at).toLocaleDateString()
                  : 'No actions'
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}