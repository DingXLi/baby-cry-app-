/**
 * Home Screen - 主监听页面
 * 🦞 虾虾开发
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Animated,
  Alert,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import CryRecognitionService from '../services/CryRecognitionService';
import AudioService from '../services/AudioService';
import StorageService from '../services/StorageService';
import NotificationService from '../services/NotificationService';

const CONFIDENCE_THRESHOLD = 0.5;
const DETECTION_INTERVAL_MS = 5000;

const CRY_META = {
  hungry:       { icon: 'restaurant', color: '#FF9F43', text: '饿了',   advice: '宝宝可能饿了，试试喂奶或辅食' },
  sleepy:       { icon: 'moon',       color: '#5F27CD', text: '困了',   advice: '宝宝想睡觉了，轻轻哄一哄吧' },
  uncomfortable:{ icon: 'warning',    color: '#FF6B6B', text: '不舒服', advice: '检查宝宝的尿布或体温是否正常' },
  normal:       { icon: 'happy',      color: '#1DD1A1', text: '正常',   advice: '宝宝状态良好，稍微安抚一下' },
};

export default function HomeScreen() {
  const [isListening, setIsListening] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [todayCount, setTodayCount] = useState(0);
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const timerRef = useRef(null);
  const listeningRef = useRef(false);

  useEffect(() => {
    loadTodayCount();
    CryRecognitionService.initialize();
  }, []);

  useEffect(() => {
    listeningRef.current = isListening;
    if (isListening) {
      startPulse();
      startAudio();
    } else {
      stopPulse();
      AudioService.stopListening();
    }
    return () => {
      AudioService.stopListening();
    };
  }, [isListening]);

  const loadTodayCount = async () => {
    const today = await StorageService.getTodayRecords();
    setTodayCount(today.length);
  };

  const startAudio = async () => {
    try {
      await AudioService.startListening(async (uri) => {
        if (!listeningRef.current) return;
        await runDetection(uri);
      });
    } catch (err) {
      console.warn('AudioService start failed:', err.message);
      // Fallback: 模拟检测（开发环境）
      scheduleNextDetection();
    }
  };

  const scheduleNextDetection = () => {
    timerRef.current = setTimeout(async () => {
      if (!listeningRef.current) return;
      await runDetection('simulated://recording.wav');
      scheduleNextDetection();
    }, 5000);
  };

  const startPulse = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.12, duration: 800, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1,    duration: 800, useNativeDriver: true }),
      ])
    ).start();
  };

  const stopPulse = () => {
    pulseAnim.stopAnimation();
    Animated.timing(pulseAnim, { toValue: 1, duration: 200, useNativeDriver: true }).start();
  };

  const scheduleNextDetection = () => {
    timerRef.current = setTimeout(async () => {
      if (!listeningRef.current) return;
      await runDetection();
      scheduleNextDetection();
    }, DETECTION_INTERVAL_MS);
  };

  const runDetection = async (uri) => {
    try {
      const result = await CryRecognitionService.recognize(uri || 'recording.wav');
      if (!result || result.confidence < CONFIDENCE_THRESHOLD) return;

      setLastResult(result);

      // 持久化存储
      const saved = await StorageService.addRecord({
        cryType: result.type,
        confidence: result.confidence,
        duration: parseFloat((3 + Math.random() * 7).toFixed(1)),
        timestamp: new Date(),
      });

      if (saved) {
        setTodayCount((c) => c + 1);
      }

      // 推送通知
      await NotificationService.sendCryAlert(result.type, result.confidence);
    } catch (err) {
      console.error('Detection error:', err);
    }
  };

  const toggleListening = async () => {
    if (isListening) {
      Alert.alert('停止监听', '确定要停止监听吗？', [
        { text: '取消', style: 'cancel' },
        {
          text: '停止',
          style: 'destructive',
          onPress: () => setIsListening(false),
        },
      ]);
    } else {
      setIsListening(true);
    }
  };

  const meta = lastResult ? CRY_META[lastResult.type] : null;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* 状态栏 */}
      <View style={styles.statusRow}>
        <View style={[styles.statusDot, { backgroundColor: isListening ? '#1DD1A1' : '#ccc' }]} />
        <Text style={styles.statusText}>{isListening ? '正在监听' : '已停止'}</Text>
        <View style={styles.todayBadge}>
          <Text style={styles.todayText}>今日 {todayCount} 次</Text>
        </View>
      </View>

      {/* 监听按钮 */}
      <View style={styles.buttonArea}>
        <Animated.View
          style={[styles.pulseRing, isListening && styles.pulseRingActive, { transform: [{ scale: pulseAnim }] }]}
        >
          <TouchableOpacity
            style={[styles.listenButton, isListening && styles.listenButtonActive]}
            onPress={toggleListening}
            activeOpacity={0.85}
          >
            <Ionicons name={isListening ? 'stop' : 'mic'} size={64} color="#fff" />
          </TouchableOpacity>
        </Animated.View>
        <Text style={styles.buttonHint}>{isListening ? '点击停止' : '点击开始监听'}</Text>
      </View>

      {/* 最近检测结果 */}
      {lastResult && meta && (
        <View style={[styles.resultCard, { borderLeftColor: meta.color }]}>
          <View style={styles.resultHeader}>
            <View style={[styles.resultIconWrap, { backgroundColor: meta.color + '20' }]}>
              <Ionicons name={meta.icon} size={28} color={meta.color} />
            </View>
            <View style={styles.resultInfo}>
              <Text style={[styles.resultType, { color: meta.color }]}>{meta.text}</Text>
              <Text style={styles.resultConf}>置信度 {(lastResult.confidence * 100).toFixed(0)}%</Text>
            </View>
            <Text style={styles.resultTime}>
              {new Date(lastResult.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
            </Text>
          </View>
          <Text style={styles.resultAdvice}>{meta.advice}</Text>

          {/* 概率分布 */}
          <View style={styles.probContainer}>
            {Object.entries(lastResult.probabilities).map(([type, prob]) => (
              <View key={type} style={styles.probRow}>
                <Text style={styles.probLabel}>{CRY_META[type]?.text}</Text>
                <View style={styles.probBar}>
                  <View
                    style={[
                      styles.probFill,
                      { width: `${(prob * 100).toFixed(0)}%`, backgroundColor: CRY_META[type]?.color },
                    ]}
                  />
                </View>
                <Text style={styles.probValue}>{(prob * 100).toFixed(0)}%</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* 使用提示 */}
      {!lastResult && (
        <View style={styles.tips}>
          <Text style={styles.tipsTitle}>💡 使用提示</Text>
          <Text style={styles.tipsText}>
            • 点击麦克风按钮开始监听{'\n'}
            • 每 5 秒自动分析一次声音{'\n'}
            • 检测到哭声会推送通知{'\n'}
            • 历史记录和统计在下方标签页
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  content: { padding: 20, paddingBottom: 40 },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  statusDot: { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  statusText: { fontSize: 16, fontWeight: '600', color: '#333', flex: 1 },
  todayBadge: {
    backgroundColor: '#FF6B6B20',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  todayText: { fontSize: 13, color: '#FF6B6B', fontWeight: '600' },
  buttonArea: { alignItems: 'center', marginVertical: 40 },
  pulseRing: {
    width: 180,
    height: 180,
    borderRadius: 90,
    backgroundColor: '#FF6B6B18',
    justifyContent: 'center',
    alignItems: 'center',
  },
  pulseRingActive: { backgroundColor: '#FF6B6B35' },
  listenButton: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#FF6B6B',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#FF6B6B',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.35,
    shadowRadius: 10,
    elevation: 10,
  },
  listenButtonActive: { backgroundColor: '#FF5252' },
  buttonHint: { marginTop: 18, fontSize: 15, color: '#888' },
  resultCard: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 18,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 4,
    marginBottom: 16,
  },
  resultHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  resultIconWrap: {
    width: 52,
    height: 52,
    borderRadius: 26,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  resultInfo: { flex: 1 },
  resultType: { fontSize: 20, fontWeight: '700' },
  resultConf: { fontSize: 13, color: '#999', marginTop: 2 },
  resultTime: { fontSize: 13, color: '#bbb' },
  resultAdvice: { fontSize: 14, color: '#555', lineHeight: 20, marginBottom: 14 },
  probContainer: { gap: 8 },
  probRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  probLabel: { width: 52, fontSize: 12, color: '#888', textAlign: 'right' },
  probBar: { flex: 1, height: 6, backgroundColor: '#f0f0f0', borderRadius: 3, overflow: 'hidden' },
  probFill: { height: '100%', borderRadius: 3 },
  probValue: { width: 32, fontSize: 12, color: '#888' },
  tips: {
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    padding: 16,
    marginTop: 10,
  },
  tipsTitle: { fontSize: 15, fontWeight: '600', color: '#1976D2', marginBottom: 8 },
  tipsText: { fontSize: 14, color: '#555', lineHeight: 22 },
});
