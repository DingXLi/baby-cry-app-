/**
 * History Screen - 历史记录页面
 * 🦞 虾虾开发
 */

import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  FlatList,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// 模拟数据（后续替换为真实数据）
const MOCK_DATA = [
  {
    id: '1',
    cryType: 'hungry',
    confidence: 0.92,
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 分钟前
    duration: 5.2,
  },
  {
    id: '2',
    cryType: 'sleepy',
    confidence: 0.87,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 小时前
    duration: 3.8,
  },
  {
    id: '3',
    cryType: 'uncomfortable',
    confidence: 0.95,
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 小时前
    duration: 8.1,
  },
];

export default function HistoryScreen() {
  const [records, setRecords] = useState(MOCK_DATA);

  const getCryTypeIcon = (type) => {
    const icons = {
      hungry: 'restaurant',
      sleepy: 'moon',
      uncomfortable: 'warning',
      normal: 'happy',
    };
    return icons[type] || 'help-circle';
  };

  const getCryTypeColor = (type) => {
    const colors = {
      hungry: '#FF9F43',
      sleepy: '#5F27CD',
      uncomfortable: '#FF6B6B',
      normal: '#1DD1A1',
    };
    return colors[type] || '#ccc';
  };

  const getCryTypeText = (type) => {
    const texts = {
      hungry: '饿了',
      sleepy: '困了',
      uncomfortable: '不舒服',
      normal: '正常',
    };
    return texts[type] || '未知';
  };

  const formatTime = (date) => {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    return `${days}天前`;
  };

  const renderRecord = ({ item }) => (
    <TouchableOpacity style={styles.recordCard} activeOpacity={0.7}>
      <View style={[styles.iconContainer, { backgroundColor: getCryTypeColor(item.cryType) + '20' }]}>
        <Ionicons
          name={getCryTypeIcon(item.cryType)}
          size={24}
          color={getCryTypeColor(item.cryType)}
        />
      </View>
      <View style={styles.recordInfo}>
        <Text style={styles.recordType}>{getCryTypeText(item.cryType)}</Text>
        <Text style={styles.recordTime}>{formatTime(item.timestamp)}</Text>
      </View>
      <View style={styles.recordMeta}>
        <Text style={styles.confidence}>{(item.confidence * 100).toFixed(0)}%</Text>
        <Text style={styles.duration}>{item.duration.toFixed(1)}s</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {records.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="time-outline" size={80} color="#ccc" />
          <Text style={styles.emptyText}>暂无记录</Text>
          <Text style={styles.emptySubtext}>开始监听后，哭声记录会显示在这里</Text>
        </View>
      ) : (
        <>
          <View style={styles.header}>
            <Text style={styles.headerTitle}>今日记录</Text>
            <Text style={styles.headerCount}>{records.length} 条</Text>
          </View>
          <FlatList
            data={records}
            renderItem={renderRecord}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContainer}
            showsVerticalScrollIndicator={false}
          />
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  headerCount: {
    fontSize: 14,
    color: '#999',
  },
  listContainer: {
    padding: 20,
  },
  recordCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  iconContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordInfo: {
    flex: 1,
    marginLeft: 15,
  },
  recordType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  recordTime: {
    fontSize: 13,
    color: '#999',
  },
  recordMeta: {
    alignItems: 'flex-end',
  },
  confidence: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1DD1A1',
    marginBottom: 2,
  },
  duration: {
    fontSize: 12,
    color: '#999',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#999',
    marginTop: 20,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#ccc',
    marginTop: 8,
    textAlign: 'center',
  },
});
