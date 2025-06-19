'use client';

import { useState } from 'react';
import { ordersAPI } from '../lib/api';
import { ArrowLeftIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

export default function NewOrderForm({ vendors, onOrderCreated, onCancel, preselectedVendor = null }) {
  const [selectedVendor, setSelectedVendor] = useState(preselectedVendor ? preselectedVendor.user_id.toString() : '');
  const [itemsText, setItemsText] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedVendor || !itemsText.trim()) {
      setError('Please select a vendor and add items to your order');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const orderData = {
        vendor_id: parseInt(selectedVendor),
        items_text: itemsText.trim(),
        notes: notes.trim()
      };

      const newOrder = await ordersAPI.createOrder(orderData);
      onOrderCreated(newOrder);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create order');
    } finally {
      setLoading(false);
    }
  };

  const selectedVendorData = vendors.find(v => v.id === parseInt(selectedVendor));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onCancel}
            className="btn-secondary flex items-center"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back
          </button>
          <h2 className="text-2xl font-bold text-gray-900">Create New Order</h2>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="card space-y-6">
            {/* Preselected Vendor Notice */}
            {preselectedVendor && (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg flex items-start">
                <InformationCircleIcon className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-medium">Vendor selected from marketplace:</span>
                  <span className="ml-1">{preselectedVendor.name}</span>
                  <p className="text-sm mt-1">You can change the vendor selection below if needed.</p>
                </div>
              </div>
            )}

            {/* Vendor Selection */}
            <div>
              <label htmlFor="vendor" className="block text-sm font-medium text-gray-700 mb-2">
                Select Vendor *
              </label>
              <select
                id="vendor"
                value={selectedVendor}
                onChange={(e) => setSelectedVendor(e.target.value)}
                className="form-select"
                required
              >
                <option value="">Choose a vendor...</option>
                {vendors.map(vendor => (
                  <option key={vendor.id} value={vendor.id}>
                    {vendor.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Items Text Area */}
            <div>
              <label htmlFor="items" className="block text-sm font-medium text-gray-700 mb-2">
                Order Items *
              </label>
              <textarea
                id="items"
                value={itemsText}
                onChange={(e) => setItemsText(e.target.value)}
                className="form-textarea h-48"
                placeholder="Enter your order items, one per line:&#10;&#10;10 lbs Tomatoes&#10;5 heads Lettuce&#10;2 lbs Red Onions&#10;1 case Bell Peppers"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                List each item with quantity and description. Be as specific as possible.
              </p>
            </div>

            {/* Notes */}
            <div>
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                Additional Notes
              </label>
              <textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="form-textarea h-24"
                placeholder="Any special instructions, delivery preferences, or additional information..."
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start">
                <InformationCircleIcon className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Form Actions */}
            <div className="flex space-x-3 pt-4 border-t">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Order...' : 'Create Order'}
              </button>
              <button
                type="button"
                onClick={onCancel}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Selected Vendor Info */}
          {selectedVendorData && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Vendor Details</h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900">{selectedVendorData.name}</h4>
                  {selectedVendorData.description && (
                    <p className="text-sm text-gray-600 mt-1">{selectedVendorData.description}</p>
                  )}
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-center text-gray-600">
                    <span className="font-medium w-16">Phone:</span>
                    <a href={`tel:${selectedVendorData.phone}`} className="text-primary hover:text-blue-600">
                      {selectedVendorData.phone}
                    </a>
                  </div>
                  
                  <div className="flex items-center text-gray-600">
                    <span className="font-medium w-16">Email:</span>
                    <a href={`mailto:${selectedVendorData.email}`} className="text-primary hover:text-blue-600">
                      {selectedVendorData.email}
                    </a>
                  </div>
                  
                  <div className="flex items-start text-gray-600">
                    <span className="font-medium w-16 flex-shrink-0">Address:</span>
                    <span>{selectedVendorData.address}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Order Tips */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Tips</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start">
                <span className="text-primary mr-2">•</span>
                <span>Be specific with quantities and units (lbs, cases, pieces)</span>
              </div>
              <div className="flex items-start">
                <span className="text-primary mr-2">•</span>
                <span>Include preferred brands or quality specifications</span>
              </div>
              <div className="flex items-start">
                <span className="text-primary mr-2">•</span>
                <span>Mention any delivery time preferences in notes</span>
              </div>
              <div className="flex items-start">
                <span className="text-primary mr-2">•</span>
                <span>Contact vendor directly for urgent orders</span>
              </div>
            </div>
          </div>

          {/* Available Vendors */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Vendors</h3>
            <div className="space-y-2">
              {vendors.map(vendor => (
                <div
                  key={vendor.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedVendor === vendor.id.toString()
                      ? 'border-primary bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedVendor(vendor.id.toString())}
                >
                  <div className="font-medium text-gray-900">{vendor.name}</div>
                  <div className="text-sm text-gray-600">{vendor.phone}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}