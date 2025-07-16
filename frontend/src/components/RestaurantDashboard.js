'use client';

import { useState, useEffect } from 'react';
import { ordersAPI, profilesAPI } from '../lib/api';
import OrderList from './OrderList';
import NewOrderForm from './NewOrderForm';
import ProfileView from './ProfileView';
import VendorMarketplace from './VendorMarketplace';
import {
  PlusIcon,
  UserIcon,
  BuildingStorefrontIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  TruckIcon
} from '@heroicons/react/24/outline';
import { useRouter } from 'next/navigation';

export default function RestaurantDashboard({ user }) {
  const router = useRouter();
  const [orders, setOrders] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewOrderForm, setShowNewOrderForm] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [activeTab, setActiveTab] = useState('orders'); // 'orders' or 'marketplace'
  const [preselectedVendor, setPreselectedVendor] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    confirmed: 0,
    fulfilled: 0
  });
  const [actionItems, setActionItems] = useState([]);

  useEffect(() => {
    // Ensure token is properly set before loading data
    const initializeAndLoadData = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        // Import api module and ensure token is set in axios instance
        const api = (await import('../lib/api')).default;
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // Small delay to ensure token is properly set
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      loadData();
    };
    
    initializeAndLoadData();
  }, []);

  const loadData = async () => {
    try {
      // Double-check token is set before making API calls
      const token = localStorage.getItem('token');
      if (token) {
        const api = (await import('../lib/api')).default;
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      }
      
      const [ordersData, vendorsData] = await Promise.all([
        ordersAPI.getOrders(),
        profilesAPI.getVendors()
      ]);
      
      setOrders(ordersData);
      setVendors(vendorsData);
      
      // Calculate stats
      const stats = ordersData.reduce((acc, order) => {
        acc.total++;
        acc[order.status]++;
        return acc;
      }, { total: 0, pending: 0, confirmed: 0, fulfilled: 0 });
      
      setStats(stats);

      // Calculate action items (orders that need attention)
      const now = new Date();
      const actionItems = ordersData.filter(order => {
        const orderDate = new Date(order.created_at);
        const hoursSinceOrder = (now - orderDate) / (1000 * 60 * 60);
        
        // Orders pending for more than 24 hours or late deliveries
        return (order.status === 'pending' && hoursSinceOrder > 24) ||
               (order.status === 'confirmed' && order.expected_delivery && new Date(order.expected_delivery) < now);
      });
      
      setActionItems(actionItems);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOrderCreated = (newOrder) => {
    setOrders([newOrder, ...orders]);
    setStats(prev => ({
      ...prev,
      total: prev.total + 1,
      pending: prev.pending + 1
    }));
    setShowNewOrderForm(false);
    setPreselectedVendor(null);
    setActiveTab('orders'); // Switch back to orders tab after creating order
  };

  const handleCreateOrderFromMarketplace = (vendor) => {
    // Pre-select vendor and show new order form
    setPreselectedVendor(vendor);
    setShowNewOrderForm(true);
    setActiveTab('orders');
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-gray-600">Loading your orders...</p>
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

  if (showNewOrderForm) {
    return (
      <NewOrderForm
        vendors={vendors}
        onOrderCreated={handleOrderCreated}
        onCancel={() => {
          setShowNewOrderForm(false);
          setPreselectedVendor(null);
        }}
        preselectedVendor={preselectedVendor}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Restaurant Dashboard</h2>
          <p className="text-sm text-gray-600 mt-1">Manage your supply orders and vendors</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowProfile(true)}
            className="btn-secondary flex items-center"
          >
            <UserIcon className="h-4 w-4 mr-2" />
            Profile
          </button>
          <button
            onClick={() => setShowNewOrderForm(true)}
            className="btn-primary flex items-center"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Place Order
          </button>
        </div>
      </div>
      {/* Action Items Section - Interactive Style */}
      {actionItems.length > 0 && (
        <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-6 border border-red-200 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center shadow-sm">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                Action Required
                <div className="w-2 h-2 bg-red-500 rounded-full blink-dot"></div>
              </h3>
              <p className="text-sm text-gray-600">
                {actionItems.length} order{actionItems.length > 1 ? 's' : ''} need{actionItems.length === 1 ? 's' : ''} your attention
              </p>
            </div>
          </div>
          
          <div className="space-y-3">
            {actionItems.map((order, index) => (
              <div key={order.id} className="bg-white rounded-xl p-4 border border-red-200 cursor-pointer hover:shadow-md hover:border-red-300 transition-all duration-200 hover:-translate-y-0.5"
                   onClick={() => setActiveTab('orders')}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-2 h-2 bg-red-500 rounded-full blink-dot"></div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {order.vendor.name}
                      </p>
                      <p className="text-sm text-gray-600">
                        Order #{order.id} • {order.status === 'pending' ? 'Pending 24+ hours' : 'Delivery overdue'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`status-${order.status} px-3 py-1 rounded-full text-xs font-medium`}>
                      {order.status.toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status Overview - Interactive Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-gray-500 hover-lift slide-in">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center shadow-sm">
                <ClipboardDocumentListIcon className="h-5 w-5 text-gray-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Orders</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className={`bg-white rounded-xl shadow-sm p-6 border-l-4 border-yellow-500 hover-lift slide-in`} style={{animationDelay: '0.1s'}}>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className={`w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center shadow-sm`}>
                <ClockIcon className="h-5 w-5 text-yellow-600" />
              </div>
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500 flex items-center gap-2">
                Pending
                {stats.pending > 0 && <div className="w-2 h-2 bg-yellow-500 rounded-full blink-dot"></div>}
              </div>
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
            </div>
          </div>
        </div>

        <div className={`bg-white rounded-xl shadow-sm p-6 border-l-4 border-blue-500 hover-lift slide-in`} style={{animationDelay: '0.2s'}}>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center shadow-sm">
                <CheckCircleIcon className="h-5 w-5 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Confirmed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.confirmed}</p>
            </div>
          </div>
        </div>

        <div className={`bg-white rounded-xl shadow-sm p-6 border-l-4 border-green-500 hover-lift slide-in`} style={{animationDelay: '0.3s'}}>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center shadow-sm">
                <TruckIcon className="h-5 w-5 text-green-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Fulfilled</p>
              <p className="text-2xl font-bold text-gray-900">{stats.fulfilled}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation - Interactive Style */}
      <div className="bg-white rounded-xl shadow-sm p-1 flex space-x-1 border border-gray-200">
        <button
          onClick={() => setActiveTab('orders')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium text-sm transition-all duration-200 ${
            activeTab === 'orders'
              ? 'bg-blue-600 text-white shadow-md'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
          }`}
        >
          <ClipboardDocumentListIcon className="h-5 w-5" />
          <span>All Orders</span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium shadow-sm ${
            activeTab === 'orders'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-600'
          }`}>
            {orders.length}
          </span>
          {orders.length > 0 && activeTab !== 'orders' && <div className="w-2 h-2 bg-blue-500 rounded-full blink-dot ml-1"></div>}
        </button>
        <button
          onClick={() => setActiveTab('marketplace')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium text-sm transition-all duration-200 ${
            activeTab === 'marketplace'
              ? 'bg-blue-600 text-white shadow-md'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
          }`}
        >
          <BuildingStorefrontIcon className="h-5 w-5" />
          <span>Marketplace</span>
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'orders' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">
                Active Orders
              </h3>
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
                <h3 className="text-lg font-medium text-gray-900 mb-2">No orders yet</h3>
                <p className="text-gray-600 mb-6">Start by browsing suppliers or placing your first order</p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <button
                    onClick={() => setActiveTab('marketplace')}
                    className="btn-secondary flex items-center justify-center"
                  >
                    <BuildingStorefrontIcon className="h-5 w-5 mr-2" />
                    Browse Marketplace
                  </button>
                  <button
                    onClick={() => setShowNewOrderForm(true)}
                    className="btn-primary flex items-center justify-center"
                  >
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Place First Order
                  </button>
                </div>
              </div>
            ) : (
              <OrderList orders={orders} userRole="restaurant" onRefresh={loadData} />
            )}
          </div>
        </div>
      )}

      {activeTab === 'marketplace' && (
        <VendorMarketplace onCreateOrder={handleCreateOrderFromMarketplace} />
      )}
    </div>
  );
}