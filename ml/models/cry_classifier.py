"""
Baby Cry Classifier Model
🦞 虾虾开发

Model Architecture: Lightweight CNN for audio classification
Input: Mel Spectrogram (128 x 128)
Output: 4 classes (hungry, sleepy, uncomfortable, normal)
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Model Configuration
INPUT_SHAPE = (128, 128, 1)  # Mel spectrogram dimensions
NUM_CLASSES = 4
CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal']


def create_model():
    """
    Create a lightweight CNN model for baby cry classification.
    Optimized for mobile deployment (TensorFlow Lite).
    """
    inputs = keras.Input(shape=INPUT_SHAPE)
    
    # Block 1
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 2
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 3
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Global Average Pooling
    x = layers.GlobalAveragePooling2D()(x)
    
    # Dense layers
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    
    # Output layer
    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = keras.Model(inputs, outputs)
    
    return model


def compile_model(model, learning_rate=0.001):
    """Compile the model with optimizer and metrics."""
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    return model


def export_to_tflite(model, output_path='export/cry_classifier.tflite'):
    """Convert model to TensorFlow Lite format for mobile deployment."""
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"✅ Model exported to {output_path}")
    return tflite_model


if __name__ == '__main__':
    # Create and test model
    model = create_model()
    model = compile_model(model)
    
    model.summary()
    print(f"\n🦞 Model created successfully!")
    print(f"Input shape: {INPUT_SHAPE}")
    print(f"Output classes: {CLASS_NAMES}")
