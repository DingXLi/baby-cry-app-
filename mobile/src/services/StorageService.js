/**
 * StorageService - AsyncStorage 持久化
 * 本地存储哭声记录和设置，无需后端即可独立运行
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const KEYS = {
  RECORDS: 'cry_records',
  SETTINGS: 'app_settings',
};

const DEFAULT_SETTINGS = {
  notifications: true,
  sound: true,
  vibration: true,
  backgroundMonitoring: false,
  sensitivity: 0.5,
  monitoringSchedule: { enabled: false, startTime: '22:00', endTime: '06:00' },
};

class StorageServiceClass {
  // ─── Records ─────────────────────────────────────────────────────────────

  async getAllRecords() {
    try {
      const raw = await AsyncStorage.getItem(KEYS.RECORDS);
      if (!raw) return [];
      const records = JSON.parse(raw);
      return records.map((r) => ({ ...r, timestamp: new Date(r.timestamp) }));
    } catch {
      return [];
    }
  }

  async addRecord(record) {
    try {
      const records = await this.getAllRecords();
      const newRecord = {
        id: `local-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        timestamp: new Date(),
        ...record,
      };
      records.unshift(newRecord);
      // Keep max 500 records locally
      const trimmed = records.slice(0, 500);
      await AsyncStorage.setItem(KEYS.RECORDS, JSON.stringify(trimmed));
      return newRecord;
    } catch (err) {
      console.error('StorageService.addRecord failed:', err);
      return null;
    }
  }

  async deleteRecord(id) {
    try {
      const records = await this.getAllRecords();
      const filtered = records.filter((r) => r.id !== id);
      await AsyncStorage.setItem(KEYS.RECORDS, JSON.stringify(filtered));
      return true;
    } catch {
      return false;
    }
  }

  async clearAllRecords() {
    try {
      await AsyncStorage.removeItem(KEYS.RECORDS);
      return true;
    } catch {
      return false;
    }
  }

  /** Records from the last N days */
  async getRecentRecords(days = 7) {
    const records = await this.getAllRecords();
    const cutoff = Date.now() - days * 86400000;
    return records.filter((r) => new Date(r.timestamp).getTime() >= cutoff);
  }

  /** Records from today */
  async getTodayRecords() {
    const records = await this.getAllRecords();
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return records.filter((r) => new Date(r.timestamp) >= today);
  }

  // ─── Stats ────────────────────────────────────────────────────────────────

  async getStats(days = 7) {
    const [allRecords, recentRecords, todayRecords] = await Promise.all([
      this.getAllRecords(),
      this.getRecentRecords(days),
      this.getTodayRecords(),
    ]);

    const typeDistribution = { hungry: 0, sleepy: 0, uncomfortable: 0, normal: 0 };
    for (const r of recentRecords) {
      if (typeDistribution[r.cryType] !== undefined) typeDistribution[r.cryType]++;
    }

    // Peak hours
    const hourCounts = {};
    for (const r of recentRecords) {
      const h = new Date(r.timestamp).getHours();
      hourCounts[h] = (hourCounts[h] || 0) + 1;
    }
    const peakHours = Object.entries(hourCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([h]) => parseInt(h));

    const daysSinceFirst = allRecords.length > 0
      ? Math.max(1, Math.ceil(
          (Date.now() - new Date(allRecords[allRecords.length - 1].timestamp).getTime()) / 86400000
        ))
      : 1;

    return {
      totalCries: allRecords.length,
      todayCries: todayRecords.length,
      recentCries: recentRecords.length,
      dailyAverage: parseFloat((allRecords.length / daysSinceFirst).toFixed(1)),
      typeDistribution,
      peakHours,
    };
  }

  // ─── Settings ─────────────────────────────────────────────────────────────

  async getSettings() {
    try {
      const raw = await AsyncStorage.getItem(KEYS.SETTINGS);
      if (!raw) return { ...DEFAULT_SETTINGS };
      return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
    } catch {
      return { ...DEFAULT_SETTINGS };
    }
  }

  async updateSettings(patch) {
    try {
      const current = await this.getSettings();
      const updated = { ...current, ...patch };
      await AsyncStorage.setItem(KEYS.SETTINGS, JSON.stringify(updated));
      return updated;
    } catch {
      return null;
    }
  }

  // ─── Export ───────────────────────────────────────────────────────────────

  async exportCSV() {
    const records = await this.getAllRecords();
    const header = 'id,cryType,confidence,duration,timestamp\n';
    const rows = records.map((r) =>
      `${r.id},${r.cryType},${r.confidence.toFixed(2)},${r.duration || ''},${new Date(r.timestamp).toISOString()}`
    );
    return header + rows.join('\n');
  }
}

export const StorageService = new StorageServiceClass();
export default StorageService;
