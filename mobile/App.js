/**
 * Baby Cry App - Main Entry Point
 * 🦞 虾虾开发
 */

import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import * as SplashScreen from 'expo-splash-screen';

// Navigation
import AppNavigator from './src/navigation/AppNavigator';

// Services
import NotificationService from './src/services/NotificationService';

// Keep splash screen visible while loading
SplashScreen.preventAutoHideAsync();

export default function App() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // 初始化通知服务
      await NotificationService.initialize();

      // 设置晨间简报（早上 8 点）
      await NotificationService.scheduleDailyReminder(8, 0);

      console.log('✅ App initialized');
    } catch (error) {
      console.error('Failed to initialize app:', error);
    } finally {
      setIsReady(true);
      await SplashScreen.hideAsync();
    }
  };

  if (!isReady) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B6B" />
        <Text style={styles.loadingText}>虾虾加载中...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <AppNavigator />
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  loadingText: {
    marginTop: 20,
    fontSize: 16,
    color: '#999',
  },
});
