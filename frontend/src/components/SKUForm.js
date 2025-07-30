'use client';

import { useState, useEffect } from 'react';
import { inventoryAPI } from '../lib/api';
import { XMarkIcon, PlusIcon, MinusIcon } from '@heroicons/react/24/outline';

export default function SKUForm({ sku, item, items, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    item_id: item ? item.item_id : '',
    sku_code: '',
    variant_name: '',
    attributes: {},
    price: 0,
    cost_price: null,
    discount_price: null,
    current_stock: 0,
    low_stock_threshold: 0,
    weight: null,
    dimensions: {},
    supplier_sku: '',
    supplier_name: '',
    is_default: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [newAttrKey, setNewAttrKey] = useState('');
  const [newAttrValue, setNewAttrValue] = useState('');
  const [newDimKey, setNewDimKey] = useState('');
  const [newDimValue, setNewDimValue] = useState('');

  const dimensionOptions = ['length', 'width', 'height', 'diameter', 'depth'];

  useEffect(() => {
    if (sku) {
      setFormData({
        item_id: sku.item_id,
        sku_code: sku.sku_code || '',
        variant_name: sku.variant_name || '',
        attributes: sku.attributes || {},
        price: sku.price || 0,
        cost_price: sku.cost_price || null,
        discount_price: sku.discount_price || null,
        current_stock: sku.current_stock || 0,
        low_stock_threshold: sku.low_stock_threshold || 0,
        weight: sku.weight || null,
        dimensions: sku.dimensions || {},
        supplier_sku: sku.supplier_sku || '',
        supplier_name: sku.supplier_name || '',
        is_default: sku.is_default || false
      });
    } else if (item) {
      setFormData(prev => ({
        ...prev,
        item_id: item.item_id,
        price: item.base_price || 0,
        cost_price: item.cost_price || null
      }));
    }
  }, [sku, item]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Convert string values to appropriate types
      const submitData = {
        ...formData,
        item_id: parseInt(formData.item_id),
        price: parseFloat(formData.price || 0),
        cost_price: formData.cost_price ? parseFloat(formData.cost_price) : null,
        discount_price: formData.discount_price ? parseFloat(formData.discount_price) : null,
        current_stock: parseInt(formData.current_stock || 0),
        low_stock_threshold: parseInt(formData.low_stock_threshold || 0),
        weight: formData.weight ? parseFloat(formData.weight) : null,
        dimensions: Object.fromEntries(
          Object.entries(formData.dimensions).map(([key, value]) => [key, parseFloat(value)])
        )
      };

      let result;
      if (sku) {
        result = await inventoryAPI.updateSKU(sku.sku_id, submitData);
      } else {
        result = await inventoryAPI.createSKU(submitData);
      }
      onSave(result);
    } catch (error) {
      console.error('Error saving SKU:', error);
      const errorMessage = error.response?.data?.detail;
      if (typeof errorMessage === 'string') {
        setError(errorMessage);
      } else if (Array.isArray(errorMessage)) {
        setError(errorMessage.map(err => `${err.loc.join(' > ')}: ${err.msg}`).join(', '));
      } else {
        setError('Failed to save SKU');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const addAttribute = () => {
    if (newAttrKey.trim() && newAttrValue.trim()) {
      setFormData(prev => ({
        ...prev,
        attributes: {
          ...prev.attributes,
          [newAttrKey.trim()]: newAttrValue.trim()
        }
      }));
      setNewAttrKey('');
      setNewAttrValue('');
    }
  };

  const removeAttribute = (keyToRemove) => {
    setFormData(prev => ({
      ...prev,
      attributes: Object.fromEntries(
        Object.entries(prev.attributes).filter(([key]) => key !== keyToRemove)
      )
    }));
  };

  const addDimension = () => {
    if (newDimKey.trim() && newDimValue.trim() && !isNaN(newDimValue)) {
      setFormData(prev => ({
        ...prev,
        dimensions: {
          ...prev.dimensions,
          [newDimKey.trim()]: newDimValue.trim()
        }
      }));
      setNewDimKey('');
      setNewDimValue('');
    }
  };

  const removeDimension = (keyToRemove) => {
    setFormData(prev => ({
      ...prev,
      dimensions: Object.fromEntries(
        Object.entries(prev.dimensions).filter(([key]) => key !== keyToRemove)
      )
    }));
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {sku ? 'Edit SKU' : 'Create New SKU'}
            {item && <span className="text-sm text-gray-500 ml-2">for {item.name}</span>}
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 max-h-96 overflow-y-auto">
          {!item && (
            <div>
              <label htmlFor="item_id" className="block text-sm font-medium text-gray-700">
                Select Item *
              </label>
              <select
                id="item_id"
                name="item_id"
                value={formData.item_id}
                onChange={handleChange}
                required
                className="form-input"
              >
                <option value="">Select an item</option>
                {items.map((i) => (
                  <option key={i.item_id} value={i.item_id}>
                    {i.name}
                  </option>
                ))}
              </select>
            </div>
          )}
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="sku_code" className="block text-sm font-medium text-gray-700">
                SKU Code *
              </label>
              <input
                type="text"
                id="sku_code"
                name="sku_code"
                value={formData.sku_code}
                onChange={handleChange}
                required
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., ITEM-001-LG"
              />
            </div>

            <div>
              <label htmlFor="variant_name" className="block text-sm font-medium text-gray-700">
                Variant Name
              </label>
              <input
                type="text"
                id="variant_name"
                name="variant_name"
                value={formData.variant_name}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Large, Red, Pack of 12"
              />
            </div>
          </div>

          {/* Pricing */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="price" className="block text-sm font-medium text-gray-700">
                Price * ($)
              </label>
              <input
                type="number"
                id="price"
                name="price"
                value={formData.price}
                onChange={handleChange}
                min="0"
                step="0.01"
                required
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="cost_price" className="block text-sm font-medium text-gray-700">
                Cost Price ($)
              </label>
              <input
                type="number"
                id="cost_price"
                name="cost_price"
                value={formData.cost_price || ''}
                onChange={handleChange}
                min="0"
                step="0.01"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="discount_price" className="block text-sm font-medium text-gray-700">
                Discount Price ($)
              </label>
              <input
                type="number"
                id="discount_price"
                name="discount_price"
                value={formData.discount_price || ''}
                onChange={handleChange}
                min="0"
                step="0.01"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Inventory */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="current_stock" className="block text-sm font-medium text-gray-700">
                Current Stock
              </label>
              <input
                type="number"
                id="current_stock"
                name="current_stock"
                value={formData.current_stock}
                onChange={handleChange}
                min="0"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="low_stock_threshold" className="block text-sm font-medium text-gray-700">
                Low Stock Threshold
              </label>
              <input
                type="number"
                id="low_stock_threshold"
                name="low_stock_threshold"
                value={formData.low_stock_threshold}
                onChange={handleChange}
                min="0"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Physical Properties */}
          <div>
            <label htmlFor="weight" className="block text-sm font-medium text-gray-700">
              Weight (kg)
            </label>
            <input
              type="number"
              id="weight"
              name="weight"
              value={formData.weight || ''}
              onChange={handleChange}
              min="0"
              step="0.01"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Supplier Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="supplier_name" className="block text-sm font-medium text-gray-700">
                Supplier Name
              </label>
              <input
                type="text"
                id="supplier_name"
                name="supplier_name"
                value={formData.supplier_name}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="supplier_sku" className="block text-sm font-medium text-gray-700">
                Supplier SKU
              </label>
              <input
                type="text"
                id="supplier_sku"
                name="supplier_sku"
                value={formData.supplier_sku}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Default SKU */}
          <div className="flex items-center">
            <input
              id="is_default"
              name="is_default"
              type="checkbox"
              checked={formData.is_default}
              onChange={handleChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_default" className="ml-2 block text-sm text-gray-900">
              Set as default SKU for this item
            </label>
          </div>

          {/* Attributes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Variant Attributes</label>
            <div className="space-y-2 mb-2">
              {Object.entries(formData.attributes).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-600 min-w-0 flex-1">{key}:</span>
                  <span className="text-sm text-gray-900 min-w-0 flex-1">{value}</span>
                  <button
                    type="button"
                    onClick={() => removeAttribute(key)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <MinusIcon className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newAttrKey}
                onChange={(e) => setNewAttrKey(e.target.value)}
                placeholder="Attribute name (e.g., size, color)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <input
                type="text"
                value={newAttrValue}
                onChange={(e) => setNewAttrValue(e.target.value)}
                placeholder="Value"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={addAttribute}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <PlusIcon className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Dimensions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Dimensions (cm)</label>
            <div className="space-y-2 mb-2">
              {Object.entries(formData.dimensions).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-600 min-w-0 flex-1 capitalize">{key}:</span>
                  <span className="text-sm text-gray-900 min-w-0 flex-1">{value} cm</span>
                  <button
                    type="button"
                    onClick={() => removeDimension(key)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <MinusIcon className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex space-x-2">
              <select
                value={newDimKey}
                onChange={(e) => setNewDimKey(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select dimension</option>
                {dimensionOptions.map(dim => (
                  <option key={dim} value={dim} disabled={formData.dimensions[dim]}>
                    {dim.charAt(0).toUpperCase() + dim.slice(1)}
                  </option>
                ))}
              </select>
              <input
                type="number"
                value={newDimValue}
                onChange={(e) => setNewDimValue(e.target.value)}
                placeholder="Value (cm)"
                min="0"
                step="0.1"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="button"
                onClick={addDimension}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <PlusIcon className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Saving...' : (sku ? 'Update' : 'Create')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}