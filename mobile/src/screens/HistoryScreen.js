/**
 * History Screen - 历史记录页面
 * 🦞 虾虾开发
 */

import React, { useState, useCallback } from 'react';
import {
  StyleSheet,
  Text,
  View,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
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

function timeAgo(date) {
  const diff = Date.now() - new Date(date).getTime();
  const m = Math.floor(diff / 60000);
  const h = Math.floor(diff / 3600000);
  const d = Math.floor(diff / 86400000);
  if (m < 1) return '刚刚';
  if (m < 60) return `${m}分钟前`;
  if (h < 24) return `${h}小时前`;
  return `${d}天前`;
}

export default function HistoryScreen() {
  const [records, setRecords] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all');

  const loadRecords = useCallback(async () => {
    const all = await StorageService.getAllRecords();
    setRecords(all);
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadRecords();
    }, [loadRecords])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await loadRecords();
    setRefreshing(false);
  };

  const handleDelete = (id) => {
    Alert.alert('删除记录', '确定要删除这条记录吗？', [
      { text: '取消', style: 'cancel' },
      {
        text: '删除',
        style: 'destructive',
        onPress: async () => {
          await StorageService.deleteRecord(id);
          setRecords((prev) => prev.filter((r) => r.id !== id));
        },
      },
    ]);
  };

  const handleClearAll = () => {
    Alert.alert('清空记录', '确定要删除所有记录吗？此操作不可撤销。', [
      { text: '取消', style: 'cancel' },
      {
        text: '清空',
        style: 'destructive',
        onPress: async () => {
          await StorageService.clearAllRecords();
          setRecords([]);
        },
      },
    ]);
  };

  const FILTERS = [
    { key: 'all', label: '全部' },
    { key: 'hungry', label: '饿了' },
    { key: 'sleepy', label: '困了' },
    { key: 'uncomfortable', label: '不舒服' },
    { key: 'normal', label: '正常' },
  ];

  const filtered = filter === 'all' ? records : records.filter((r) => r.cryType === filter);

  const renderRecord = ({ item }) => {
    const meta = CRY_META[item.cryType] || CRY_META.normal;
    return (
      <TouchableOpacity
        style={styles.recordCard}
        activeOpacity={0.75}
        onLongPress={() => handleDelete(item.id)}
      >
        <View style={[styles.iconWrap, { backgroundColor: meta.color + '20' }]}>
          <Ionicons name={meta.icon} size={24} color={meta.color} />
        </View>
        <View style={styles.recordInfo}>
          <Text style={styles.recordType}>{meta.text}</Text>
          <Text style={styles.recordTime}>{timeAgo(item.timestamp)}</Text>
        </View>
        <View style={styles.recordMeta}>
          <Text style={[styles.confidence, { color: meta.color }]}>
            {(item.confidence * 100).toFixed(0)}%
          </Text>
          {item.duration ? (
            <Text style={styles.duration}>{item.duration.toFixed(1)}s</Text>
          ) : null}
        </View>
      </TouchableOpacity>
    );
  };

  const ListHeader = () => (
    <View style={styles.listHeader}>
      <View style={styles.countRow}>
        <Text style={styles.countTitle}>共 {filtered.length} 条记录</Text>
        {records.length > 0 && (
          <TouchableOpacity onPress={handleClearAll}>
            <Text style={styles.clearBtn}>清空</Text>
          </TouchableOpacity>
        )}
      </View>
      {/* Filter chips */}
      <View style={styles.filterRow}>
        {FILTERS.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[styles.chip, filter === f.key && styles.chipActive]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.chipText, filter === f.key && styles.chipTextActive]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {records.length === 0 ? (
        <View style={styles.empty}>
          <Ionicons name="time-outline" size={72} color="#ddd" />
          <Text style={styles.emptyTitle}>暂无记录</Text>
          <Text style={styles.emptyHint}>开始监听后，哭声记录会显示在这里</Text>
        </View>
      ) : (
        <FlatList
          data={filtered}
          renderItem={renderRecord}
          keyExtractor={(item) => item.id}
          ListHeaderComponent={ListHeader}
          contentContainerStyle={styles.list}
          showsVerticalScrollIndicator={false}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#FF6B6B']} />}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  listHeader: { paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  countRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  countTitle: { fontSize: 15, fontWeight: '600', color: '#555' },
  clearBtn: { fontSize: 14, color: '#FF6B6B' },
  filterRow: { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  chipActive: { backgroundColor: '#FF6B6B', borderColor: '#FF6B6B' },
  chipText: { fontSize: 13, color: '#666' },
  chipTextActive: { color: '#fff', fontWeight: '600' },
  list: { padding: 16 },
  recordCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
  },
  iconWrap: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordInfo: { flex: 1, marginLeft: 14 },
  recordType: { fontSize: 16, fontWeight: '600', color: '#333', marginBottom: 3 },
  recordTime: { fontSize: 13, color: '#aaa' },
  recordMeta: { alignItems: 'flex-end' },
  confidence: { fontSize: 15, fontWeight: '700', marginBottom: 2 },
  duration: { fontSize: 12, color: '#bbb' },
  empty: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40 },
  emptyTitle: { fontSize: 18, fontWeight: '600', color: '#ccc', marginTop: 16 },
  emptyHint: { fontSize: 14, color: '#ddd', marginTop: 8, textAlign: 'center' },
});
