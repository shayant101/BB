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
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { key: 'all', label: 'All Orders', count: orders.length },
          { key: 'pending', label: 'Pending', count: orders.filter(o => o.status === 'pending').length },
          { key: 'confirmed', label: 'Confirmed', count: orders.filter(o => o.status === 'confirmed').length },
          { key: 'fulfilled', label: 'Fulfilled', count: orders.filter(o => o.status === 'fulfilled').length },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              filter === tab.key
                ? 'bg-white text-primary shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      {/* Orders Grid */}
      {sortedOrders.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">📭</div>
          <p className="text-gray-600">
            {filter === 'all' 
              ? 'No orders found' 
              : `No ${filter} orders found`
            }
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {sortedOrders.map(order => (
            <OrderCard
              key={order.id}
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