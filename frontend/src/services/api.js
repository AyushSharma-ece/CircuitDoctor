/**
 * CircuitDoctor - API Client Service
 * Centralized Axios instance with type-safe endpoint wrappers.
 */

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 60000,
  headers: {
    'Accept': 'application/json',
  }
});

// Interceptor for standardized error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const errorMsg = error.response?.data?.detail || error.message || 'Network communication error';
    console.error(`[CircuitDoctor API Error]:`, errorMsg);
    return Promise.reject(new Error(errorMsg));
  }
);

export const getHealth = () => api.get('/api/health');
export const getModelInfo = () => api.get('/api/model/info');
export const getDatasetInfo = () => api.get('/api/dataset/info');
export const getStatistics = () => api.get('/api/statistics');

export const getInspections = (params = {}) => api.get('/api/inspections', { params });
export const getInspectionById = (id) => api.get(`/api/inspections/${id}`);
export const deleteInspection = (id) => api.delete(`/api/inspections/${id}`);

export const uploadAndInspect = (formData, config = {}) => {
  return api.post('/api/inspect', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    ...config,
  });
};

export const getReportDownloadUrl = (id) => `/api/inspections/${id}/report`;
export const getOriginalImageUrl = (id) => `/api/images/original/${id}`;
export const getAnnotatedImageUrl = (id) => `/api/images/annotated/${id}`;

export default api;
