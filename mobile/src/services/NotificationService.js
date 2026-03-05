/**
 * Notification Service - 通知服务
 * 🦞 虾虾开发
 */

import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

class NotificationServiceClass {
  constructor() {
    this.initialized = false;
  }

  /**
   * 初始化通知服务
   */
  async initialize() {
    if (this.initialized) {
      return;
    }

    try {
      // 设置通知处理程序
      Notifications.setNotificationHandler({
        handleNotification: async () => ({
          shouldShowAlert: true,
          shouldPlaySound: true,
          shouldSetBadge: false,
        }),
      });

      // 请求权限
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.warn('Notification permission not granted');
        return false;
      }

      this.initialized = true;
      console.log('✅ Notification service initialized');
      return true;
    } catch (error) {
      console.error('Failed to initialize notifications:', error);
      return false;
    }
  }

  /**
   * 发送哭声检测通知
   */
  async sendCryAlert(cryType, confidence) {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      const cryTypeText = this.getCryTypeText(cryType);
      const cryTypeEmoji = this.getCryTypeEmoji(cryType);

      await Notifications.scheduleNotificationAsync({
        content: {
          title: `👶 ${cryTypeEmoji} ${cryTypeText}`,
          body: `检测到宝宝哭声 (${(confidence * 100).toFixed(0)}% 置信度)`,
          sound: true,
          priority: Notifications.AndroidNotificationPriority.HIGH,
          categoryIdentifier: 'cry-alert',
        },
        trigger: null, // 立即发送
      });

      console.log('✅ Cry alert sent:', cryType);
    } catch (error) {
      console.error('Failed to send cry alert:', error);
    }
  }

  /**
   * 发送日常统计通知
   */
  async sendDailySummary(stats) {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      await Notifications.scheduleNotificationAsync({
        content: {
          title: '📊 今日哭声统计',
          body: `今天检测到 ${stats.totalCries} 次哭声，最常见类型：${stats.mostCommonType}`,
          sound: false,
        },
        trigger: null,
      });
    } catch (error) {
      console.error('Failed to send daily summary:', error);
    }
  }

  /**
   * 设置定时通知（如晨间简报）
   */
  async scheduleDailyReminder(hour = 8, minute = 0) {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      // 取消之前的定时通知
      await Notifications.cancelAllScheduledNotificationsAsync();

      // 设置新的定时通知
      await Notifications.scheduleNotificationAsync({
        content: {
          title: '🦞 虾虾的晨间简报',
          body: '点击查看今日统计和提醒',
          sound: true,
        },
        trigger: {
          hour,
          minute,
          repeats: true,
        },
      });

      console.log(`✅ Daily reminder scheduled for ${hour}:${minute}`);
    } catch (error) {
      console.error('Failed to schedule daily reminder:', error);
    }
  }

  /**
   * 获取哭声类型文本
   */
  getCryTypeText(type) {
    const texts = {
      hungry: '饿了',
      sleepy: '困了',
      uncomfortable: '不舒服',
      normal: '正常',
    };
    return texts[type] || '未知';
  }

  /**
   * 获取哭声类型表情
   */
  getCryTypeEmoji(type) {
    const emojis = {
      hungry: '🍼',
      sleepy: '😴',
      uncomfortable: '😢',
      normal: '😊',
    };
    return emojis[type] || '❓';
  }

  /**
   * 取消所有通知
   */
  async cancelAll() {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      console.log('✅ All notifications cancelled');
    } catch (error) {
      console.error('Failed to cancel notifications:', error);
    }
  }
}

// 单例模式
export const NotificationService = new NotificationServiceClass();
export default NotificationService;
