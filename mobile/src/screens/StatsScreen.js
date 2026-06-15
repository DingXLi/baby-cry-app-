/**
 * Stats Screen - 统计分析页面
 * 🦞 虾虾开发
 */

import React, { useState, useCallback } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import StorageService from '../services/StorageService';

const CRY_META = {
  hungry:        { icon: 'restaurant', color: '#FF9F43', text: '饿了' },
  sleepy:        { icon: 'moon',       color: '#5F27CD', text: '困了' },
  uncomfortable: { icon: 'warning',    color: '#FF6B6B', text: '不舒服' },
  normal:        { icon: 'happy',      color: '#1DD1A1', text: '正常' },
};

const PERIOD_OPTIONS = [
  { label: '今日', days: 1 },
  { label: '7天', days: 7 },
  { label: '30天', days: 30 },
];

export default function StatsScreen() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState(7);

  const loadStats = useCallback(async () => {
    setLoading(true);
    const s = await StorageService.getStats(period);
    setStats(s);
    setLoading(false);
  }, [period]);

  useFocusEffect(
    useCallback(() => {
      loadStats();
    }, [loadStats])
  );

  const total = stats
    ? Object.values(stats.typeDistribution).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* 时段选择 */}
      <View style={styles.periodRow}>
        {PERIOD_OPTIONS.map((opt) => (
          <TouchableOpacity
            key={opt.days}
            style={[styles.periodBtn, period === opt.days && styles.periodBtnActive]}
            onPress={() => setPeriod(opt.days)}
          >
            <Text style={[styles.periodText, period === opt.days && styles.periodTextActive]}>
              {opt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <View style={styles.loadingWrap}>
          <ActivityIndicator color="#FF6B6B" size="large" />
        </View>
      ) : stats && total === 0 ? (
        <View style={styles.empty}>
          <Ionicons name="bar-chart-outline" size={72} color="#ddd" />
          <Text style={styles.emptyTitle}>暂无数据</Text>
          <Text style={styles.emptyHint}>开始监听并记录哭声后，统计会在这里展示</Text>
        </View>
      ) : (
        <>
          {/* 总览卡片 */}
          <View style={styles.overviewRow}>
            {[
              { label: '总次数', value: stats.totalCries },
              { label: '今日',   value: stats.todayCries },
              { label: '日均',   value: stats.dailyAverage },
            ].map((item) => (
              <View key={item.label} style={styles.statCard}>
                <Text style={styles.statValue}>{item.value}</Text>
                <Text style={styles.statLabel}>{item.label}</Text>
              </View>
            ))}
          </View>

          {/* 类型分布 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>哭声类型分布</Text>
            {Object.entries(stats.typeDistribution)
              .sort((a, b) => b[1] - a[1])
              .map(([type, count]) => {
                const meta = CRY_META[type];
                const pct = total > 0 ? (count / total) * 100 : 0;
                return (
                  <View key={type} style={styles.distItem}>
                    <View style={styles.distHeader}>
                      <View style={styles.distLabel}>
                        <Ionicons name={meta.icon} size={16} color={meta.color} />
                        <Text style={styles.distText}>{meta.text}</Text>
                      </View>
                      <Text style={styles.distCount}>
                        {count}次 · {pct.toFixed(1)}%
                      </Text>
                    </View>
                    <View style={styles.bar}>
                      <View
                        style={[styles.barFill, { width: `${pct}%`, backgroundColor: meta.color }]}
                      />
                    </View>
                  </View>
                );
              })}
          </View>

          {/* 高峰时段 */}
          {stats.peakHours.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>高峰时段</Text>
              <View style={styles.peakRow}>
                {stats.peakHours.map((h) => (
                  <View key={h} style={styles.peakChip}>
                    <Ionicons name="time-outline" size={16} color="#FF6B6B" />
                    <Text style={styles.peakText}>{String(h).padStart(2, '0')}:00</Text>
                  </View>
                ))}
              </View>
              <Text style={styles.peakHint}>宝宝在这些时段最容易哭闹，提前做好准备吧</Text>
            </View>
          )}

          {/* 贴士 */}
          <View style={styles.tipBox}>
            <Ionicons name="bulb-outline" size={20} color="#1976D2" />
            <Text style={styles.tipText}>
              数据越多，分析越准确。坚持使用帮助你掌握宝宝的规律。
            </Text>
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  periodRow: {
    flexDirection: 'row',
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 2,
  },
  periodBtn: { flex: 1, paddingVertical: 8, alignItems: 'center', borderRadius: 8 },
  periodBtnActive: { backgroundColor: '#FF6B6B' },
  periodText: { fontSize: 14, color: '#888', fontWeight: '500' },
  periodTextActive: { color: '#fff', fontWeight: '700' },
  loadingWrap: { height: 200, justifyContent: 'center', alignItems: 'center' },
  empty: { alignItems: 'center', paddingVertical: 80 },
  emptyTitle: { fontSize: 18, fontWeight: '600', color: '#ccc', marginTop: 16 },
  emptyHint: { fontSize: 14, color: '#ddd', marginTop: 8, textAlign: 'center', paddingHorizontal: 40 },
  overviewRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    gap: 12,
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: { fontSize: 26, fontWeight: 'bold', color: '#FF6B6B' },
  statLabel: { fontSize: 12, color: '#aaa', marginTop: 4 },
  section: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
    padding: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: '#333', marginBottom: 16 },
  distItem: { marginBottom: 14 },
  distHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  distLabel: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  distText: { fontSize: 14, color: '#333' },
  distCount: { fontSize: 13, color: '#999' },
  bar: { height: 8, backgroundColor: '#f0f0f0', borderRadius: 4, overflow: 'hidden' },
  barFill: { height: '100%', borderRadius: 4 },
  peakRow: { flexDirection: 'row', gap: 10, flexWrap: 'wrap', marginBottom: 10 },
  peakChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#FFF5F5',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
  },
  peakText: { fontSize: 14, fontWeight: '600', color: '#333' },
  peakHint: { fontSize: 13, color: '#aaa', lineHeight: 18 },
  tipBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#E3F2FD',
    margin: 16,
    padding: 14,
    borderRadius: 10,
    gap: 10,
    marginBottom: 30,
  },
  tipText: { flex: 1, fontSize: 13, color: '#555', lineHeight: 20 },
});
