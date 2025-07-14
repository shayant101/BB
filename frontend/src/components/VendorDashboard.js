'use client';

import { useState, useEffect } from 'react';
import { ordersAPI } from '../lib/api';
import OrderList from './OrderList';
import ProfileView from './ProfileView';
import { UserIcon } from '@heroicons/react/24/outline';

export default function VendorDashboard({ user }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showProfile, setShowProfile] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    confirmed: 0,
    fulfilled: 0
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const ordersData = await ordersAPI.getOrders();
      setOrders(ordersData);
      
      // Calculate stats
      const stats = ordersData.reduce((acc, order) => {
        acc.total++;
        acc[order.status]++;
        return acc;
      }, { total: 0, pending: 0, confirmed: 0, fulfilled: 0 });
      
      setStats(stats);
    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-gray-600">Loading incoming orders...</p>
      </div>
    );
  }

  if (showProfile) {
    return (
      <ProfileView 
        onBack={() => setShowProfile(false)}
        onProfileUpdated={loadData}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Vendor Dashboard</h2>
          <p className="text-sm text-gray-600 mt-1">Manage incoming orders from restaurants</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowProfile(true)}
            className="btn-secondary flex items-center"
          >
            <UserIcon className="h-4 w-4 mr-2" />
            Profile
          </button>
        </div>
      </div>

      {/* Stats Cards - Modern Style matching Admin Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-gray-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                <span className="text-gray-600 font-bold">📋</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Orders</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-600 font-bold">⏳</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold">✅</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Confirmed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.confirmed}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">🚚</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Fulfilled</p>
              <p className="text-2xl font-bold text-gray-900">{stats.fulfilled}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Orders List - Modern Card Style */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Incoming Orders</h3>
            <button
              onClick={loadData}
              className="btn-secondary text-sm"
            >
              Refresh
            </button>
          </div>
        </div>
        <div className="p-6">
          {orders.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📦</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No orders received</h3>
              <p className="text-gray-600">Orders from restaurants will appear here</p>
            </div>
          ) : (
            <OrderList orders={orders} userRole="vendor" onRefresh={loadData} />
          )}
        </div>
      </div>
    </div>
  );
}