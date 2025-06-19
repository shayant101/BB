'use client';

import { useState, useEffect } from 'react';
import { ordersAPI, profilesAPI } from '../lib/api';
import OrderList from './OrderList';
import NewOrderForm from './NewOrderForm';
import ProfileView from './ProfileView';
import VendorMarketplace from './VendorMarketplace';
import { PlusIcon, UserIcon, BuildingStorefrontIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/outline';
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

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
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
        <h2 className="text-2xl font-bold text-gray-900">Restaurant Dashboard</h2>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowProfile(true)}
            className="btn-secondary flex items-center"
          >
            <UserIcon className="h-5 w-5 mr-2" />
            Profile
          </button>
          <button
            onClick={() => setShowNewOrderForm(true)}
            className="btn-primary flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Order
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Orders</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
              📋
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-orange-600">{stats.pending}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              ⏳
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Confirmed</p>
              <p className="text-2xl font-bold text-blue-600">{stats.confirmed}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              ✅
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Fulfilled</p>
              <p className="text-2xl font-bold text-green-600">{stats.fulfilled}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              🚚
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('orders')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'orders'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ClipboardDocumentListIcon className="h-5 w-5 inline mr-2" />
            Your Orders
          </button>
          <button
            onClick={() => setActiveTab('marketplace')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'marketplace'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <BuildingStorefrontIcon className="h-5 w-5 inline mr-2" />
            Vendor Marketplace
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'orders' && (
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Your Orders</h3>
            <button
              onClick={loadData}
              className="btn-secondary text-sm"
            >
              Refresh
            </button>
          </div>
          
          {orders.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📦</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No orders yet</h3>
              <p className="text-gray-600 mb-6">Discover suppliers in our marketplace or create your first order</p>
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
                  Create First Order
                </button>
              </div>
            </div>
          ) : (
            <OrderList orders={orders} userRole="restaurant" onRefresh={loadData} />
          )}
        </div>
      )}

      {activeTab === 'marketplace' && (
        <VendorMarketplace onCreateOrder={handleCreateOrderFromMarketplace} />
      )}
    </div>
  );
}