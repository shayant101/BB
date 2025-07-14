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
    <div className="min-h-screen bg-gray-50">
      {/* Fixed Header */}
      <div className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-black text-gray-900 tracking-tight">
                BistroBoard
              </h1>
              <p className="text-sm text-gray-600 font-medium">Supply Command Center</p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowProfile(true)}
                className="btn-secondary-neo flex items-center"
              >
                <UserIcon className="h-4 w-4 mr-2" />
                Profile
              </button>
              <button
                onClick={() => setShowNewOrderForm(true)}
                className="btn-primary-neo flex items-center"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Place Order
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Action Items Section - Most Important */}
        {actionItems.length > 0 && (
          <div className="action-items-card">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center">
                <ExclamationTriangleIcon className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-black text-gray-900 tracking-tight">
                  ACTION REQUIRED
                </h2>
                <p className="text-sm text-gray-600 font-medium">
                  {actionItems.length} order{actionItems.length > 1 ? 's' : ''} need{actionItems.length === 1 ? 's' : ''} your attention
                </p>
              </div>
            </div>
            
            <div className="space-y-3">
              {actionItems.map(order => (
                <div key={order.id} className="action-item-row" onClick={() => setActiveTab('orders')}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <div>
                        <p className="font-bold text-gray-900">
                          {order.vendor.name}
                        </p>
                        <p className="text-sm text-gray-600">
                          Order #{order.id} • {order.status === 'pending' ? 'Pending 24+ hours' : 'Delivery overdue'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`status-badge-neo status-${order.status}`}>
                        {order.status.toUpperCase()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Status Overview - Clean and Scannable */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="stats-card-neo">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-bold text-gray-600 uppercase tracking-wide">TOTAL</p>
                <p className="text-3xl font-black text-gray-900">{stats.total}</p>
              </div>
              <ClipboardDocumentListIcon className="h-8 w-8 text-gray-400" />
            </div>
          </div>

          <div className="stats-card-neo">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-bold text-amber-600 uppercase tracking-wide">PENDING</p>
                <p className="text-3xl font-black text-amber-600">{stats.pending}</p>
              </div>
              <ClockIcon className="h-8 w-8 text-amber-400" />
            </div>
          </div>

          <div className="stats-card-neo">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-bold text-blue-600 uppercase tracking-wide">CONFIRMED</p>
                <p className="text-3xl font-black text-blue-600">{stats.confirmed}</p>
              </div>
              <CheckCircleIcon className="h-8 w-8 text-blue-400" />
            </div>
          </div>

          <div className="stats-card-neo">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-bold text-green-600 uppercase tracking-wide">FULFILLED</p>
                <p className="text-3xl font-black text-green-600">{stats.fulfilled}</p>
              </div>
              <TruckIcon className="h-8 w-8 text-green-400" />
            </div>
          </div>
        </div>

        {/* Tab Navigation - Neo-Brutalist Style */}
        <div className="tab-navigation-neo">
          <button
            onClick={() => setActiveTab('orders')}
            className={`tab-button-neo ${activeTab === 'orders' ? 'tab-active' : ''}`}
          >
            <ClipboardDocumentListIcon className="h-5 w-5" />
            <span className="font-bold">ALL ORDERS</span>
            <span className="tab-count">{orders.length}</span>
          </button>
          <button
            onClick={() => setActiveTab('marketplace')}
            className={`tab-button-neo ${activeTab === 'marketplace' ? 'tab-active' : ''}`}
          >
            <BuildingStorefrontIcon className="h-5 w-5" />
            <span className="font-bold">MARKETPLACE</span>
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'orders' && (
          <div className="content-section-neo">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-black text-gray-900 tracking-tight">
                ACTIVE ORDERS
              </h3>
              <button
                onClick={loadData}
                className="btn-secondary-neo text-sm"
              >
                Refresh
              </button>
            </div>
            
            {orders.length === 0 ? (
              <div className="empty-state-neo">
                <div className="text-6xl mb-4">📦</div>
                <h3 className="text-xl font-black text-gray-900 mb-2">NO ORDERS YET</h3>
                <p className="text-gray-600 mb-6 font-medium">Start by browsing suppliers or placing your first order</p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <button
                    onClick={() => setActiveTab('marketplace')}
                    className="btn-secondary-neo flex items-center justify-center"
                  >
                    <BuildingStorefrontIcon className="h-5 w-5 mr-2" />
                    Browse Marketplace
                  </button>
                  <button
                    onClick={() => setShowNewOrderForm(true)}
                    className="btn-primary-neo flex items-center justify-center"
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
        )}

        {activeTab === 'marketplace' && (
          <VendorMarketplace onCreateOrder={handleCreateOrderFromMarketplace} />
        )}
      </div>

      {/* Floating Action Button - Always Visible */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setShowNewOrderForm(true)}
          className="floating-action-button"
          title="Place New Order"
        >
          <PlusIcon className="h-6 w-6" />
        </button>
      </div>
    </div>
  );
}