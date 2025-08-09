'use client';

import { useState } from 'react';
import { marketplaceAPI } from '../lib/api';
import {
  PlusIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  ScaleIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  StarIcon,
  TruckIcon,
  CurrencyDollarIcon,
  ClockIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

export default function PriceComparisonTool({ user }) {
  const [products, setProducts] = useState([{ name: '', category: '', brand: '' }]);
  const [filters, setFilters] = useState({
    max_price: '',
    min_price: '',
    sort_by: 'price_low_to_high',
    min_rating: ''
  });
  const [includeRecommendations, setIncludeRecommendations] = useState(true);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const addProduct = () => {
    setProducts([...products, { name: '', category: '', brand: '' }]);
  };

  const removeProduct = (index) => {
    if (products.length > 1) {
      setProducts(products.filter((_, i) => i !== index));
    }
  };

  const updateProduct = (index, field, value) => {
    const updatedProducts = products.map((product, i) => 
      i === index ? { ...product, [field]: value } : product
    );
    setProducts(updatedProducts);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Filter out empty products
      const validProducts = products.filter(p => p.name.trim());
      
      if (validProducts.length === 0) {
        throw new Error('Please enter at least one product to compare');
      }

      // Build the comparison request
      const comparisonRequest = {
        products: validProducts.map(p => ({
          name: p.name.trim(),
          ...(p.category.trim() && { category: p.category.trim() }),
          ...(p.brand.trim() && { brand: p.brand.trim() })
        })),
        filters: {
          ...(filters.max_price && { max_price: parseFloat(filters.max_price) }),
          ...(filters.min_price && { min_price: parseFloat(filters.min_price) }),
          ...(filters.min_rating && { min_rating: parseFloat(filters.min_rating) }),
          sort_by: filters.sort_by
        },
        include_recommendations: includeRecommendations
      };

      const response = await marketplaceAPI.comparePrices(comparisonRequest);
      setResults(response);
    } catch (err) {
      console.error('Price comparison error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to compare prices');
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating || 0);
    const hasHalfStar = (rating || 0) % 1 >= 0.5;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<StarIconSolid key={i} className="h-4 w-4 text-yellow-400" />);
      } else if (i === fullStars && hasHalfStar) {
        stars.push(<StarIconSolid key={i} className="h-4 w-4 text-yellow-400" />);
      } else {
        stars.push(<StarIcon key={i} className="h-4 w-4 text-gray-300" />);
      }
    }
    return stars;
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  return (
    <div className="space-y-8">
      {/* Search Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-6">
          <ScaleIcon className="h-6 w-6 text-primary mr-3" />
          <h2 className="text-xl font-semibold text-gray-900">Compare Product Prices</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Products Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Products to Compare
            </label>
            <div className="space-y-4">
              {products.map((product, index) => (
                <div key={index} className="flex gap-4 items-start p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Product Name *
                      </label>
                      <input
                        type="text"
                        value={product.name}
                        onChange={(e) => updateProduct(index, 'name', e.target.value)}
                        placeholder="e.g., Organic Tomatoes"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Category (Optional)
                      </label>
                      <input
                        type="text"
                        value={product.category}
                        onChange={(e) => updateProduct(index, 'category', e.target.value)}
                        placeholder="e.g., Vegetables"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Brand (Optional)
                      </label>
                      <input
                        type="text"
                        value={product.brand}
                        onChange={(e) => updateProduct(index, 'brand', e.target.value)}
                        placeholder="e.g., Fresh Farms"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                  </div>
                  {products.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeProduct(index)}
                      className="mt-6 p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
              ))}
            </div>
            
            <button
              type="button"
              onClick={addProduct}
              className="mt-4 flex items-center text-primary hover:text-primary-dark transition-colors"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Add Another Product
            </button>
          </div>

          {/* Filters Section */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Filters & Options</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={filters.min_price}
                  onChange={(e) => setFilters({...filters, min_price: e.target.value})}
                  placeholder="$0.00"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={filters.max_price}
                  onChange={(e) => setFilters({...filters, max_price: e.target.value})}
                  placeholder="$100.00"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Rating
                </label>
                <select
                  value={filters.min_rating}
                  onChange={(e) => setFilters({...filters, min_rating: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="">Any Rating</option>
                  <option value="4.5">4.5+ Stars</option>
                  <option value="4.0">4.0+ Stars</option>
                  <option value="3.5">3.5+ Stars</option>
                  <option value="3.0">3.0+ Stars</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sort By
                </label>
                <select
                  value={filters.sort_by}
                  onChange={(e) => setFilters({...filters, sort_by: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="price_low_to_high">Price: Low to High</option>
                  <option value="price_high_to_low">Price: High to Low</option>
                  <option value="rating">Highest Rated</option>
                  <option value="delivery_time">Fastest Delivery</option>
                </select>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeRecommendations}
                  onChange={(e) => setIncludeRecommendations(e.target.checked)}
                  className="rounded border-gray-300 text-primary focus:ring-primary"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Include AI-powered recommendations
                </span>
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Comparing Prices...
                </>
              ) : (
                <>
                  <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                  Compare Prices
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mr-3" />
            <div>
              <h3 className="text-lg font-medium text-red-900">Error</h3>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Comparison Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{results.summary.total_products_compared}</div>
                <div className="text-sm text-blue-600">Products Compared</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{results.summary.total_vendors}</div>
                <div className="text-sm text-green-600">Vendors Found</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{results.performance_metrics.search_time_ms}ms</div>
                <div className="text-sm text-purple-600">Search Time</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{formatPrice(results.summary.average_savings_potential || 0)}</div>
                <div className="text-sm text-yellow-600">Avg. Savings</div>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {results.recommendations && results.recommendations.length > 0 && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <StarIconSolid className="h-6 w-6 text-yellow-500 mr-2" />
                AI Recommendations
              </h3>
              <div className="space-y-3">
                {results.recommendations.map((rec, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-blue-200">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-900">{rec.reason}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          Confidence: {Math.round(rec.confidence_score * 100)}%
                        </p>
                      </div>
                      {rec.potential_savings && (
                        <div className="text-right">
                          <div className="text-lg font-bold text-green-600">
                            {formatPrice(rec.potential_savings)}
                          </div>
                          <div className="text-xs text-gray-500">Potential Savings</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Product Results */}
          {results.results.map((productResult, productIndex) => (
            <div key={productIndex} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    {productResult.query.name}
                  </h3>
                  {productResult.query.category && (
                    <p className="text-sm text-gray-600 mt-1">
                      Category: {productResult.query.category}
                    </p>
                  )}
                  {productResult.query.brand && (
                    <p className="text-sm text-gray-600">
                      Brand: {productResult.query.brand}
                    </p>
                  )}
                </div>
                {productResult.price_range && (
                  <div className="text-right">
                    <div className="text-sm text-gray-600">Price Range</div>
                    <div className="text-lg font-semibold text-gray-900">
                      {formatPrice(productResult.price_range.min)} - {formatPrice(productResult.price_range.max)}
                    </div>
                    {productResult.average_price && (
                      <div className="text-sm text-gray-500">
                        Avg: {formatPrice(productResult.average_price)}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {productResult.vendors.length === 0 ? (
                <div className="text-center py-8">
                  <ExclamationTriangleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">No vendors found</h4>
                  <p className="text-gray-600">Try adjusting your search terms or filters</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {productResult.vendors.map((vendor, vendorIndex) => (
                    <div key={vendorIndex} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="text-lg font-semibold text-gray-900">{vendor.vendor_name}</h4>
                          <div className="flex items-center mt-1">
                            <div className="flex items-center mr-4">
                              {renderStars(vendor.vendor_rating)}
                              <span className="ml-1 text-sm text-gray-600">
                                ({vendor.vendor_rating?.toFixed(1) || 'N/A'})
                              </span>
                            </div>
                            {vendor.certifications && vendor.certifications.length > 0 && (
                              <div className="flex items-center">
                                <ShieldCheckIcon className="h-4 w-4 text-green-500 mr-1" />
                                <span className="text-xs text-green-600">
                                  {vendor.certifications.join(', ')}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-gray-900">
                            {formatPrice(vendor.pricing.unit_price)}
                          </div>
                          <div className="text-sm text-gray-600">per unit</div>
                          {vendor.pricing.delivery_fee && (
                            <div className="text-xs text-gray-500 mt-1">
                              + {formatPrice(vendor.pricing.delivery_fee)} delivery
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                        <div className="flex items-center text-sm">
                          <CheckCircleIcon className={`h-4 w-4 mr-2 ${vendor.availability.in_stock ? 'text-green-500' : 'text-red-500'}`} />
                          <span className={vendor.availability.in_stock ? 'text-green-700' : 'text-red-700'}>
                            {vendor.availability.in_stock ? 'In Stock' : 'Out of Stock'}
                          </span>
                          {vendor.availability.quantity_available && (
                            <span className="text-gray-500 ml-1">
                              ({vendor.availability.quantity_available} available)
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center text-sm text-gray-600">
                          <TruckIcon className="h-4 w-4 mr-2" />
                          {vendor.delivery_time || 'Contact for delivery time'}
                        </div>
                        
                        <div className="flex items-center text-sm text-gray-600">
                          <CurrencyDollarIcon className="h-4 w-4 mr-2" />
                          Min Order: {formatPrice(vendor.minimum_order || 0)}
                        </div>
                      </div>

                      {vendor.availability.lead_time_days && (
                        <div className="mt-2 flex items-center text-sm text-gray-600">
                          <ClockIcon className="h-4 w-4 mr-2" />
                          Lead time: {vendor.availability.lead_time_days} days
                        </div>
                      )}

                      {productResult.best_price_vendor === vendor.vendor_id && (
                        <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircleIcon className="h-4 w-4 mr-1" />
                          Best Price
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Smart Suggestions */}
          {results.smart_suggestions && results.smart_suggestions.length > 0 && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200 p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <ScaleIcon className="h-6 w-6 text-purple-600 mr-2" />
                Smart Suggestions
              </h3>
              <div className="grid gap-4">
                {results.smart_suggestions.map((suggestion, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-purple-200">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-gray-900">{suggestion.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{suggestion.description}</p>
                        {suggestion.confidence_score && (
                          <p className="text-xs text-gray-500 mt-2">
                            Confidence: {Math.round(suggestion.confidence_score * 100)}%
                          </p>
                        )}
                      </div>
                      {suggestion.potential_savings && (
                        <div className="text-right">
                          <div className="text-lg font-bold text-purple-600">
                            {formatPrice(suggestion.potential_savings)}
                          </div>
                          <div className="text-xs text-gray-500">Potential Savings</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}