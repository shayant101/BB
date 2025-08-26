"use client";

import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon, MinusIcon, PlusIcon, ShoppingCartIcon } from '@heroicons/react/24/outline';
import { useCart } from '../context/CartContext';
import { useParams } from 'next/navigation';
import api from '../lib/api';

export default function CartModal({ isOpen, onClose }) {
  const { cartItems, removeFromCart, updateQuantity, getCartTotal, clearCart } = useCart();
  const { vendorId } = useParams();
  const [isPlacingOrder, setIsPlacingOrder] = useState(false);
  const [orderError, setOrderError] = useState(null);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const handleQuantityChange = (productId, currentQuantity, change) => {
    const newQuantity = currentQuantity + change;
    updateQuantity(productId, newQuantity);
  };

  const handlePlaceOrder = async () => {
    if (!cartItems.length || !vendorId) return;

    setIsPlacingOrder(true);
    setOrderError(null);

    try {
      // Format cart data to match OrderCreate API model
      const orderData = {
        vendor_id: parseInt(vendorId),
        items: cartItems.map(item => ({
          product_id: String(item.product_id || item.id || ''), // API expects string, handle various field names
          name: item.name || 'Unknown Product', // Include product name for display
          quantity: item.quantity,
          price: item.price
        }))
      };

      console.log('🔍 Cart - Placing order with data:', orderData);

      // Use the configured API client with Clerk authentication
      const response = await api.post('/storefront/orders', orderData);
      
      console.log('🔍 Cart - Order response:', response.data);
      
      // Success: show notification, clear cart, close modal
      alert(`Order placed successfully! Order ID: ${response.data.order_id}`);
      clearCart();
      onClose();

    } catch (error) {
      console.error('❌ Cart - Error placing order:', error);
      
      // Handle different error formats
      let errorMessage = 'Failed to place order. Please try again.';
      
      if (error.response?.data) {
        const errorData = error.response.data;
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // Handle validation errors array
          errorMessage = errorData.detail.map(err =>
            typeof err === 'string' ? err : err.msg || 'Validation error'
          ).join(', ');
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setOrderError(errorMessage);
    } finally {
      setIsPlacingOrder(false);
    }
  };

  const subtotal = getCartTotal();
  const tax = subtotal * 0.08; // 8% tax rate
  const total = subtotal + tax;

  return (
    <Transition.Root show={isOpen} as={Fragment}>
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
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-500 sm:duration-700"
                enterFrom="translate-x-full"
                enterTo="translate-x-0"
                leave="transform transition ease-in-out duration-500 sm:duration-700"
                leaveFrom="translate-x-0"
                leaveTo="translate-x-full"
              >
                <Dialog.Panel className="pointer-events-auto w-screen max-w-md">
                  <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
                    {/* Header */}
                    <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
                      <div className="flex items-start justify-between">
                        <Dialog.Title className="text-lg font-medium text-gray-900">
                          Shopping Cart
                        </Dialog.Title>
                        <div className="ml-3 flex h-7 items-center">
                          <button
                            type="button"
                            className="relative -m-2 p-2 text-gray-400 hover:text-gray-500"
                            onClick={onClose}
                          >
                            <span className="absolute -inset-0.5" />
                            <span className="sr-only">Close panel</span>
                            <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                          </button>
                        </div>
                      </div>

                      {/* Cart Items */}
                      <div className="mt-8">
                        <div className="flow-root">
                          {cartItems.length === 0 ? (
                            <div className="text-center py-12">
                              <ShoppingCartIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                              <h3 className="text-lg font-medium text-gray-900 mb-2">Your cart is empty</h3>
                              <p className="text-gray-600">Add some products to get started!</p>
                            </div>
                          ) : (
                            <ul role="list" className="-my-6 divide-y divide-gray-200">
                              {cartItems.map((item) => (
                                <li key={item.product_id} className="flex py-6">
                                  <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-md border border-gray-200">
                                    {item.image_urls && item.image_urls.length > 0 ? (
                                      <img
                                        src={item.image_urls[0]}
                                        alt={item.name}
                                        className="h-full w-full object-cover object-center"
                                      />
                                    ) : (
                                      <div className="h-full w-full bg-gray-200 flex items-center justify-center">
                                        <ShoppingCartIcon className="h-8 w-8 text-gray-400" />
                                      </div>
                                    )}
                                  </div>

                                  <div className="ml-4 flex flex-1 flex-col">
                                    <div>
                                      <div className="flex justify-between text-base font-medium text-gray-900">
                                        <h3 className="line-clamp-2">{item.name}</h3>
                                        <p className="ml-4">{formatCurrency(item.price * item.quantity)}</p>
                                      </div>
                                      {item.description && (
                                        <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                                          {item.description}
                                        </p>
                                      )}
                                    </div>
                                    <div className="flex flex-1 items-end justify-between text-sm">
                                      <div className="flex items-center space-x-2">
                                        <span className="text-gray-500">Qty:</span>
                                        <div className="flex items-center space-x-1">
                                          <button
                                            onClick={() => handleQuantityChange(item.product_id, item.quantity, -1)}
                                            className="p-1 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            disabled={item.quantity <= 1}
                                          >
                                            <MinusIcon className="h-4 w-4 text-gray-600" />
                                          </button>
                                          <span className="w-8 text-center font-medium">{item.quantity}</span>
                                          <button
                                            onClick={() => handleQuantityChange(item.product_id, item.quantity, 1)}
                                            className="p-1 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                          >
                                            <PlusIcon className="h-4 w-4 text-gray-600" />
                                          </button>
                                        </div>
                                      </div>

                                      <div className="flex">
                                        <button
                                          type="button"
                                          onClick={() => removeFromCart(item.product_id)}
                                          className="font-medium text-red-600 hover:text-red-500"
                                        >
                                          Remove
                                        </button>
                                      </div>
                                    </div>
                                  </div>
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Footer with totals and checkout */}
                    {cartItems.length > 0 && (
                      <div className="border-t border-gray-200 px-4 py-6 sm:px-6">
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm text-gray-600">
                            <p>Subtotal</p>
                            <p>{formatCurrency(subtotal)}</p>
                          </div>
                          <div className="flex justify-between text-sm text-gray-600">
                            <p>Tax (8%)</p>
                            <p>{formatCurrency(tax)}</p>
                          </div>
                          <div className="flex justify-between text-base font-medium text-gray-900 border-t border-gray-200 pt-2">
                            <p>Total</p>
                            <p>{formatCurrency(total)}</p>
                          </div>
                        </div>
                        
                        {/* Error message */}
                        {orderError && (
                          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-sm text-red-600">{orderError}</p>
                          </div>
                        )}
                        
                        <div className="mt-6 space-y-3">
                          <button
                            type="button"
                            onClick={handlePlaceOrder}
                            disabled={isPlacingOrder || !vendorId}
                            className={`w-full border border-transparent rounded-md py-3 px-4 text-base font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                              isPlacingOrder || !vendorId
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700'
                            }`}
                          >
                            {isPlacingOrder ? 'Placing Order...' : 'Place Order'}
                          </button>
                          <button
                            type="button"
                            onClick={clearCart}
                            disabled={isPlacingOrder}
                            className={`w-full bg-white border border-gray-300 rounded-md py-2 px-4 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                              isPlacingOrder
                                ? 'text-gray-400 cursor-not-allowed'
                                : 'text-gray-700 hover:bg-gray-50'
                            }`}
                          >
                            Clear Cart
                          </button>
                        </div>
                        <div className="mt-6 flex justify-center text-center text-sm text-gray-500">
                          <p>
                            or{' '}
                            <button
                              type="button"
                              className="font-medium text-blue-600 hover:text-blue-500"
                              onClick={onClose}
                              disabled={isPlacingOrder}
                            >
                              Continue Shopping
                              <span aria-hidden="true"> &rarr;</span>
                            </button>
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}