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
        return <ClockIcon className="h-4 w-4" />;
      case 'confirmed':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'fulfilled':
        return <TruckIcon className="h-4 w-4" />;
      default:
        return <ClockIcon className="h-4 w-4" />;
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending':
        return 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-amber-100 text-amber-800';
      case 'confirmed':
        return 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800';
      case 'fulfilled':
        return 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-green-100 text-green-800';
      default:
        return 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-gray-100 text-gray-800';
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
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer" onClick={onClick}>
      {/* Header Section */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="text-xl font-bold text-gray-900">
              Order #{order.id}
            </h3>
            <div className={getStatusBadgeClass(order.status)}>
              {getStatusIcon(order.status)}
              <span className="capitalize">{order.status}</span>
            </div>
          </div>
          
          <div className="space-y-1">
            <div className="text-sm text-gray-600">
              <span className="font-medium">
                {userRole === 'restaurant' ? 'To: ' : 'From: '}
              </span>
              <span className="font-semibold text-gray-900">{otherParty.name}</span>
            </div>
            
            <div className="text-sm text-gray-500">
              {formatDate(order.created_at)}
            </div>
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
            className={`btn-primary text-sm flex items-center gap-2 ${updating ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {updating ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Updating...
              </>
            ) : (
              getNextStatusLabel(order.status)
            )}
          </button>
        )}
      </div>

      {/* Order Items Section */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Items:</h4>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
            {truncateItems(order.items_text)}
          </p>
        </div>
      </div>

      {/* Notes Section */}
      {order.notes && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Notes:</h4>
          <div className="bg-blue-50 rounded-lg p-3">
            <p className="text-sm text-gray-700 leading-relaxed">
              {truncateItems(order.notes, 80)}
            </p>
          </div>
        </div>
      )}

      {/* Contact Info Section */}
      <div className="border-t border-gray-200 pt-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <a 
              href={`tel:${otherParty.phone}`}
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              <PhoneIcon className="h-4 w-4" />
              <span>{otherParty.phone}</span>
            </a>
            
            <a 
              href={`mailto:${otherParty.email}`}
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-2 text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              <EnvelopeIcon className="h-4 w-4" />
              <span>Email</span>
            </a>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <MapPinIcon className="h-4 w-4 flex-shrink-0" />
            <span className="truncate max-w-32">{otherParty.address.split(',')[0]}</span>
          </div>
        </div>
      </div>
    </div>
  );
}