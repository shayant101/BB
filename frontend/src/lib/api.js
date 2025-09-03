import axios from 'axios';

// API Configuration with robust fallback and validation
let API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// Validate and set API URL with proper error handling
function validateAndSetApiUrl() {
  // In production, API URL is required
  if (process.env.NODE_ENV === 'production' && !API_BASE_URL) {
    const error = 'FATAL: NEXT_PUBLIC_API_URL environment variable is not set for production.';
    console.error(error);
    throw new Error(error);
  }

  // For development, provide a robust fallback
  if (!API_BASE_URL) {
    API_BASE_URL = 'http://localhost:8000/api';
    console.warn(`⚠️ NEXT_PUBLIC_API_URL not set, defaulting to ${API_BASE_URL}`);
  }

  // Ensure API URL ends with /api for consistency
  if (!API_BASE_URL.endsWith('/api')) {
    if (API_BASE_URL.endsWith('/')) {
      API_BASE_URL = API_BASE_URL + 'api';
    } else {
      API_BASE_URL = API_BASE_URL + '/api';
    }
    console.info(`🔧 API URL normalized to: ${API_BASE_URL}`);
  }

  // Validate URL format
  try {
    new URL(API_BASE_URL);
    console.info(`✅ API Base URL configured: ${API_BASE_URL}`);
  } catch (error) {
    const errorMsg = `❌ Invalid API URL format: ${API_BASE_URL}`;
    console.error(errorMsg);
    throw new Error(errorMsg);
  }

  return API_BASE_URL;
}

// Initialize API URL with validation
API_BASE_URL = validateAndSetApiUrl();

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

// Request interceptor to add auth token (backend JWT or Clerk)
api.interceptors.request.use(
  async (config) => {
    console.log('🔍 API Request Interceptor triggered for:', config.url);
    
    try {
      // First, check for backend JWT token (for admin and backend login)
      const backendToken = safeLocalStorage.getItem('token');
      if (backendToken) {
        console.log('✅ Using backend JWT token for:', config.url);
        config.headers.Authorization = `Bearer ${backendToken}`;
        return config;
      }
      
      // If no backend token, try Clerk authentication
      if (typeof window !== 'undefined' && window.Clerk) {
        console.log('🔍 Clerk is available, checking user state...');
        
        // Check if user is signed in
        const user = window.Clerk.user;
        console.log('🔍 User state:', {
          hasUser: !!user,
          userId: user?.id,
          isSignedIn: !!user
        });
        
        if (user) {
          // Try to get session and token
          const session = window.Clerk.session;
          console.log('🔍 Session state:', {
            hasSession: !!session,
            sessionId: session?.id
          });
          
          if (session) {
            console.log('🔍 Attempting to get Clerk token...');
            const token = await session.getToken();
            console.log('🔍 Clerk token result:', {
              hasToken: !!token,
              tokenLength: token?.length,
              tokenPreview: token ? `${token.substring(0, 20)}...` : 'No token'
            });
            
            if (token) {
              config.headers.Authorization = `Bearer ${token}`;
              console.log('✅ Clerk authorization header set for:', config.url);
              return config;
            } else {
              console.log('❌ Failed to get token from Clerk session');
            }
          } else {
            console.log('❌ No Clerk session available');
          }
        } else {
          console.log('❌ No Clerk user signed in');
        }
      } else {
        console.log('❌ Clerk not available in window');
      }
      
      console.log('⚠️ Proceeding without authentication token for:', config.url);
    } catch (error) {
      console.error('❌ Error in request interceptor:', {
        error: error.message,
        url: config.url
      });
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors and API connectivity
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors - TEMPORARILY DISABLED FOR DEBUGGING
    if (error.response?.status === 401) {
      console.error('🚨 401 AUTHENTICATION ERROR');
      console.error('Error details:', {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
      
      removeAuthToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/sign-in';
      }
    }
    
    // Handle API connectivity issues
    if (!error.response) {
      console.error('❌ API Connection Error:', {
        message: error.message,
        code: error.code,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          baseURL: error.config?.baseURL
        }
      });
      
      // Check if it's a network error to the API
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        console.error(`🚨 Backend server appears to be down. Check if server is running on ${API_BASE_URL}`);
      }
    }
    
    return Promise.reject(error);
  }
);

// API Health Check Function
export const checkApiHealth = async () => {
  try {
    // Remove /api from base URL for health check since it's at root level
    const healthUrl = API_BASE_URL.replace('/api', '/health');
    const response = await axios.get(healthUrl, { timeout: 5000 });
    console.log('✅ API Health Check Passed:', response.data);
    return { healthy: true, data: response.data };
  } catch (error) {
    console.error('❌ API Health Check Failed:', error.message);
    return {
      healthy: false,
      error: error.message,
      suggestion: `Ensure backend server is running on ${API_BASE_URL.replace('/api', '')}`
    };
  }
};

// Initialize API health check in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  // Run health check after a short delay to allow server startup
  setTimeout(async () => {
    const health = await checkApiHealth();
    if (!health.healthy) {
      console.warn('⚠️ Backend server health check failed. Some features may not work properly.');
    }
  }, 2000);
}

// Auth API
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  
  // Email-based authentication endpoints
  emailLogin: async (email, password) => {
    const response = await api.post('/auth/login', { username: email, password });
    return response.data;
  },
  
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
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
  },
  
  setRole: async (role) => {
    const response = await api.post('/profiles/set-role', { role });
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
  },
  
  comparePrices: async (comparisonRequest) => {
    const response = await api.post('/marketplace/compare-prices', comparisonRequest);
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
  
  impersonateUser: async (userId, reason = "Admin impersonation") => {
    const response = await api.post(`/admin/users/${userId}/impersonate`, { reason });
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
// Storefront API
export const storefrontAPI = {
  getVendorProducts: async (vendorId) => {
    const response = await api.get(`/storefront/${vendorId}/products`);
    return response.data;
  },

  getCart: async (restaurantId) => {
    const response = await api.get(`/storefront/cart/${restaurantId}`);
    return response.data;
  },

  updateCart: async (restaurantId, cartData) => {
    const response = await api.post(`/storefront/cart/${restaurantId}`, cartData);
    return response.data;
  },

  addToWishlist: async (restaurantId, skuId) => {
    const response = await api.post(`/storefront/wishlist/${restaurantId}`, { sku_id: skuId });
    return response.data;
  },

  getWishlist: async (restaurantId) => {
    const response = await api.get(`/storefront/wishlist/${restaurantId}`);
    return response.data;
  },
};


export default api;