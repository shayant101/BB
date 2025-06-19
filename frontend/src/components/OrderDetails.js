'use client';

import { useState } from 'react';
import { ordersAPI } from '../lib/api';
import { 
  ArrowLeftIcon,
  ClockIcon, 
  CheckCircleIcon, 
  TruckIcon,
  PhoneIcon,
  EnvelopeIcon,
  MapPinIcon,
  PencilIcon
} from '@heroicons/react/24/outline';

export default function OrderDetails({ order, userRole, onBack, onOrderUpdated }) {
  const [updating, setUpdating] = useState(false);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notes, setNotes] = useState(order.notes || '');

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-6 w-6 text-orange-500" />;
      case 'confirmed':
        return <CheckCircleIcon className="h-6 w-6 text-blue-500" />;
      case 'fulfilled':
        return <TruckIcon className="h-6 w-6 text-green-500" />;
      default:
        return <ClockIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending':
        return 'status-badge status-pending text-lg px-4 py-2';
      case 'confirmed':
        return 'status-badge status-confirmed text-lg px-4 py-2';
      case 'fulfilled':
        return 'status-badge status-fulfilled text-lg px-4 py-2';
      default:
        return 'status-badge bg-gray-100 text-gray-800 text-lg px-4 py-2';
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    if (updating) return;
    
    setUpdating(true);
    try {
      const updatedOrder = await ordersAPI.updateOrderStatus(order.id, newStatus);
      onOrderUpdated(updatedOrder);
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update order status');
    } finally {
      setUpdating(false);
    }
  };

  const handleNotesUpdate = async () => {
    if (updating) return;
    
    setUpdating(true);
    try {
      const updatedOrder = await ordersAPI.updateOrderNotes(order.id, notes);
      onOrderUpdated(updatedOrder);
      setEditingNotes(false);
    } catch (error) {
      console.error('Error updating notes:', error);
      alert('Failed to update notes');
    } finally {
      setUpdating(false);
    }
  };

  const getAvailableStatuses = (currentStatus) => {
    const statuses = [
      { value: 'pending', label: 'Pending', color: 'orange' },
      { value: 'confirmed', label: 'Confirmed', color: 'blue' },
      { value: 'fulfilled', label: 'Fulfilled', color: 'green' }
    ];
    
    return statuses.filter(status => status.value !== currentStatus);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const otherParty = userRole === 'restaurant' ? order.vendor : order.restaurant;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="btn-secondary flex items-center"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back
          </button>
          <h2 className="text-2xl font-bold text-gray-900">Order #{order.id}</h2>
        </div>
        
        <div className="flex items-center space-x-3">
          {getStatusIcon(order.status)}
          <span className={getStatusBadgeClass(order.status)}>
            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Order Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Order Items */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Items</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                {order.items_text}
              </pre>
            </div>
          </div>

          {/* Notes Section */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Notes</h3>
              <button
                onClick={() => setEditingNotes(!editingNotes)}
                className="btn-secondary text-sm flex items-center"
              >
                <PencilIcon className="h-4 w-4 mr-1" />
                {editingNotes ? 'Cancel' : 'Edit'}
              </button>
            </div>
            
            {editingNotes ? (
              <div className="space-y-3">
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="form-textarea h-32"
                  placeholder="Add notes about this order..."
                />
                <div className="flex space-x-2">
                  <button
                    onClick={handleNotesUpdate}
                    disabled={updating}
                    className="btn-primary"
                  >
                    {updating ? 'Saving...' : 'Save Notes'}
                  </button>
                  <button
                    onClick={() => {
                      setEditingNotes(false);
                      setNotes(order.notes || '');
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 p-4 rounded-lg min-h-24">
                {order.notes ? (
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{order.notes}</p>
                ) : (
                  <p className="text-sm text-gray-500 italic">No notes added yet</p>
                )}
              </div>
            )}
          </div>

          {/* Order Timeline */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Timeline</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                <div className="text-sm">
                  <span className="font-medium">Order Created</span>
                  <span className="text-gray-500 ml-2">{formatDate(order.created_at)}</span>
                </div>
              </div>
              {order.updated_at !== order.created_at && (
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <div className="text-sm">
                    <span className="font-medium">Last Updated</span>
                    <span className="text-gray-500 ml-2">{formatDate(order.updated_at)}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Contact Information */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {userRole === 'restaurant' ? 'Vendor' : 'Restaurant'} Details
            </h3>
            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-gray-900">{otherParty.name}</h4>
                {otherParty.description && (
                  <p className="text-sm text-gray-600 mt-1">{otherParty.description}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <a
                  href={`tel:${otherParty.phone}`}
                  className="flex items-center text-sm text-primary hover:text-blue-600"
                >
                  <PhoneIcon className="h-4 w-4 mr-2" />
                  {otherParty.phone}
                </a>
                
                <a
                  href={`mailto:${otherParty.email}`}
                  className="flex items-center text-sm text-primary hover:text-blue-600"
                >
                  <EnvelopeIcon className="h-4 w-4 mr-2" />
                  {otherParty.email}
                </a>
                
                <div className="flex items-start text-sm text-gray-600">
                  <MapPinIcon className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                  <span>{otherParty.address}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Status Management (Vendors Only) */}
          {userRole === 'vendor' && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Update Status</h3>
              <div className="space-y-2">
                {getAvailableStatuses(order.status).map(status => (
                  <button
                    key={status.value}
                    onClick={() => handleStatusUpdate(status.value)}
                    disabled={updating}
                    className={`w-full btn-${status.color === 'orange' ? 'warning' : status.color === 'blue' ? 'primary' : 'success'} ${
                      updating ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {updating ? 'Updating...' : `Mark as ${status.label}`}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}