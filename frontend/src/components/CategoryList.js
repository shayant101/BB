'use client';

import { useState } from 'react';
import { inventoryAPI } from '../lib/api';
import { PencilIcon, TrashIcon, PlusIcon, FolderIcon } from '@heroicons/react/24/outline';

export default function CategoryList({ categories, onEdit, onRefresh }) {
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (categoryId) => {
    if (!confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
      return;
    }

    setDeletingId(categoryId);
    try {
      await inventoryAPI.deleteCategory(categoryId);
      onRefresh();
    } catch (error) {
      console.error('Error deleting category:', error);
      alert('Failed to delete category: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDeletingId(null);
    }
  };

  const getParentCategoryName = (parentId) => {
    if (!parentId) return null;
    const parent = categories.find(cat => cat.category_id === parentId);
    return parent ? parent.name : 'Unknown';
  };

  const sortedCategories = [...categories].sort((a, b) => {
    // Sort by sort_order first, then by name
    if (a.sort_order !== b.sort_order) {
      return a.sort_order - b.sort_order;
    }
    return a.name.localeCompare(b.name);
  });

  if (categories.length === 0) {
    return (
      <div className="text-center py-12">
        <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No categories</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating your first category.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {sortedCategories.map((category) => (
          <li key={category.category_id}>
            <div className="px-4 py-4 flex items-center justify-between hover:bg-gray-50">
              <div className="flex items-center min-w-0 flex-1">
                <div className="flex-shrink-0">
                  <FolderIcon className="h-8 w-8 text-blue-500" />
                </div>
                <div className="ml-4 min-w-0 flex-1">
                  <div className="flex items-center">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {category.name}
                    </p>
                    {!category.is_active && (
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Inactive
                      </span>
                    )}
                  </div>
                  {category.description && (
                    <p className="text-sm text-gray-500 truncate mt-1">
                      {category.description}
                    </p>
                  )}
                  <div className="flex items-center mt-1 text-xs text-gray-400 space-x-4">
                    {category.parent_category_id && (
                      <span>
                        Parent: {getParentCategoryName(category.parent_category_id)}
                      </span>
                    )}
                    <span>Order: {category.sort_order}</span>
                    <span>
                      Created: {new Date(category.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onEdit(category)}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full"
                  title="Edit category"
                >
                  <PencilIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(category.category_id)}
                  disabled={deletingId === category.category_id}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full disabled:opacity-50"
                  title="Delete category"
                >
                  {deletingId === category.category_id ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                  ) : (
                    <TrashIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}