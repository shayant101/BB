'use client';

import { useState } from 'react';
import { inventoryAPI } from '../lib/api';
import { PencilIcon, TrashIcon, CubeIcon, TagIcon, PlusIcon } from '@heroicons/react/24/outline';

export default function ItemList({ items, categories, onEdit, onRefresh, onViewSKUs, onAddSKU }) {
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (itemId) => {
    if (!confirm('Are you sure you want to delete this item? This will also delete all associated SKUs.')) {
      return;
    }

    setDeletingId(itemId);
    try {
      await inventoryAPI.deleteItem(itemId);
      onRefresh();
    } catch (error) {
      console.error('Error deleting item:', error);
      alert('Failed to delete item: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDeletingId(null);
    }
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(cat => cat.category_id === categoryId);
    return category ? category.name : 'Unknown Category';
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <CubeIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No items</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating your first item.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {items.map((item) => (
          <li key={item.item_id}>
            <div className="px-4 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center min-w-0 flex-1">
                  <div className="flex-shrink-0">
                    <CubeIcon className="h-8 w-8 text-green-500" />
                  </div>
                  <div className="ml-4 min-w-0 flex-1">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {item.name}
                      </p>
                      {item.brand && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {item.brand}
                        </span>
                      )}
                      {!item.is_active && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Inactive
                        </span>
                      )}
                      {item.is_featured && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Featured
                        </span>
                      )}
                    </div>
                    
                    {item.description && (
                      <p className="text-sm text-gray-500 truncate mt-1">
                        {item.description}
                      </p>
                    )}
                    
                    <div className="flex items-center mt-2 text-xs text-gray-400 space-x-4">
                      <span>Category: {getCategoryName(item.category_id)}</span>
                      <span>Price: {formatPrice(item.base_price)}</span>
                      <span>Unit: {item.unit_of_measure}</span>
                      {item.minimum_order_quantity > 1 && (
                        <span>Min Qty: {item.minimum_order_quantity}</span>
                      )}
                      {item.lead_time_days > 0 && (
                        <span>Lead Time: {item.lead_time_days} days</span>
                      )}
                    </div>

                    {/* Tags */}
                    {item.tags && item.tags.length > 0 && (
                      <div className="flex items-center mt-2 space-x-1">
                        <TagIcon className="h-3 w-3 text-gray-400" />
                        <div className="flex flex-wrap gap-1">
                          {item.tags.slice(0, 3).map((tag, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {tag}
                            </span>
                          ))}
                          {item.tags.length > 3 && (
                            <span className="text-xs text-gray-500">
                              +{item.tags.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Specifications */}
                    {item.specifications && Object.keys(item.specifications).length > 0 && (
                      <div className="mt-2 text-xs text-gray-500">
                        <span className="font-medium">Specs: </span>
                        {Object.entries(item.specifications).slice(0, 2).map(([key, value], index) => (
                          <span key={key}>
                            {index > 0 && ', '}
                            {key}: {value}
                          </span>
                        ))}
                        {Object.keys(item.specifications).length > 2 && (
                          <span> +{Object.keys(item.specifications).length - 2} more</span>
                        )}
                      </div>
                    )}

                    {/* Inventory Status */}
                    {item.track_inventory && (
                      <div className="mt-2 flex items-center space-x-4 text-xs">
                        <span className={`font-medium ${
                          item.current_stock <= (item.low_stock_threshold || 0) 
                            ? 'text-red-600' 
                            : 'text-green-600'
                        }`}>
                          Stock: {item.current_stock || 0}
                        </span>
                        {item.low_stock_threshold && (
                          <span className="text-gray-500">
                            Low Stock Alert: {item.low_stock_threshold}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {onViewSKUs && (
                    <button
                      onClick={() => onViewSKUs(item)}
                      className="p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-full"
                      title="View SKUs"
                    >
                      <CubeIcon className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    onClick={() => onAddSKU(item)}
                    className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-full"
                    title="Add SKU"
                  >
                    <PlusIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onEdit(item)}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full"
                    title="Edit item"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(item.item_id)}
                    disabled={deletingId === item.item_id}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full disabled:opacity-50"
                    title="Delete item"
                  >
                    {deletingId === item.item_id ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                    ) : (
                      <TrashIcon className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}