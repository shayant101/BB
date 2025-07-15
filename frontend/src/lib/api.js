import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

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

// Token management
export const setAuthToken = (token) => {
  if (token) {
    safeLocalStorage.setItem('token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    safeLocalStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
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

// Initialize token from localStorage on app start (client-side only)
if (typeof window !== 'undefined') {
  const token = getAuthToken();
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
}

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
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

export default api;