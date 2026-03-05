/**
 * Home Screen - 主监听页面
 * 🦞 虾虾开发
 */

import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Animated,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function HomeScreen() {
  const [isListening, setIsListening] = useState(false);
  const [lastCryType, setLastCryType] = useState(null);
  const [lastCryTime, setLastCryTime] = useState(null);
  const [pulseAnim] = useState(new Animated.Value(1));

  // 脉冲动画效果
  useEffect(() => {
    if (isListening) {
      const pulse = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      );
      pulse.start();
      return () => pulse.stop();
    } else {
      pulseAnim.setValue(1);
    }
  }, [isListening]);

  const toggleListening = () => {
    if (isListening) {
      Alert.alert(
        '停止监听',
        '确定要停止监听吗？',
        [
          { text: '取消', style: 'cancel' },
          {
            text: '停止',
            style: 'destructive',
            onPress: () => {
              setIsListening(false);
            },
          },
        ]
      );
    } else {
      setIsListening(true);
      // TODO: 实现音频采集和哭声识别
    }
  };

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

  return (
    <View style={styles.container}>
      {/* 状态显示 */}
      <View style={styles.statusContainer}>
        <Text style={styles.statusText}>
          {isListening ? '🟢 正在监听' : '🔴 已停止'}
        </Text>
      </View>

      {/* 监听按钮 */}
      <View style={styles.buttonContainer}>
        <Animated.View
          style={[
            styles.pulseContainer,
            { transform: [{ scale: pulseAnim }] },
            isListening && styles.pulseActive,
          ]}
        >
          <TouchableOpacity
            style={[styles.listenButton, isListening && styles.listenButtonActive]}
            onPress={toggleListening}
            activeOpacity={0.8}
          >
            <Ionicons
              name={isListening ? 'stop' : 'mic'}
              size={60}
              color="#fff"
            />
          </TouchableOpacity>
        </Animated.View>
        <Text style={styles.buttonText}>
          {isListening ? '点击停止' : '点击开始监听'}
        </Text>
      </View>

      {/* 上次哭声记录 */}
      {lastCryType && (
        <View style={styles.lastRecordContainer}>
          <Text style={styles.lastRecordTitle}>上次哭声检测</Text>
          <View style={[styles.cryTypeBadge, { backgroundColor: getCryTypeColor(lastCryType) + '20' }]}>
            <Ionicons
              name={getCryTypeIcon(lastCryType)}
              size={24}
              color={getCryTypeColor(lastCryType)}
            />
            <Text style={[styles.cryTypeText, { color: getCryTypeColor(lastCryType) }]}>
              {getCryTypeText(lastCryType)}
            </Text>
          </View>
          <Text style={styles.cryTime}>{lastCryTime}</Text>
        </View>
      )}

      {/* 提示信息 */}
      <View style={styles.tipsContainer}>
        <Text style={styles.tipsTitle}>💡 使用提示</Text>
        <Text style={styles.tipsText}>
          • 点击麦克风按钮开始监听{'\n'}
          • 检测到哭声会自动通知{'\n'}
          • 可在设置中调整监听时间
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  statusContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  statusText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  buttonContainer: {
    alignItems: 'center',
    marginTop: 40,
  },
  pulseContainer: {
    width: 180,
    height: 180,
    borderRadius: 90,
    backgroundColor: '#FF6B6B30',
    justifyContent: 'center',
    alignItems: 'center',
  },
  pulseActive: {
    backgroundColor: '#FF6B6B50',
  },
  listenButton: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#FF6B6B',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#FF6B6B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  listenButtonActive: {
    backgroundColor: '#FF5252',
  },
  buttonText: {
    marginTop: 20,
    fontSize: 16,
    color: '#666',
  },
  lastRecordContainer: {
    marginTop: 40,
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
  lastRecordTitle: {
    fontSize: 14,
    color: '#999',
    marginBottom: 15,
  },
  cryTypeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    marginBottom: 10,
  },
  cryTypeText: {
    fontSize: 18,
    fontWeight: '600',
    marginLeft: 8,
  },
  cryTime: {
    fontSize: 14,
    color: '#999',
  },
  tipsContainer: {
    marginTop: 30,
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    padding: 15,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1976D2',
    marginBottom: 8,
  },
  tipsText: {
    fontSize: 14,
    color: '#555',
    lineHeight: 22,
  },
});
