/**
 * AudioService - 音频采集与分析
 * 🦞 虾虾开发
 *
 * 录制 5 秒片段 → 返回 URI → CryRecognitionService 提取特征并推理
 * 循环运行，每次录制完成自动开始下一次
 */

import { Audio } from 'expo-av';

const SEGMENT_DURATION_MS = 5000;
const RECORDING_OPTIONS = {
  ...Audio.RecordingOptionsPresets.HIGH_QUALITY,
  android: {
    ...Audio.RecordingOptionsPresets.HIGH_QUALITY.android,
    extension: '.wav',
    sampleRate: 16000,
    numberOfChannels: 1,
  },
  ios: {
    ...Audio.RecordingOptionsPresets.HIGH_QUALITY.ios,
    extension: '.wav',
    sampleRate: 16000,
    numberOfChannels: 1,
  },
};

class AudioServiceClass {
  constructor() {
    this.isListening = false;
    this.currentRecording = null;
    this.onSegmentReady = null; // callback(uri: string)
    this.loopTimer = null;
  }

  async requestPermission() {
    try {
      const { granted } = await Audio.requestPermissionsAsync();
      return granted;
    } catch {
      return false;
    }
  }

  /**
   * 开始循环录音
   * @param {(uri: string) => void} onSegmentReady - 每段录音完成后的回调
   */
  async startListening(onSegmentReady) {
    if (this.isListening) return;

    const granted = await this.requestPermission();
    if (!granted) throw new Error('麦克风权限被拒绝');

    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      playsInSilentModeIOS: true,
    });

    this.isListening = true;
    this.onSegmentReady = onSegmentReady;
    this._recordLoop();
  }

  async _recordLoop() {
    if (!this.isListening) return;

    try {
      const { recording } = await Audio.Recording.createAsync(RECORDING_OPTIONS);
      this.currentRecording = recording;

      // 录制固定时长后停止
      this.loopTimer = setTimeout(async () => {
        if (!this.isListening || !this.currentRecording) return;
        try {
          await this.currentRecording.stopAndUnloadAsync();
          const uri = this.currentRecording.getURI();
          this.currentRecording = null;

          if (uri && this.onSegmentReady) {
            this.onSegmentReady(uri);
          }
        } catch (err) {
          console.warn('AudioService: stop segment failed', err.message);
        }
        // 继续下一轮
        this._recordLoop();
      }, SEGMENT_DURATION_MS);

    } catch (err) {
      console.error('AudioService: recording failed', err.message);
      this.isListening = false;
    }
  }

  async stopListening() {
    this.isListening = false;
    if (this.loopTimer) {
      clearTimeout(this.loopTimer);
      this.loopTimer = null;
    }
    if (this.currentRecording) {
      try {
        await this.currentRecording.stopAndUnloadAsync();
      } catch {
        // ignore cleanup errors
      }
      this.currentRecording = null;
    }
    await Audio.setAudioModeAsync({ allowsRecordingIOS: false });
  }

  getStatus() {
    return { isListening: this.isListening };
  }
}

export const AudioService = new AudioServiceClass();
export default AudioService;
