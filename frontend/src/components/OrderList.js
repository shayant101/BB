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
      {/* Filter Tabs - Neo-Brutalist Style */}
      <div className="filter-tabs-neo">
        {[
          { key: 'all', label: 'ALL', count: orders.length },
          { key: 'pending', label: 'PENDING', count: orders.filter(o => o.status === 'pending').length },
          { key: 'confirmed', label: 'CONFIRMED', count: orders.filter(o => o.status === 'confirmed').length },
          { key: 'fulfilled', label: 'FULFILLED', count: orders.filter(o => o.status === 'fulfilled').length },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`filter-tab-neo ${filter === tab.key ? 'filter-tab-active' : ''}`}
          >
            <span className="font-black">{tab.label}</span>
            <span className="tab-count">{tab.count}</span>
          </button>
        ))}
      </div>

      {/* Orders Grid */}
      {sortedOrders.length === 0 ? (
        <div className="empty-state-neo">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-black text-gray-900 mb-2">
            NO {filter.toUpperCase()} ORDERS
          </h3>
          <p className="text-gray-600 font-medium">
            {filter === 'all'
              ? 'No orders found'
              : `No ${filter} orders found`
            }
          </p>
        </div>
      ) : (
        <div className="orders-grid-neo">
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