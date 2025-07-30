import axios from 'axios';

let API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// In a production environment, the API URL must be set.
// This prevents deploying a broken frontend.
if (process.env.NODE_ENV === 'production' && !API_BASE_URL) {
  console.error('FATAL: NEXT_PUBLIC_API_URL environment variable is not set for production.');
  // Note: This will cause an error, but a visible one.
  // In a real CI/CD pipeline, you'd want the build to fail here.
  API_BASE_URL = ''; // Set to empty to ensure requests fail visibly.
}

// For local development, we can default to localhost.
if (!API_BASE_URL) {
  API_BASE_URL = 'http://localhost:8000/api';
  console.warn(`⚠️ NEXT_PUBLIC_API_URL not set, defaulting to ${API_BASE_URL}`);
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Safe localStorage access for SSR compatibility
const safeLocalStorage = {
  getItem: (key) => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(key);
    }
    return null;
  },
  setItem: (key, value) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(key, value);
    }
  },
  removeItem: (key) => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(key);
    }
  }
};

// Token management - Enhanced with debugging
export const setAuthToken = (token) => {
  console.log('🔧 setAuthToken called:', {
    hasToken: !!token,
    tokenPreview: token ? `${token.substring(0, 20)}...` : 'No token',
    timestamp: new Date().toISOString(),
    stackTrace: new Error().stack
  });
  
  if (token) {
    // Store in localStorage
    safeLocalStorage.setItem('token', token);
    console.log('✅ Token stored in localStorage');
    
    // Set in multiple places to ensure it's always available
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    console.log('✅ Token set in API headers');
  } else {
    console.log('🗑️ Removing token');
    safeLocalStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    delete api.defaults.headers['Authorization'];
  }
};

export const getAuthToken = () => {
  return safeLocalStorage.getItem('token');
};

export const removeAuthToken = () => {
  safeLocalStorage.removeItem('token');
  safeLocalStorage.removeItem('user');
  delete api.defaults.headers.common['Authorization'];
};

// User management
export const setUser = (user) => {
  safeLocalStorage.setItem('user', JSON.stringify(user));
};

