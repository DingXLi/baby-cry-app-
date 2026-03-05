/**
 * Settings Screen - 设置页面
 * 🦞 虾虾开发
 */

import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function SettingsScreen() {
  const [notifications, setNotifications] = useState(true);
  const [backgroundMonitoring, setBackgroundMonitoring] = useState(false);
  const [vibration, setVibration] = useState(true);
  const [sound, setSound] = useState(true);

  const SettingItem = ({ icon, title, description, value, onValueChange, type = 'switch' }) => (
    <View style={styles.settingItem}>
      <View style={styles.settingLeft}>
        <View style={[styles.iconContainer, { backgroundColor: '#FFF5F5' }]}>
          <Ionicons name={icon} size={24} color="#FF6B6B" />
        </View>
        <View style={styles.settingText}>
          <Text style={styles.settingTitle}>{title}</Text>
          {description && <Text style={styles.settingDescription}>{description}</Text>}
        </View>
      </View>
      {type === 'switch' && (
        <Switch
          value={value}
          onValueChange={onValueChange}
          trackColor={{ false: '#ddd', true: '#FF6B6B' }}
          thumbColor="#fff"
        />
      )}
      {type === 'arrow' && (
        <Ionicons name="chevron-forward" size={24} color="#ccc" />
      )}
    </View>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* 通知设置 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>通知</Text>
        <SettingItem
          icon="notifications"
          title="推送通知"
          description="检测到哭声时发送通知"
          value={notifications}
          onValueChange={setNotifications}
        />
        <SettingItem
          icon="volume-high"
          title="声音提醒"
          description="播放提示音"
          value={sound}
          onValueChange={setSound}
        />
        <SettingItem
          icon="phone-portrait"
          title="振动"
          description="检测到哭声时振动"
          value={vibration}
          onValueChange={setVibration}
        />
      </View>

      {/* 监听设置 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>监听</Text>
        <SettingItem
          icon="moon"
          title="后台监听"
          description="应用后台运行时继续监听"
          value={backgroundMonitoring}
          onValueChange={setBackgroundMonitoring}
        />
        <TouchableOpacity style={styles.settingItem} activeOpacity={0.7}>
          <View style={styles.settingLeft}>
            <View style={[styles.iconContainer, { backgroundColor: '#E8F5E9' }]}>
              <Ionicons name="time" size={24} color="#4CAF50" />
            </View>
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>监听时间段</Text>
              <Text style={styles.settingDescription}>设置自动监听的时间</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#ccc" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingItem} activeOpacity={0.7}>
          <View style={styles.settingLeft}>
            <View style={[styles.iconContainer, { backgroundColor: '#FFF3E0' }]}>
              <Ionicons name="sensitivity" size={24} color="#FF9800" />
            </View>
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>灵敏度</Text>
              <Text style={styles.settingDescription}>调整哭声检测灵敏度</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#ccc" />
        </TouchableOpacity>
      </View>

      {/* 数据管理 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>数据</Text>
        <TouchableOpacity style={styles.settingItem} activeOpacity={0.7}>
          <View style={styles.settingLeft}>
            <View style={[styles.iconContainer, { backgroundColor: '#E3F2FD' }]}>
              <Ionicons name="cloud-download" size={24} color="#2196F3" />
            </View>
            <View style={styles.settingText}>
              <Text style={styles.settingTitle">导出记录</Text>
              <Text style={styles.settingDescription}>导出哭声记录为 CSV</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#ccc" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingItem} activeOpacity={0.7}>
          <View style={styles.settingLeft}>
            <View style={[styles.iconContainer, { backgroundColor: '#FCE4EC' }]}>
              <Ionicons name="trash" size={24} color="#E91E63" />
            </View>
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>清除数据</Text>
              <Text style={styles.settingDescription}>删除所有本地记录</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#ccc" />
        </TouchableOpacity>
      </View>

      {/* 关于 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>关于</Text>
        <TouchableOpacity style={styles.settingItem} activeOpacity={0.7}>
          <View style={styles.settingLeft}>
            <View style={[styles.iconContainer, { backgroundColor: '#F3E5F5' }]}>
              <Ionicons name="information-circle" size={24} color="#9C27B0" />
            </View>
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>应用版本</Text>
              <Text style={styles.settingDescription}>Version 0.1.0</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#ccc" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingItem} activeOpacity={0.7}>
          <View style={styles.settingLeft}>
            <View style={[styles.iconContainer, { backgroundColor: '#E0F2F1' }]}>
              <Ionicons name="star" size={24} color="#009688" />
            </View>
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>给个好评</Text>
              <Text style={styles.settingDescription">支持虾虾开发</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={24} color="#ccc" />
        </TouchableOpacity>
      </View>

      {/* 底部信息 */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>🦞 虾虾开发</Text>
        <Text style={styles.footerSubtext}>Baby Cry Recognition App</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 20,
    paddingVertical: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#999',
    paddingHorizontal: 20,
    paddingVertical: 10,
    textTransform: 'uppercase',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f5f5f5',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingText: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 13,
    color: '#999',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  footerText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  footerSubtext: {
    fontSize: 14,
    color: '#999',
  },
});
