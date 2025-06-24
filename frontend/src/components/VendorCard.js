'use client';

import { useState } from 'react';
import { StarIcon, MapPinIcon, ClockIcon, CurrencyDollarIcon } from '@heroicons/react/24/solid';
import { StarIcon as StarOutlineIcon } from '@heroicons/react/24/outline';

export default function VendorCard({ vendor, onViewDetails, onQuickOrder, compact = false }) {
  const [imageError, setImageError] = useState(false);

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <StarIcon key={i} className="h-4 w-4 text-yellow-400" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={i} className="relative">
            <StarOutlineIcon className="h-4 w-4 text-gray-300" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <StarIcon className="h-4 w-4 text-yellow-400" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <StarOutlineIcon key={i} className="h-4 w-4 text-gray-300" />
        );
      }
    }
    return stars;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (compact) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
           onClick={() => onViewDetails?.(vendor)}>
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            {vendor.logo_url && !imageError ? (
              <img
                src={vendor.logo_url}
                alt={`${vendor.name} logo`}
                className="h-12 w-12 rounded-lg object-cover"
                onError={() => setImageError(true)}
              />
            ) : (
              <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
                <span className="text-lg font-semibold text-gray-600">
                  {vendor.name.charAt(0)}
                </span>
              </div>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900 truncate">
              {vendor.name}
            </h3>
            <p className="text-xs text-gray-600 truncate">
              {vendor.business_type}
            </p>
            
            <div className="flex items-center mt-1">
              <div className="flex items-center">
                {renderStars(vendor.average_rating)}
              </div>
              <span className="ml-1 text-xs text-gray-600">
                ({vendor.review_count})
              </span>
            </div>
          </div>
          
          <div className="flex-shrink-0">
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              vendor.is_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {vendor.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200 hover:-translate-y-1">
      {/* Header with logo and status */}
      <div className="p-6 pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              {vendor.logo_url && !imageError ? (
                <img
                  src={vendor.logo_url}
                  alt={`${vendor.name} logo`}
                  className="h-16 w-16 rounded-xl object-cover"
                  onError={() => setImageError(true)}
                />
              ) : (
                <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">
                    {vendor.name.charAt(0)}
                  </span>
                </div>
              )}
            </div>
            
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-1">
                {vendor.name}
              </h3>
              <p className="text-sm text-gray-600 mb-2">
                {vendor.business_type}
              </p>
              
              {/* Rating */}
              <div className="flex items-center space-x-2">
                <div className="flex items-center">
                  {renderStars(vendor.average_rating)}
                </div>
                <span className="text-sm font-medium text-gray-900">
                  {vendor.average_rating.toFixed(1)}
                </span>
                <span className="text-sm text-gray-600">
                  ({vendor.review_count} reviews)
                </span>
              </div>
            </div>
          </div>
          
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            vendor.is_active 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {vendor.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      {/* Categories */}
      {vendor.categories && vendor.categories.length > 0 && (
        <div className="px-6 pb-4">
          <div className="flex flex-wrap gap-2">
            {vendor.categories.slice(0, 3).map((category, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {category}
              </span>
            ))}
            {vendor.categories.length > 3 && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                +{vendor.categories.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Specialties */}
      {vendor.specialties && vendor.specialties.length > 0 && (
        <div className="px-6 pb-4">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Specialties:</span> {vendor.specialties.slice(0, 3).join(', ')}
            {vendor.specialties.length > 3 && ` +${vendor.specialties.length - 3} more`}
          </p>
        </div>
      )}

      {/* Key Info */}
      <div className="px-6 pb-4 space-y-2">
        {vendor.delivery_areas && (
          <div className="flex items-center text-sm text-gray-600">
            <MapPinIcon className="h-4 w-4 mr-2 text-gray-400" />
            <span>Delivers to: {vendor.delivery_areas}</span>
          </div>
        )}
        
        {vendor.business_hours && (
          <div className="flex items-center text-sm text-gray-600">
            <ClockIcon className="h-4 w-4 mr-2 text-gray-400" />
            <span>{vendor.business_hours}</span>
          </div>
        )}
        
        {vendor.minimum_order > 0 && (
          <div className="flex items-center text-sm text-gray-600">
            <CurrencyDollarIcon className="h-4 w-4 mr-2 text-gray-400" />
            <span>Min order: {formatCurrency(vendor.minimum_order)}</span>
          </div>
        )}
      </div>

      {/* Certifications */}
      {vendor.certifications && vendor.certifications.length > 0 && (
        <div className="px-6 pb-4">
          <div className="flex flex-wrap gap-1">
            {vendor.certifications.slice(0, 2).map((cert, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700"
              >
                ✓ {cert}
              </span>
            ))}
            {vendor.certifications.length > 2 && (
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600">
                +{vendor.certifications.length - 2} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex gap-3">
          <button
            onClick={() => onViewDetails?.(vendor)}
            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-1 text-sm flex items-center justify-center min-h-[44px]"
          >
            View Details
          </button>
          <button
            onClick={() => onQuickOrder?.(vendor)}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 text-sm flex items-center justify-center min-h-[44px]"
          >
            Quick Order
          </button>
        </div>
      </div>
    </div>
  );
}