export const getUser = () => {
  const user = safeLocalStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

// Token initialization is now handled in a client-side component
// to ensure it only runs in the browser.

// Request interceptor to add token - Enhanced with debugging
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    
    // Debug logging
    console.log('🔍 API Request Interceptor:', {
      url: config.url,
      method: config.method,
      hasToken: !!token,
      tokenPreview: token ? `${token.substring(0, 20)}...` : 'No token',
      headers: config.headers
    });
    
    if (token) {
      // Set both Authorization header and ensure it's in the config
      config.headers.Authorization = `Bearer ${token}`;
      config.headers['Authorization'] = `Bearer ${token}`;
      
      // Also ensure it's in the default headers
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      console.log('✅ Token attached to request:', config.url);
    } else {
      console.log('❌ No token available for request:', config.url);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeAuthToken();
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  
  googleLogin: async (token, role = 'restaurant') => {
    const response = await api.post('/auth/google', { token, role });
    return response.data;
  },
  
  updateGoogleUserRole: async (token, role) => {
    const response = await api.put('/auth/google/role', { token, role });
    return response.data;
  },
  
  getGoogleConfig: async () => {
    const response = await api.get('/auth/google/config');
    return response.data;
  },
  
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      removeAuthToken();
    }
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

// Orders API
export const ordersAPI = {
  getOrders: async () => {
    const response = await api.get('/orders');
    return response.data;
  },
  
  getOrder: async (id) => {
    const response = await api.get(`/orders/${id}`);
    return response.data;
  },
  
  createOrder: async (orderData) => {
    const response = await api.post('/orders', orderData);
    return response.data;
  },
  
  updateOrderStatus: async (id, status) => {
    const response = await api.put(`/orders/${id}/status`, { status });
    return response.data;
  },
  
  updateOrderNotes: async (id, notes) => {
    const response = await api.put(`/orders/${id}/notes`, { notes });
    return response.data;
  },
  
  deleteOrder: async (id) => {
    const response = await api.delete(`/orders/${id}`);
    return response.data;
  }
};

// Profiles API
export const profilesAPI = {
  getProfile: async () => {
    const response = await api.get('/profiles/me');
    return response.data;
  },
  
  updateProfile: async (profileData) => {
    const response = await api.put('/profiles/me', profileData);
    return response.data;
  },
  
  getVendors: async () => {
    const response = await api.get('/profiles/vendors');
    return response.data;
  },
  
  getRestaurants: async () => {
    const response = await api.get('/profiles/restaurants');
    return response.data;
  }
};

// Marketplace API
export const marketplaceAPI = {
  getVendors: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/marketplace/vendors${queryString ? `?${queryString}` : ''}`);
    return response.data;
  },
  
  getVendorDetail: async (id) => {
    const response = await api.get(`/marketplace/vendors/${id}`);
    return response.data;
  },
  
  getCategories: async () => {
    const response = await api.get('/marketplace/categories');
    return response.data;
  },
  
  searchVendors: async (query) => {
    const response = await api.get(`/marketplace/search?q=${encodeURIComponent(query)}`);
    return response.data;
  }
};

// Admin API
export const adminAPI = {
  getDashboardStats: async () => {
    const response = await api.get('/admin/dashboard-stats');
    return response.data;
  },
  
  getActionQueues: async () => {
    const response = await api.get('/admin/action-queues');
    return response.data;
  },
  
  getUsers: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/admin/users${queryString ? `?${queryString}` : ''}`);
    return response.data;
  },
  
  updateUserStatus: async (userId, status) => {
    const response = await api.put(`/admin/users/${userId}/status`, { status });
    return response.data;
  },
  
  deleteUser: async (userId) => {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },
  
  createUser: async (userData) => {
    const response = await api.post('/admin/users', userData);
    return response.data;
  },
  
  impersonateUser: async (userId) => {
    const response = await api.post(`/admin/users/${userId}/impersonate`);
    return response.data;
  },
  
  getAuditLogs: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/admin/audit-logs${queryString ? `?${queryString}` : ''}`);
    return response.data;
  }
};

// Inventory API
export const inventoryAPI = {
  // Categories
  getCategories: async (includeInactive = false) => {
    const response = await api.get(`/inventory/categories?include_inactive=${includeInactive}`);
    return response.data;
  },
  
  getCategory: async (categoryId) => {
    const response = await api.get(`/inventory/categories/${categoryId}`);
    return response.data;
  },
  
  createCategory: async (categoryData) => {
    const response = await api.post('/inventory/categories', categoryData);
    return response.data;
  },
  
  updateCategory: async (categoryId, categoryData) => {
    const response = await api.put(`/inventory/categories/${categoryId}`, categoryData);
    return response.data;
  },
  
  deleteCategory: async (categoryId) => {
    const response = await api.delete(`/inventory/categories/${categoryId}`);
    return response.data;
  },
  
  // Items
  getItems: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/inventory/items${queryString ? `?${queryString}` : ''}`);
    return response.data;
  },
  
  getItem: async (itemId) => {
    const response = await api.get(`/inventory/items/${itemId}`);
    return response.data;
  },
  
  createItem: async (itemData) => {
    const response = await api.post('/inventory/items', itemData);
    return response.data;
  },
  
  updateItem: async (itemId, itemData) => {
    const response = await api.put(`/inventory/items/${itemId}`, itemData);
    return response.data;
  },
  
  deleteItem: async (itemId) => {
    const response = await api.delete(`/inventory/items/${itemId}`);
    return response.data;
  },
  
  getCategoryItems: async (categoryId, params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/inventory/categories/${categoryId}/items${queryString ? `?${queryString}` : ''}`);
    return response.data;
  },
  
  // SKUs
  getSKUs: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/inventory/skus${queryString ? `?${queryString}` : ''}`);
    return response.data;
  },
  
  getSKU: async (skuId) => {
    const response = await api.get(`/inventory/skus/${skuId}`);
    return response.data;
  },
  
  createSKU: async (skuData) => {
    const response = await api.post('/inventory/skus', skuData);
    return response.data;
  },
  
  updateSKU: async (skuId, skuData) => {
    const response = await api.put(`/inventory/skus/${skuId}`, skuData);
    return response.data;
  },
  
  deleteSKU: async (skuId) => {
    const response = await api.delete(`/inventory/skus/${skuId}`);
    return response.data;
  },
  
  getItemSKUs: async (itemId, includeInactive = false) => {
    const response = await api.get(`/inventory/items/${itemId}/skus?include_inactive=${includeInactive}`);
    return response.data;
  },
  
  // Stock management
  updateStock: async (skuId, quantityChange, operation = 'set') => {
    const response = await api.patch(`/inventory/skus/${skuId}/stock?quantity_change=${quantityChange}&operation=${operation}`);
    return response.data;
  },
  
  // Dashboard/Summary
  getInventorySummary: async () => {
    const response = await api.get('/inventory/summary');
    return response.data;
  }
};

export default api;