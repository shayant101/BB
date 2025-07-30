'use client';

import { useState } from 'react';
import OrderCard from './OrderCard';
import OrderDetails from './OrderDetails';

export default function OrderList({ orders, userRole, onRefresh }) {
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [filter, setFilter] = useState('all');

  const filteredOrders = orders.filter(order => {
    if (filter === 'all') return true;
    return order.status === filter;
  });

  const sortedOrders = filteredOrders.sort((a, b) => 
    new Date(b.created_at) - new Date(a.created_at)
  );

  if (selectedOrder) {
    return (
      <OrderDetails
        order={selectedOrder}
        userRole={userRole}
        onBack={() => setSelectedOrder(null)}
        onOrderUpdated={(updatedOrder) => {
          setSelectedOrder(updatedOrder);
          onRefresh();
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Filter Tabs - Modern Style */}
      <div className="bg-white rounded-xl shadow-sm p-1 flex space-x-1 border border-gray-200">
        {[
          { key: 'all', label: 'All', count: orders.length },
          { key: 'pending', label: 'Pending', count: orders.filter(o => o.status === 'pending').length },
          { key: 'confirmed', label: 'Confirmed', count: orders.filter(o => o.status === 'confirmed').length },
          { key: 'fulfilled', label: 'Fulfilled', count: orders.filter(o => o.status === 'fulfilled').length },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium text-sm transition-all duration-200 ${
              filter === tab.key
                ? 'bg-blue-600 text-white shadow-md transform hover:shadow-lg'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50 hover:shadow-sm'
            }`}
          >
            <span>{tab.label}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium shadow-sm ${
              filter === tab.key
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-600'
            }`}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {/* Orders Grid */}
      {sortedOrders.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No {filter === 'all' ? '' : filter} orders
          </h3>
          <p className="text-gray-600">
            {filter === 'all'
              ? 'No orders found'
              : `No ${filter} orders found`
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedOrders.map(order => (
            <OrderCard
              key={order.order_id}
              order={order}
              userRole={userRole}
              onClick={() => setSelectedOrder(order)}
              onStatusUpdate={onRefresh}
            />
          ))}
        </div>
      )}
    </div>
  );
}