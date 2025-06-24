'use client';

import { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [actionQueues, setActionQueues] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aiInsights, setAiInsights] = useState([]);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch dashboard stats
      const statsResponse = await fetch('http://localhost:8000/api/admin/dashboard-stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch action queues
      const queuesResponse = await fetch('http://localhost:8000/api/admin/action-queues', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const queuesData = await queuesResponse.json();
      setActionQueues(queuesData);

      // Generate AI insights
      generateAIInsights(statsData, queuesData);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const generateAIInsights = (stats, queues) => {
    const insights = [];

    // Platform Health Insights
    if (stats.stuck_orders_count > 0) {
      insights.push({
        type: 'warning',
        icon: '⚠️',
        title: 'Order Processing Alert',
        message: `${stats.stuck_orders_count} orders have been pending for over 48 hours. Consider reaching out to vendors or restaurants.`,
        priority: 'high'
      });
    }

    // Growth Insights
    if (stats.recent_signups_24h > 0) {
      const growthRate = (stats.recent_signups_24h / stats.total_users * 100).toFixed(1);
      insights.push({
        type: 'success',
        icon: '📈',
        title: 'Growth Momentum',
        message: `${stats.recent_signups_24h} new users joined in the last 24 hours (${growthRate}% daily growth rate).`,
        priority: 'medium'
      });
    }

    // Vendor Approval Insights
    if (stats.pending_vendor_approvals > 0) {
      insights.push({
        type: 'info',
        icon: '👥',
        title: 'Vendor Pipeline',
        message: `${stats.pending_vendor_approvals} vendors awaiting approval. Quick approvals can boost marketplace diversity.`,
        priority: 'medium'
      });
    }

    // Platform Balance Insights
    const restaurantVendorRatio = (stats.total_restaurants / stats.total_vendors).toFixed(2);
    if (restaurantVendorRatio > 2) {
      insights.push({
        type: 'info',
        icon: '⚖️',
        title: 'Market Balance',
        message: `Restaurant-to-vendor ratio is ${restaurantVendorRatio}:1. Consider vendor acquisition campaigns.`,
        priority: 'low'
      });
    }

    // Order Volume Insights
    const ordersPerUser = (stats.total_orders / stats.total_users).toFixed(1);
    if (ordersPerUser > 2) {
      insights.push({
        type: 'success',
        icon: '🎯',
        title: 'High Engagement',
        message: `Average ${ordersPerUser} orders per user indicates strong platform engagement.`,
        priority: 'low'
      });
    }

    // Security Insights
    if (stats.active_impersonation_sessions > 0) {
      insights.push({
        type: 'warning',
        icon: '🔒',
        title: 'Active Admin Sessions',
        message: `${stats.active_impersonation_sessions} impersonation sessions active. Monitor for security.`,
        priority: 'high'
      });
    }

    setAiInsights(insights.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Chart configurations
  const userDistributionData = {
    labels: ['Restaurants', 'Vendors'],
    datasets: [{
      data: [stats?.total_restaurants || 0, stats?.total_vendors || 0],
      backgroundColor: ['#3B82F6', '#10B981'],
      borderWidth: 0,
    }]
  };

  const platformMetricsData = {
    labels: ['Total Users', 'Total Orders', 'Pending Approvals', 'Recent Signups'],
    datasets: [{
      label: 'Platform Metrics',
      data: [
        stats?.total_users || 0,
        stats?.total_orders || 0,
        stats?.pending_vendor_approvals || 0,
        stats?.recent_signups_24h || 0
      ],
      backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
      borderRadius: 8,
    }]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* AI Insights Panel */}
      {aiInsights.length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            🤖 AI Platform Insights
          </h3>
          <div className="grid gap-4 md:grid-cols-2">
            {aiInsights.slice(0, 4).map((insight, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  insight.type === 'warning' ? 'bg-yellow-50 border-yellow-400' :
                  insight.type === 'success' ? 'bg-green-50 border-green-400' :
                  'bg-blue-50 border-blue-400'
                }`}
              >
                <div className="flex items-start">
                  <span className="text-2xl mr-3">{insight.icon}</span>
                  <div>
                    <h4 className="font-medium text-gray-900">{insight.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{insight.message}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold">👥</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.total_users || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">📦</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Orders</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.total_orders || 0}</p>
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
              <p className="text-sm font-medium text-gray-500">Pending Approvals</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.pending_vendor_approvals || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-bold">🆕</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">New Users (24h)</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.recent_signups_24h || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User Distribution</h3>
          <div className="h-64">
            <Doughnut data={userDistributionData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Metrics</h3>
          <div className="h-64">
            <Bar data={platformMetricsData} options={{ ...chartOptions, maintainAspectRatio: false }} />
          </div>
        </div>
      </div>

      {/* Action Queues */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Vendors */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <span className="mr-2">👥</span>
              Pending Vendor Approvals
              {actionQueues?.pending_vendors?.length > 0 && (
                <span className="ml-2 bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                  {actionQueues.pending_vendors.length}
                </span>
              )}
            </h3>
          </div>
          <div className="p-6">
            {actionQueues?.pending_vendors?.length > 0 ? (
              <div className="space-y-4">
                {actionQueues.pending_vendors.map((vendor) => (
                  <div key={vendor.id} className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                    <div>
                      <h4 className="font-medium text-gray-900">{vendor.name}</h4>
                      <p className="text-sm text-gray-600">{vendor.email}</p>
                      <p className="text-xs text-gray-500">Pending for {vendor.days_pending} days</p>
                    </div>
                    <div className="flex space-x-2">
                      <button className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm">
                        Approve
                      </button>
                      <button className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm">
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No pending vendor approvals</p>
            )}
          </div>
        </div>

        {/* Stuck Orders */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <span className="mr-2">⚠️</span>
              Stuck Orders ({'>'}48h)
              {actionQueues?.stuck_orders?.length > 0 && (
                <span className="ml-2 bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                  {actionQueues.stuck_orders.length}
                </span>
              )}
            </h3>
          </div>
          <div className="p-6">
            {actionQueues?.stuck_orders?.length > 0 ? (
              <div className="space-y-4">
                {actionQueues.stuck_orders.map((order) => (
                  <div key={order.id} className="p-4 bg-red-50 rounded-lg border border-red-200">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-gray-900">Order #{order.id}</h4>
                        <p className="text-sm text-gray-600">{order.restaurant_name} → {order.vendor_name}</p>
                        <p className="text-xs text-gray-500">Stuck for {order.hours_stuck} hours</p>
                        <p className="text-sm text-gray-700 mt-1">{order.items_text}</p>
                      </div>
                      <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
                        Investigate
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl">✅</span>
                <p className="text-gray-500 mt-2">No stuck orders - all systems running smoothly!</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Real-time Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Live - Updates every 30s</span>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats?.active_impersonation_sessions || 0}</div>
            <div className="text-sm text-gray-500">Active Sessions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats?.total_restaurants || 0}</div>
            <div className="text-sm text-gray-500">Restaurants</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{stats?.total_vendors || 0}</div>
            <div className="text-sm text-gray-500">Vendors</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {stats ? Math.round((stats.total_orders / stats.total_users) * 10) / 10 : 0}
            </div>
            <div className="text-sm text-gray-500">Avg Orders/User</div>
          </div>
        </div>
      </div>
    </div>
  );
}