/**
 * Audio Service - 音频采集和处理
 * 🦞 虾虾开发
 * 
 * TODO: 实现音频录制和哭声检测功能
 */

import { Audio } from 'expo-av';

class AudioServiceClass {
  constructor() {
    this.recording = null;
    this.isListening = false;
    this.onCryDetected = null;
  }

  /**
   * 请求录音权限
   */
  async requestPermission() {
    try {
      const { granted } = await Audio.requestPermissionsAsync();
      return granted;
    } catch (error) {
      console.error('Failed to request audio permission:', error);
      return false;
    }
  }

  /**
   * 开始监听
   */
  async startListening(callback) {
    if (this.isListening) {
      console.warn('Already listening');
      return;
    }

    const hasPermission = await this.requestPermission();
    if (!hasPermission) {
      throw new Error('Audio permission denied');
    }

    this.onCryDetected = callback;
    this.isListening = true;

    try {
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      this.recording = recording;
      console.log('✅ Started listening');

      // TODO: 实现实时音频分析和哭声检测
      // 目前仅作为框架，后续需要：
      // 1. 实时获取音频数据
      // 2. 提取特征 (MFCC/Mel 频谱)
      // 3. 运行 TFLite 模型推理
      // 4. 检测到哭声时回调 onCryDetected

    } catch (error) {
      console.error('Failed to start listening:', error);
      this.isListening = false;
      throw error;
    }
  }

  /**
   * 停止监听
   */
  async stopListening() {
    if (!this.isListening || !this.recording) {
      return;
    }

    try {
      await this.recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
      });

      this.recording = null;
      this.isListening = false;
      console.log('✅ Stopped listening');
    } catch (error) {
      console.error('Failed to stop listening:', error);
      throw error;
    }
  }

  /**
   * 获取监听状态
   */
  getListeningStatus() {
    return this.isListening;
  }

  /**
   * 测试音频录制（开发用）
   */
  async testRecording() {
    console.log('🎤 Testing audio recording...');
    const hasPermission = await this.requestPermission();
    console.log('Permission:', hasPermission);
    return hasPermission;
  }
}

// 单例模式
export const AudioService = new AudioServiceClass();
export default AudioService;
