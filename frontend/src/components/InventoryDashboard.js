'use client';

import { useState, useEffect } from 'react';
import { inventoryAPI } from '../lib/api';
import CategoryForm from './CategoryForm';
import CategoryList from './CategoryList';
import ItemForm from './ItemForm';
import ItemList from './ItemList';
import SKUForm from './SKUForm';
import SKUList from './SKUList';
import { 
  PlusIcon, 
  FolderIcon, 
  CubeIcon, 
  TagIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

export default function InventoryDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Data states
  const [summary, setSummary] = useState({});
  const [categories, setCategories] = useState([]);
  const [items, setItems] = useState([]);
  const [skus, setSKUs] = useState([]);
  
  // Form states
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [showItemForm, setShowItemForm] = useState(false);
  const [showSKUForm, setShowSKUForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [editingItem, setEditingItem] = useState(null);
  const [editingSKU, setEditingSKU] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showInactive, setShowInactive] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [summaryData, categoriesData, itemsData, skusData] = await Promise.all([
        inventoryAPI.getInventorySummary(),
        inventoryAPI.getCategories(true), // Include inactive
        inventoryAPI.getItems({ include_inactive: true }),
        inventoryAPI.getSKUs({ include_inactive: true })
      ]);
      
      setSummary(summaryData);
      setCategories(categoriesData);
      setItems(itemsData);
      setSKUs(skusData);
    } catch (error) {
      console.error('Error loading inventory data:', error);
      setError('Failed to load inventory data');
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySave = (category) => {
    setShowCategoryForm(false);
    setEditingCategory(null);
    loadData();
  };

  const handleItemSave = (item) => {
    setShowItemForm(false);
    setEditingItem(null);
    loadData();
  };

  const handleSKUSave = (sku) => {
    setShowSKUForm(false);
    setEditingSKU(null);
    setSelectedItem(null);
    loadData();
  };

  const handleEditCategory = (category) => {
    setEditingCategory(category);
    setShowCategoryForm(true);
  };

  const handleEditItem = (item) => {
    setEditingItem(item);
    setShowItemForm(true);
  };

  const handleEditSKU = (sku) => {
    setEditingSKU(sku);
    setShowSKUForm(true);
  };

  const handleViewSKUs = (item) => {
    setSelectedItem(item);
    setActiveTab('skus');
  };

  const handleCreateSKU = (item = null) => {
    setSelectedItem(item);
    setShowSKUForm(true);
  };

  // Filter functions
  const filteredCategories = categories.filter(category => {
    if (!showInactive && !category.is_active) return false;
    if (searchTerm && !category.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const filteredItems = items.filter(item => {
    if (!showInactive && !item.is_active) return false;
    if (selectedCategory && item.category_id !== parseInt(selectedCategory)) return false;
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return item.name.toLowerCase().includes(searchLower) ||
             (item.description && item.description.toLowerCase().includes(searchLower)) ||
             (item.brand && item.brand.toLowerCase().includes(searchLower)) ||
             (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchLower)));
    }
    return true;
  });

  const filteredSKUs = skus.filter(sku => {
    if (!showInactive && !sku.is_active) return false;
    if (selectedItem && sku.item_id !== selectedItem.item_id) return false;
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return sku.sku_code.toLowerCase().includes(searchLower) ||
             (sku.variant_name && sku.variant_name.toLowerCase().includes(searchLower));
    }
    return true;
  });

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-gray-600">Loading inventory...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error}</div>
        <button onClick={loadData} className="btn-primary">
          Retry
        </button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: CurrencyDollarIcon },
    { id: 'categories', name: 'Categories', icon: FolderIcon, count: filteredCategories.length },
    { id: 'items', name: 'Items', icon: CubeIcon, count: filteredItems.length },
    { id: 'skus', name: 'SKUs', icon: TagIcon, count: filteredSKUs.length }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Inventory Management</h2>
          <p className="text-sm text-gray-600 mt-1">Manage your products, categories, and stock levels</p>
        </div>
        <button
          onClick={loadData}
          className="btn-secondary"
        >
          Refresh
        </button>
      </div>

      {/* Summary Stats */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FolderIcon className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Categories</p>
                <p className="text-2xl font-bold text-gray-900">{summary.categories_count || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CubeIcon className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Items</p>
                <p className="text-2xl font-bold text-gray-900">{summary.items_count || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-purple-500">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TagIcon className="h-8 w-8 text-purple-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">SKUs</p>
                <p className="text-2xl font-bold text-gray-900">{summary.skus_count || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-red-500">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Low Stock Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{summary.low_stock_alerts || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-yellow-500">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-yellow-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Inventory Value</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${(summary.total_inventory_value || 0).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{tab.name}</span>
                {tab.count !== undefined && (
                  <span className="bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Filters and Actions */}
      {activeTab !== 'overview' && (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Category Filter for Items */}
            {activeTab === 'items' && (
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Categories</option>
                {categories.filter(cat => cat.is_active).map(category => (
                  <option key={category.category_id} value={category.category_id}>
                    {category.name}
                  </option>
                ))}
              </select>
            )}

            {/* Show Inactive Toggle */}
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={showInactive}
                onChange={(e) => setShowInactive(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-2 text-sm text-gray-600">Show inactive</span>
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-2">
            {activeTab === 'categories' && (
              <button
                onClick={() => setShowCategoryForm(true)}
                className="btn-primary flex items-center"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Category
              </button>
            )}
            {activeTab === 'items' && (
              <button
                onClick={() => setShowItemForm(true)}
                className="btn-primary flex items-center"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Item
              </button>
            )}
            {activeTab === 'skus' && (
              <button
                onClick={() => handleCreateSKU()}
                className="btn-primary flex items-center"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add SKU
              </button>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="text-center py-8">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Inventory Overview</h3>
              <p className="text-gray-600">
                Use the tabs above to manage your categories, items, and SKUs.
              </p>
            </div>
          )}

          {activeTab === 'categories' && (
            <CategoryList
              categories={filteredCategories}
              onEdit={handleEditCategory}
              onRefresh={loadData}
            />
          )}

          {activeTab === 'items' && (
            <ItemList
              items={filteredItems}
              categories={categories}
              onEdit={handleEditItem}
              onRefresh={loadData}
              onViewSKUs={handleViewSKUs}
              onAddSKU={handleCreateSKU}
            />
          )}

          {activeTab === 'skus' && (
            <div>
              {selectedItem && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-sm text-blue-800">
                    Showing SKUs for: <strong>{selectedItem.name}</strong>
                    <button
                      onClick={() => setSelectedItem(null)}
                      className="ml-2 text-blue-600 hover:text-blue-800 underline"
                    >
                      Show all SKUs
                    </button>
                  </p>
                </div>
              )}
              <SKUList
                skus={filteredSKUs}
                items={items}
                onEdit={handleEditSKU}
                onRefresh={loadData}
                onUpdateStock={true}
              />
            </div>
          )}
        </div>
      </div>

      {/* Forms */}
      {showCategoryForm && (
        <CategoryForm
          category={editingCategory}
          categories={categories}
          onSave={handleCategorySave}
          onCancel={() => {
            setShowCategoryForm(false);
            setEditingCategory(null);
          }}
        />
      )}

      {showItemForm && (
        <ItemForm
          item={editingItem}
          categories={categories.filter(cat => cat.is_active)}
          onSave={handleItemSave}
          onCancel={() => {
            setShowItemForm(false);
            setEditingItem(null);
          }}
        />
      )}

      {showSKUForm && (
        <SKUForm
          sku={editingSKU}
          item={selectedItem}
          items={items}
          onSave={handleSKUSave}
          onCancel={() => {
            setShowSKUForm(false);
            setEditingSKU(null);
            setSelectedItem(null);
          }}
        />
      )}
    </div>
  );
}