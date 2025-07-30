'use client';

import { useState } from 'react';
import { inventoryAPI } from '../lib/api';
import { PencilIcon, TrashIcon, CubeIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export default function SKUList({ skus, items, onEdit, onRefresh, onUpdateStock }) {
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [stockUpdates, setStockUpdates] = useState({});

  const handleDelete = async (skuId) => {
    if (!confirm('Are you sure you want to delete this SKU? This action cannot be undone.')) {
      return;
    }

    setDeletingId(skuId);
    try {
      await inventoryAPI.deleteSKU(skuId);
      onRefresh();
    } catch (error) {
      console.error('Error deleting SKU:', error);
      alert('Failed to delete SKU: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDeletingId(null);
    }
  };

  const getItemName = (itemId) => {
    const item = items.find(item => item.item_id === itemId);
    return item ? item.name : 'Unknown Item';
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const handleStockUpdate = async (skuId, operation, quantity) => {
    try {
      setStockUpdates(prev => ({ ...prev, [skuId]: true }));
      await inventoryAPI.updateStock(skuId, quantity, operation);
      onRefresh();
    } catch (error) {
      console.error('Error updating stock:', error);
      alert('Failed to update stock: ' + (error.response?.data?.detail || error.message));
    } finally {
      setStockUpdates(prev => ({ ...prev, [skuId]: false }));
    }
  };

  const isLowStock = (sku) => {
    return sku.current_stock <= sku.low_stock_threshold;
  };

  if (skus.length === 0) {
    return (
      <div className="text-center py-12">
        <CubeIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No SKUs</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating your first SKU.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {skus.map((sku) => (
          <li key={sku.sku_id}>
            <div className="px-4 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center min-w-0 flex-1">
                  <div className="flex-shrink-0">
                    <div className="relative">
                      <CubeIcon className="h-8 w-8 text-purple-500" />
                      {isLowStock(sku) && (
                        <ExclamationTriangleIcon className="absolute -top-1 -right-1 h-4 w-4 text-red-500" />
                      )}
                    </div>
                  </div>
                  <div className="ml-4 min-w-0 flex-1">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {sku.sku_code}
                      </p>
                      {sku.variant_name && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          {sku.variant_name}
                        </span>
                      )}
                      {sku.is_default && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Default
                        </span>
                      )}
                      {!sku.is_active && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Inactive
                        </span>
                      )}
                      {isLowStock(sku) && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Low Stock
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-500 mt-1">
                      Item: {getItemName(sku.item_id)}
                    </p>
                    
                    <div className="flex items-center mt-2 text-xs text-gray-400 space-x-4">
                      <span>Price: {formatPrice(sku.price)}</span>
                      {sku.cost_price && (
                        <span>Cost: {formatPrice(sku.cost_price)}</span>
                      )}
                      {sku.discount_price && (
                        <span>Discount: {formatPrice(sku.discount_price)}</span>
                      )}
                      {sku.weight && (
                        <span>Weight: {sku.weight}kg</span>
                      )}
                    </div>

                    {/* Attributes */}
                    {sku.attributes && Object.keys(sku.attributes).length > 0 && (
                      <div className="flex items-center mt-2 space-x-2">
                        <span className="text-xs text-gray-500">Attributes:</span>
                        <div className="flex flex-wrap gap-1">
                          {Object.entries(sku.attributes).map(([key, value]) => (
                            <span
                              key={key}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                            >
                              {key}: {value}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Dimensions */}
                    {sku.dimensions && Object.keys(sku.dimensions).length > 0 && (
                      <div className="mt-2 text-xs text-gray-500">
                        <span className="font-medium">Dimensions: </span>
                        {Object.entries(sku.dimensions).map(([key, value], index) => (
                          <span key={key}>
                            {index > 0 && ' × '}
                            {value}cm {key}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Stock Information */}
                    <div className="mt-2 flex items-center space-x-4 text-xs">
                      <span className={`font-medium ${
                        isLowStock(sku) ? 'text-red-600' : 'text-green-600'
                      }`}>
                        Stock: {sku.current_stock}
                      </span>
                      {sku.reserved_stock > 0 && (
                        <span className="text-orange-600">
                          Reserved: {sku.reserved_stock}
                        </span>
                      )}
                      <span className="text-blue-600">
                        Available: {sku.available_stock}
                      </span>
                      {sku.low_stock_threshold > 0 && (
                        <span className="text-gray-500">
                          Low Stock Alert: {sku.low_stock_threshold}
                        </span>
                      )}
                    </div>

                    {/* Supplier Information */}
                    {(sku.supplier_name || sku.supplier_sku) && (
                      <div className="mt-2 text-xs text-gray-500">
                        {sku.supplier_name && (
                          <span>Supplier: {sku.supplier_name}</span>
                        )}
                        {sku.supplier_name && sku.supplier_sku && <span> • </span>}
                        {sku.supplier_sku && (
                          <span>Supplier SKU: {sku.supplier_sku}</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {/* Quick Stock Actions */}
                  {onUpdateStock && (
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleStockUpdate(sku.sku_id, 'subtract', 1)}
                        disabled={stockUpdates[sku.sku_id] || sku.current_stock <= 0}
                        className="p-1 text-xs text-gray-400 hover:text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                        title="Decrease stock by 1"
                      >
                        -1
                      </button>
                      <button
                        onClick={() => handleStockUpdate(sku.sku_id, 'add', 1)}
                        disabled={stockUpdates[sku.sku_id]}
                        className="p-1 text-xs text-gray-400 hover:text-green-600 hover:bg-green-50 rounded disabled:opacity-50"
                        title="Increase stock by 1"
                      >
                        +1
                      </button>
                    </div>
                  )}
                  
                  <button
                    onClick={() => onEdit(sku)}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full"
                    title="Edit SKU"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(sku.sku_id)}
                    disabled={deletingId === sku.sku_id}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full disabled:opacity-50"
                    title="Delete SKU"
                  >
                    {deletingId === sku.sku_id ? (
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