'use client';

import { useState } from 'react';
import { ordersAPI } from '../lib/api';
import {
  ClockIcon,
  CheckCircleIcon,
  TruckIcon,
  PhoneIcon,
  EnvelopeIcon,
  MapPinIcon,
  CalendarDaysIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export default function OrderCard({ order, userRole, onClick, onStatusUpdate }) {
  const [updating, setUpdating] = useState(false);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-5 w-5" />;
      case 'confirmed':
        return <CheckCircleIcon className="h-5 w-5" />;
      case 'fulfilled':
        return <TruckIcon className="h-5 w-5" />;
      default:
        return <ClockIcon className="h-5 w-5" />;
    }
  };

  const isUrgent = () => {
    const now = new Date();
    const orderDate = new Date(order.created_at);
    const hoursSinceOrder = (now - orderDate) / (1000 * 60 * 60);
    
    return (order.status === 'pending' && hoursSinceOrder > 24) ||
           (order.status === 'confirmed' && order.expected_delivery && new Date(order.expected_delivery) < now);
  };

  const handleStatusUpdate = async (newStatus) => {
    if (updating) return;
    
    setUpdating(true);
    try {
      await ordersAPI.updateOrderStatus(order.id, newStatus);
      onStatusUpdate();
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update order status');
    } finally {
      setUpdating(false);
    }
  };

  const getNextStatus = (currentStatus) => {
    switch (currentStatus) {
      case 'pending':
        return 'confirmed';
      case 'confirmed':
        return 'fulfilled';
      default:
        return null;
    }
  };

  const getNextStatusLabel = (currentStatus) => {
    switch (currentStatus) {
      case 'pending':
        return 'Confirm Order';
      case 'confirmed':
        return 'Mark Fulfilled';
      default:
        return null;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateItems = (items, maxLength = 100) => {
    if (items.length <= maxLength) return items;
    return items.substring(0, maxLength) + '...';
  };

  const otherParty = userRole === 'restaurant' ? order.vendor : order.restaurant;

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 cursor-pointer transition-all duration-200 hover:shadow-md hover:border-gray-300 hover:-translate-y-0.5 relative ${isUrgent() ? 'border-red-300 bg-red-50' : ''}`} onClick={onClick}>
      {/* Urgency Indicator */}
      {isUrgent() && (
        <div className="absolute -top-2 -right-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 shadow-md z-10">
          <ExclamationTriangleIcon className="h-3 w-3" />
          URGENT
        </div>
      )}
      
      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start mb-4">
        {/* Left Column - Primary Info */}
        <div className="space-y-2">
          <div className="text-lg font-semibold text-gray-900">
            {otherParty.name}
          </div>
          
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <span className="font-medium">#{order.id}</span>
            <span>•</span>
            <span>{formatDate(order.created_at)}</span>
          </div>

          {/* Expected Delivery */}
          {order.expected_delivery && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <CalendarDaysIcon className="h-4 w-4" />
              <span>Expected: {formatDate(order.expected_delivery)}</span>
            </div>
          )}
        </div>

        {/* Right Column - Status & Actions */}
        <div className="flex flex-col items-end gap-3">
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
            order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
            order.status === 'confirmed' ? 'bg-blue-100 text-blue-800' :
            order.status === 'fulfilled' ? 'bg-green-100 text-green-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {getStatusIcon(order.status)}
            <span>{order.status.charAt(0).toUpperCase() + order.status.slice(1)}</span>
            {order.status === 'pending' && <div className="w-2 h-2 bg-yellow-600 rounded-full blink-dot ml-1"></div>}
          </div>

          {/* Quick Actions for Vendors */}
          {userRole === 'vendor' && getNextStatus(order.status) && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleStatusUpdate(getNextStatus(order.status));
              }}
              disabled={updating}
              className={`btn-success text-sm px-4 py-2 ${updating ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {updating ? (
                <div className="flex items-center gap-2">
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  Updating...
                </div>
              ) : (
                getNextStatusLabel(order.status)
              )}
            </button>
          )}
        </div>
      </div>

      {/* Order Items - Condensed */}
      <div className="bg-gray-50 rounded-lg p-3 mb-4">
        <p className="text-sm text-gray-700 leading-relaxed">
          {truncateItems(order.items_text, 120)}
        </p>
      </div>

      {/* Contact Actions - Interactive */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <a
            href={`tel:${otherParty.phone}`}
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-colors"
          >
            <PhoneIcon className="h-4 w-4" />
            Call
          </a>
          
          <a
            href={`mailto:${otherParty.email}`}
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-colors"
          >
            <EnvelopeIcon className="h-4 w-4" />
            Email
          </a>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-500">
          <MapPinIcon className="h-4 w-4" />
          <span>{otherParty.address.split(',')[0]}</span>
        </div>
      </div>
    </div>
  );
}