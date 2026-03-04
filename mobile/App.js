/**
 * Baby Cry App - Main Entry Point
 * 🦞 虾虾开发
 */

import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>🦞 虾虾的哭声识别 App</Text>
      <Text style={styles.subtitle}>Baby Cry Recognition</Text>
      <Text style={styles.version}>Version 0.1.0</Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
  },
  version: {
    fontSize: 12,
    color: '#999',
  },
});
