import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      // 服务器返回错误
      throw new Error(error.response.data.detail || error.response.data.message || '请求失败');
    } else if (error.request) {
      // 请求发送失败
      throw new Error('网络错误，请检查网络连接');
    } else {
      // 其他错误
      throw new Error('发生错误，请稍后重试');
    }
  }
);

export default api;
