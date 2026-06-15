/**
 * ApiService - 后端 API 客户端（可选云同步）
 * 移动端可在无后端时独立工作（StorageService 处理本地数据）
 * 配置 API_BASE_URL 后自动启用云同步
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || null; // 不配置则只用本地存储
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

class ApiServiceClass {
  constructor() {
    this.token = null;
    this.baseUrl = API_BASE_URL;
  }

  get isConfigured() {
    return !!this.baseUrl;
  }

  async init() {
    this.token = await AsyncStorage.getItem(TOKEN_KEY);
  }

  // ─── HTTP Helpers ─────────────────────────────────────────────────────────

  async request(method, path, body = null) {
    if (!this.isConfigured) return null;

    const headers = { 'Content-Type': 'application/json' };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    try {
      const res = await fetch(`${this.baseUrl}${path}`, opts);
      const json = await res.json();
      if (!res.ok) throw new Error(json.error?.message || 'API Error');
      return json.data;
    } catch (err) {
      console.warn(`ApiService ${method} ${path} failed:`, err.message);
      return null;
    }
  }

  // ─── Auth ─────────────────────────────────────────────────────────────────

  async register(email, password, name) {
    const data = await this.request('POST', '/api/v1/auth/register', { email, password, name });
    if (data?.token) {
      this.token = data.token;
      await AsyncStorage.setItem(TOKEN_KEY, data.token);
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(data.user));
    }
    return data;
  }

  async login(email, password) {
    const data = await this.request('POST', '/api/v1/auth/login', { email, password });
    if (data?.token) {
      this.token = data.token;
      await AsyncStorage.setItem(TOKEN_KEY, data.token);
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(data.user));
    }
    return data;
  }

  async logout() {
    this.token = null;
    await AsyncStorage.multiRemove([TOKEN_KEY, USER_KEY]);
  }

  async getCurrentUser() {
    const raw = await AsyncStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  }

  // ─── Cry Records ──────────────────────────────────────────────────────────

  async syncRecord(record) {
    if (!this.token) return null;
    return this.request('POST', '/api/v1/cry-records', {
      cryType: record.cryType,
      confidence: record.confidence,
      duration: record.duration,
      timestamp: new Date(record.timestamp).toISOString(),
    });
  }

  async fetchRecords(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request('GET', `/api/v1/cry-records${qs ? '?' + qs : ''}`);
  }

  // ─── Analytics ────────────────────────────────────────────────────────────

  async fetchSummary(period = '7d') {
    return this.request('GET', `/api/v1/analytics/summary?period=${period}`);
  }

  async fetchTrends(period = '7d', groupBy = 'day') {
    return this.request('GET', `/api/v1/analytics/trends?period=${period}&groupBy=${groupBy}`);
  }
}

export const ApiService = new ApiServiceClass();
export default ApiService;
