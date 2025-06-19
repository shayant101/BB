'use client';

import { useState } from 'react';
import { ordersAPI } from '../lib/api';
import { 
  ClockIcon, 
  CheckCircleIcon, 
  TruckIcon,
  PhoneIcon,
  EnvelopeIcon,
  MapPinIcon
} from '@heroicons/react/24/outline';

export default function OrderCard({ order, userRole, onClick, onStatusUpdate }) {
  const [updating, setUpdating] = useState(false);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-orange-500" />;
      case 'confirmed':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />;
      case 'fulfilled':
        return <TruckIcon className="h-5 w-5 text-green-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending':
        return 'status-badge status-pending';
      case 'confirmed':
        return 'status-badge status-confirmed';
      case 'fulfilled':
        return 'status-badge status-fulfilled';
      default:
        return 'status-badge bg-gray-100 text-gray-800';
    }
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
    <div className="card hover:shadow-lg transition-shadow cursor-pointer" onClick={onClick}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              Order #{order.id}
            </h3>
            <span className={getStatusBadgeClass(order.status)}>
              {getStatusIcon(order.status)}
              <span className="ml-1 capitalize">{order.status}</span>
            </span>
          </div>
          
          <div className="text-sm text-gray-600 mb-2">
            {userRole === 'restaurant' ? 'To: ' : 'From: '}
            <span className="font-medium text-gray-900">{otherParty.name}</span>
          </div>
          
          <div className="text-sm text-gray-600">
            {formatDate(order.created_at)}
          </div>
        </div>

        {/* Quick Actions for Vendors */}
        {userRole === 'vendor' && getNextStatus(order.status) && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleStatusUpdate(getNextStatus(order.status));
            }}
            disabled={updating}
            className={`btn-primary text-sm ${updating ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {updating ? 'Updating...' : getNextStatusLabel(order.status)}
          </button>
        )}
      </div>

      {/* Order Items Preview */}
      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-1">Items:</p>
        <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
          {truncateItems(order.items_text)}
        </p>
      </div>

      {/* Contact Info */}
      <div className="border-t pt-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center">
              <PhoneIcon className="h-4 w-4 mr-1" />
              <a 
                href={`tel:${otherParty.phone}`}
                onClick={(e) => e.stopPropagation()}
                className="hover:text-primary"
              >
                {otherParty.phone}
              </a>
            </div>
            <div className="flex items-center">
              <EnvelopeIcon className="h-4 w-4 mr-1" />
              <a 
                href={`mailto:${otherParty.email}`}
                onClick={(e) => e.stopPropagation()}
                className="hover:text-primary"
              >
                Email
              </a>
            </div>
          </div>
          
          <div className="flex items-center text-sm text-gray-500">
            <MapPinIcon className="h-4 w-4 mr-1" />
            <span className="truncate max-w-32">{otherParty.address.split(',')[0]}</span>
          </div>
        </div>
      </div>

      {/* Notes Preview */}
      {order.notes && (
        <div className="mt-3 pt-3 border-t">
          <p className="text-sm font-medium text-gray-700 mb-1">Notes:</p>
          <p className="text-sm text-gray-600">
            {truncateItems(order.notes, 80)}
          </p>
        </div>
      )}
    </div>
  );
}