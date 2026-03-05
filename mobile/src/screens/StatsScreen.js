/**
 * Stats Screen - 统计页面
 * 🦞 虾虾开发
 */

import React from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// 模拟数据
const STATS_DATA = {
  totalCries: 23,
  todayCries: 5,
  typeDistribution: {
    hungry: 10,
    sleepy: 7,
    uncomfortable: 4,
    normal: 2,
  },
  peakHours: [2, 14, 22], // 凌晨 2 点、下午 2 点、晚上 10 点
};

export default function StatsScreen() {
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

  const total = Object.values(STATS_DATA.typeDistribution).reduce((a, b) => a + b, 0);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* 总览卡片 */}
      <View style={styles.overviewContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{STATS_DATA.totalCries}</Text>
          <Text style={styles.statLabel}>总次数</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{STATS_DATA.todayCries}</Text>
          <Text style={styles.statLabel}>今日</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{(STATS_DATA.todayCries / 1).toFixed(1)}</Text>
          <Text style={styles.statLabel}>日均</Text>
        </View>
      </View>

      {/* 类型分布 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>哭声类型分布</Text>
        <View style={styles.distributionContainer}>
          {Object.entries(STATS_DATA.typeDistribution).map(([type, count]) => {
            const percentage = total > 0 ? (count / total * 100).toFixed(1) : 0;
            return (
              <View key={type} style={styles.distributionItem}>
                <View style={styles.distributionHeader}>
                  <View style={styles.distributionLabel}>
                    <View style={[styles.colorDot, { backgroundColor: getCryTypeColor(type) }]} />
                    <Text style={styles.distributionText}>{getCryTypeText(type)}</Text>
                  </View>
                  <Text style={styles.distributionCount}>{count}次 ({percentage}%)</Text>
                </View>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      {
                        width: `${percentage}%`,
                        backgroundColor: getCryTypeColor(type),
                      },
                    ]}
                  />
                </View>
              </View>
            );
          })}
        </View>
      </View>

      {/* 高峰时段 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>高峰时段</Text>
        <View style={styles.peakHoursContainer}>
          {STATS_DATA.peakHours.map((hour) => (
            <View key={hour} style={styles.peakHourCard}>
              <Text style={styles.peakHourTime}>{hour}:00</Text>
              <Ionicons name="trending-up" size={20} color="#FF6B6B" />
            </View>
          ))}
        </View>
      </View>

      {/* 提示信息 */}
      <View style={styles.tipsContainer}>
        <Ionicons name="information-circle" size={24} color="#1976D2" />
        <Text style={styles.tipsText}>
          统计数据会随着使用逐渐丰富，帮助你更好地了解宝宝的哭声模式
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  overviewContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 15,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FF6B6B',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 14,
    color: '#999',
  },
  section: {
    backgroundColor: '#fff',
    marginVertical: 10,
    marginHorizontal: 20,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  distributionContainer: {
    gap: 15,
  },
  distributionItem: {
    gap: 8,
  },
  distributionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  distributionLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  colorDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  distributionText: {
    fontSize: 14,
    color: '#333',
  },
  distributionCount: {
    fontSize: 14,
    color: '#999',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  peakHoursContainer: {
    flexDirection: 'row',
    gap: 10,
    flexWrap: 'wrap',
  },
  peakHourCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF5F5',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    gap: 8,
  },
  peakHourTime: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  tipsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E3F2FD',
    margin: 20,
    padding: 15,
    borderRadius: 12,
    gap: 10,
  },
  tipsText: {
    flex: 1,
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
  },
});
