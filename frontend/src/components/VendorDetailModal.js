'use client';

import { Fragment } from 'react';
import { Dialog, Transition, Tab } from '@headlessui/react';
import { 
  XMarkIcon, 
  StarIcon, 
  MapPinIcon, 
  ClockIcon, 
  CurrencyDollarIcon,
  PhoneIcon,
  EnvelopeIcon,
  GlobeAltIcon,
  CheckBadgeIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function VendorDetailModal({ vendor, onClose, onCreateOrder }) {
  if (!vendor) return null;

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <StarSolidIcon key={i} className="h-5 w-5 text-yellow-400" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={i} className="relative">
            <StarIcon className="h-5 w-5 text-gray-300" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <StarSolidIcon className="h-5 w-5 text-yellow-400" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <StarIcon key={i} className="h-5 w-5 text-gray-300" />
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

  const tabs = [
    { name: 'Overview', id: 'overview' },
    { name: 'Contact & Hours', id: 'contact' },
    { name: 'Certifications', id: 'certifications' },
  ];

  if (vendor.gallery_images && vendor.gallery_images.length > 0) {
    tabs.push({ name: 'Gallery', id: 'gallery' });
  }

  return (
    <Transition appear show={true} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                {/* Header */}
                <div className="relative px-6 py-6 border-b border-gray-200">
                  <button
                    onClick={onClose}
                    className="absolute top-6 right-6 text-gray-400 hover:text-gray-600"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>

                  <div className="flex items-start space-x-6">
                    {/* Logo */}
                    <div className="flex-shrink-0">
                      {vendor.logo_url ? (
                        <img
                          src={vendor.logo_url}
                          alt={`${vendor.name} logo`}
                          className="h-20 w-20 rounded-xl object-cover"
                        />
                      ) : (
                        <div className="h-20 w-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                          <span className="text-3xl font-bold text-white">
                            {vendor.name.charAt(0)}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Basic Info */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h2 className="text-2xl font-bold text-gray-900 mb-2">
                            {vendor.name}
                          </h2>
                          <p className="text-lg text-gray-600 mb-3">
                            {vendor.business_type}
                          </p>
                          
                          {/* Rating */}
                          <div className="flex items-center space-x-3 mb-4">
                            <div className="flex items-center">
                              {renderStars(vendor.average_rating)}
                            </div>
                            <span className="text-lg font-semibold text-gray-900">
                              {vendor.average_rating.toFixed(1)}
                            </span>
                            <span className="text-gray-600">
                              ({vendor.review_count} reviews)
                            </span>
                          </div>

                          {/* Categories */}
                          {vendor.categories && vendor.categories.length > 0 && (
                            <div className="flex flex-wrap gap-2">
                              {vendor.categories.map((category, index) => (
                                <span
                                  key={index}
                                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                                >
                                  {typeof category === 'object' ? category.icon : ''} {typeof category === 'object' ? category.name : category}
                                </span>
                              ))}
                            </div>
                          )}
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
                  </div>

                  {/* Action Buttons */}
                  <div className="mt-6 flex space-x-4">
                    <button
                      onClick={() => onCreateOrder?.(vendor)}
                      className="btn-primary flex-1"
                    >
                      Create Order
                    </button>
                    {vendor.website_url && (vendor.website_url.startsWith('http') || vendor.website_url.startsWith('https')) && (
                      <a
                        href={vendor.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-secondary flex items-center"
                      >
                        <GlobeAltIcon className="h-4 w-4 mr-2" />
                        Visit Website
                      </a>
                    )}
                  </div>
                </div>

                {/* Tabs */}
                <div className="px-6">
                  <Tab.Group>
                    <Tab.List className="flex space-x-1 border-b border-gray-200">
                      {tabs.map((tab) => (
                        <Tab
                          key={tab.id}
                          className={({ selected }) =>
                            classNames(
                              'py-3 px-4 text-sm font-medium border-b-2 focus:outline-none',
                              selected
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            )
                          }
                        >
                          {tab.name}
                        </Tab>
                      ))}
                    </Tab.List>

                    <Tab.Panels className="py-6">
                      {/* Overview Tab */}
                      <Tab.Panel className="space-y-6">
                        {/* Business Description */}
                        {vendor.business_description && (
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-3">
                              About {vendor.name}
                            </h3>
                            <p className="text-gray-700 leading-relaxed">
                              {vendor.business_description}
                            </p>
                          </div>
                        )}

                        {/* Specialties */}
                        {vendor.specialties && vendor.specialties.length > 0 && (
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-3">
                              Specialties
                            </h3>
                            <div className="flex flex-wrap gap-2">
                              {vendor.specialties.map((specialty, index) => (
                                <span
                                  key={index}
                                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800"
                                >
                                  {specialty}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Key Information */}
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-3">
                            Key Information
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {vendor.delivery_areas && (
                              <div className="flex items-start space-x-3">
                                <MapPinIcon className="h-5 w-5 text-gray-400 mt-0.5" />
                                <div>
                                  <p className="font-medium text-gray-900">Delivery Areas</p>
                                  <p className="text-gray-600">{vendor.delivery_areas}</p>
                                </div>
                              </div>
                            )}

                            {vendor.minimum_order > 0 && (
                              <div className="flex items-start space-x-3">
                                <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mt-0.5" />
                                <div>
                                  <p className="font-medium text-gray-900">Minimum Order</p>
                                  <p className="text-gray-600">{formatCurrency(vendor.minimum_order)}</p>
                                </div>
                              </div>
                            )}

                            {vendor.payment_terms && (
                              <div className="flex items-start space-x-3">
                                <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mt-0.5" />
                                <div>
                                  <p className="font-medium text-gray-900">Payment Terms</p>
                                  <p className="text-gray-600">{vendor.payment_terms}</p>
                                </div>
                              </div>
                            )}

                            {vendor.established_year && (
                              <div className="flex items-start space-x-3">
                                <CheckBadgeIcon className="h-5 w-5 text-gray-400 mt-0.5" />
                                <div>
                                  <p className="font-medium text-gray-900">Established</p>
                                  <p className="text-gray-600">{vendor.established_year}</p>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </Tab.Panel>

                      {/* Contact & Hours Tab */}
                      <Tab.Panel className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Contact Information */}
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                              Contact Information
                            </h3>
                            <div className="space-y-3">
                              <div className="flex items-center space-x-3">
                                <PhoneIcon className="h-5 w-5 text-gray-400" />
                                <a
                                  href={`tel:${vendor.phone}`}
                                  className="text-blue-600 hover:text-blue-800"
                                >
                                  {vendor.phone}
                                </a>
                              </div>
                              <div className="flex items-center space-x-3">
                                <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                                <a
                                  href={`mailto:${vendor.email}`}
                                  className="text-blue-600 hover:text-blue-800"
                                >
                                  {vendor.email}
                                </a>
                              </div>
                              <div className="flex items-start space-x-3">
                                <MapPinIcon className="h-5 w-5 text-gray-400 mt-0.5" />
                                <p className="text-gray-700">{vendor.address}</p>
                              </div>
                            </div>
                          </div>

                          {/* Business Hours */}
                          {vendor.business_hours && (
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                                Business Hours
                              </h3>
                              <div className="flex items-start space-x-3">
                                <ClockIcon className="h-5 w-5 text-gray-400 mt-0.5" />
                                <p className="text-gray-700 whitespace-pre-line">
                                  {vendor.business_hours}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                      </Tab.Panel>

                      {/* Certifications Tab */}
                      <Tab.Panel>
                        {vendor.certifications && vendor.certifications.length > 0 ? (
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                              Certifications & Credentials
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {vendor.certifications.map((cert, index) => (
                                <div
                                  key={index}
                                  className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg"
                                >
                                  <CheckBadgeIcon className="h-6 w-6 text-green-600" />
                                  <span className="font-medium text-green-800">{cert}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-8">
                            <CheckBadgeIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                            <p className="text-gray-500">No certifications listed</p>
                          </div>
                        )}
                      </Tab.Panel>

                      {/* Gallery Tab */}
                      {vendor.gallery_images && vendor.gallery_images.length > 0 && (
                        <Tab.Panel>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                              Gallery
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                              {vendor.gallery_images.map((image, index) => (
                                <img
                                  key={index}
                                  src={image}
                                  alt={`${vendor.name} gallery ${index + 1}`}
                                  className="w-full h-32 object-cover rounded-lg"
                                />
                              ))}
                            </div>
                          </div>
                        </Tab.Panel>
                      )}
                    </Tab.Panels>
                  </Tab.Group>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}