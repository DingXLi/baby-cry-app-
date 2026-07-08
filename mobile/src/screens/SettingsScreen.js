/**
 * Settings Screen - 设置页面
 * 🦞 虾虾开发
 */

import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  Share,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import StorageService from '../services/StorageService';

const APP_VERSION = '1.0.0';

export default function SettingsScreen() {
  const [settings, setSettings] = useState({
    notifications: true,
    sound: true,
    vibration: true,
    backgroundMonitoring: false,
  });

  useEffect(() => {
    StorageService.getSettings().then(setSettings);
  }, []);

  const updateSetting = async (key, value) => {
    const updated = { ...settings, [key]: value };
    setSettings(updated);
    await StorageService.updateSettings({ [key]: value });
  };

  const handleExport = async () => {
    try {
      const csv = await StorageService.exportCSV();
      if (!csv || csv.split('\n').length <= 1) {
        Alert.alert('提示', '暂无记录可导出');
        return;
      }
      await Share.share({ message: csv, title: '哭声记录导出' });
    } catch {
      Alert.alert('错误', '导出失败');
    }
  };

  const handleClearData = () => {
    Alert.alert('清除数据', '确定要删除所有本地记录吗？此操作不可撤销。', [
      { text: '取消', style: 'cancel' },
      {
        text: '清除',
        style: 'destructive',
        onPress: async () => {
          await StorageService.clearAllRecords();
          Alert.alert('完成', '所有记录已清除');
        },
      },
    ]);
  };

  const SettingSwitch = ({ icon, iconBg, title, description, settingKey }) => (
    <View style={styles.settingItem}>
      <View style={[styles.iconWrap, { backgroundColor: iconBg }]}>
        <Ionicons name={icon} size={22} color="#FF6B6B" />
      </View>
      <View style={styles.settingText}>
        <Text style={styles.settingTitle}>{title}</Text>
        {description && <Text style={styles.settingDesc}>{description}</Text>}
      </View>
      <Switch
        value={settings[settingKey]}
        onValueChange={(v) => updateSetting(settingKey, v)}
        trackColor={{ false: '#ddd', true: '#FF6B6B' }}
        thumbColor="#fff"
      />
    </View>
  );

  const SettingAction = ({ icon, iconBg, iconColor, title, description, onPress, danger }) => (
    <TouchableOpacity style={styles.settingItem} onPress={onPress} activeOpacity={0.7}>
      <View style={[styles.iconWrap, { backgroundColor: iconBg }]}>
        <Ionicons name={icon} size={22} color={iconColor || '#FF6B6B'} />
      </View>
      <View style={styles.settingText}>
        <Text style={[styles.settingTitle, danger && { color: '#E91E63' }]}>{title}</Text>
        {description && <Text style={styles.settingDesc}>{description}</Text>}
      </View>
      <Ionicons name="chevron-forward" size={20} color="#ccc" />
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* 通知 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>通知</Text>
        <SettingSwitch
          icon="notifications"
          iconBg="#FFF5F5"
          title="推送通知"
          description="检测到哭声时发送通知"
          settingKey="notifications"
        />
        <SettingSwitch
          icon="volume-high"
          iconBg="#FFF5F5"
          title="声音提醒"
          description="播放提示音"
          settingKey="sound"
        />
        <SettingSwitch
          icon="phone-portrait"
          iconBg="#FFF5F5"
          title="振动"
          description="检测到哭声时振动"
          settingKey="vibration"
        />
      </View>

      {/* 监听 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>监听</Text>
        <SettingSwitch
          icon="moon"
          iconBg="#F3E5F5"
          title="后台监听"
          description="应用后台运行时继续监听"
          settingKey="backgroundMonitoring"
        />
      </View>

      {/* 数据 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>数据</Text>
        <SettingAction
          icon="cloud-download"
          iconBg="#E3F2FD"
          iconColor="#2196F3"
          title="导出记录"
          description="将哭声记录导出为 CSV"
          onPress={handleExport}
        />
        <SettingAction
          icon="trash"
          iconBg="#FCE4EC"
          iconColor="#E91E63"
          title="清除数据"
          description="删除所有本地记录"
          onPress={handleClearData}
          danger
        />
      </View>

      {/* 关于 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>关于</Text>
        <View style={styles.settingItem}>
          <View style={[styles.iconWrap, { backgroundColor: '#F3E5F5' }]}>
            <Ionicons name="information-circle" size={22} color="#9C27B0" />
          </View>
          <View style={styles.settingText}>
            <Text style={styles.settingTitle}>应用版本</Text>
            <Text style={styles.settingDesc}>Version {APP_VERSION}</Text>
          </View>
        </View>
        <SettingAction
          icon="star"
          iconBg="#E0F2F1"
          iconColor="#009688"
          title="给个好评"
          description="支持虾虾开发"
          onPress={() => Alert.alert('谢谢！', '您的支持是我们最大的动力 🦞')}
        />
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerMain}>🦞 虾虾开发</Text>
        <Text style={styles.footerSub}>Baby Cry Recognition App v{APP_VERSION}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  section: {
    backgroundColor: '#fff',
    marginTop: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#aaa',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    paddingHorizontal: 20,
    paddingTop: 14,
    paddingBottom: 6,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderTopWidth: 1,
    borderTopColor: '#f8f8f8',
  },
  iconWrap: {
    width: 38,
    height: 38,
    borderRadius: 19,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  settingText: { flex: 1 },
  settingTitle: { fontSize: 15, fontWeight: '500', color: '#333' },
  settingDesc: { fontSize: 12, color: '#bbb', marginTop: 2 },
  footer: { alignItems: 'center', paddingVertical: 40 },
  footerMain: { fontSize: 15, fontWeight: '600', color: '#555' },
  footerSub: { fontSize: 13, color: '#bbb', marginTop: 4 },
});
