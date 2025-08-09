'use client';

import { useState, useEffect } from 'react';
import { marketplaceAPI } from '../lib/api';
import Link from 'next/link';
import VendorCard from './VendorCard';
import MarketplaceFilters from './MarketplaceFilters';
import VendorDetailModal from './VendorDetailModal';
import { 
  Squares2X2Icon, 
  ListBulletIcon, 
  ArrowUpIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

export default function VendorMarketplace({ onCreateOrder }) {
  const [vendors, setVendors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('rating'); // 'rating', 'name', 'newest'
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    loadCategories();
    loadVendors();
  }, []);

  useEffect(() => {
    loadVendors();
  }, [filters, currentPage, sortBy]);

  const loadCategories = async () => {
    try {
      const categoriesData = await marketplaceAPI.getCategories();
      setCategories(categoriesData);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadVendors = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page: currentPage,
        page_size: 12,
        ...filters
      };

      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const response = await marketplaceAPI.getVendors(params);
      
      // Sort vendors if needed
      let sortedVendors = response.vendors;
      switch (sortBy) {
        case 'name':
          sortedVendors = [...response.vendors].sort((a, b) => a.name.localeCompare(b.name));
          break;
        case 'rating':
          sortedVendors = [...response.vendors].sort((a, b) => b.average_rating - a.average_rating);
          break;
        case 'newest':
          sortedVendors = [...response.vendors].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
          break;
        default:
          break;
      }
      
      setVendors(sortedVendors);
      setTotalPages(response.total_pages);
      setTotalCount(response.total_count);
    } catch (error) {
      console.error('Error loading vendors:', error);
      setError('Failed to load vendors. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handleViewDetails = async (vendor) => {
    try {
      const detailedVendor = await marketplaceAPI.getVendorDetail(vendor.user_id);
      setSelectedVendor(detailedVendor);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Error loading vendor details:', error);
      // Fallback to basic vendor data
      setSelectedVendor(vendor);
      setShowDetailModal(true);
    }
  };

  const handleQuickOrder = (vendor) => {
    onCreateOrder?.(vendor);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading && vendors.length === 0) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading marketplace...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Marketplace</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadVendors}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Vendor Marketplace</h1>
          <p className="mt-2 text-gray-600">
            Discover and connect with {totalCount} verified suppliers
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0 flex items-center space-x-4">
          {/* Sort Dropdown */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
          >
            <option value="rating">Sort by Rating</option>
            <option value="name">Sort by Name</option>
            <option value="newest">Sort by Newest</option>
          </select>
          
          {/* View Mode Toggle */}
          <div className="flex rounded-md border border-gray-300">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 text-sm font-medium rounded-l-md ${
                viewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Squares2X2Icon className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 text-sm font-medium rounded-r-md border-l ${
                viewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <ListBulletIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <MarketplaceFilters
        categories={categories}
        onFiltersChange={handleFiltersChange}
        initialFilters={filters}
      />

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Showing {vendors.length} of {totalCount} vendors
          {currentPage > 1 && ` (Page ${currentPage} of ${totalPages})`}
        </p>
        
        {loading && (
          <div className="flex items-center text-sm text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Loading...
          </div>
        )}
      </div>

      {/* Vendors Grid/List */}
      {vendors.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No vendors found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your filters or search terms
          </p>
        </div>
      ) : (
        <div className={
          viewMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-4'
        }>
          {vendors.map((vendor) => (
            <Link key={vendor.user_id} href={`/storefront/${vendor.user_id}`}>
              <VendorCard
                vendor={vendor}
                onQuickOrder={handleQuickOrder}
                compact={viewMode === 'list'}
              />
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <span className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          
          <button
            onClick={scrollToTop}
            className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <ArrowUpIcon className="h-4 w-4 mr-1" />
            Back to Top
          </button>
        </div>
      )}

      {/* Vendor Detail Modal */}
      {showDetailModal && selectedVendor && (
        <VendorDetailModal
          vendor={selectedVendor}
          onClose={() => setShowDetailModal(false)}
          onCreateOrder={handleQuickOrder}
        />
      )}
    </div>
  );
}