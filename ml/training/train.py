"""
Training Script for Baby Cry Classifier
🦞 虾虾开发

Usage:
    python train.py --data_dir ../data/processed --epochs 50 --batch_size 32
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.cry_classifier import create_model, compile_model, export_to_tflite, CLASS_NAMES


def parse_args():
    parser = argparse.ArgumentParser(description='Train Baby Cry Classifier')
    parser.add_argument('--data_dir', type=str, default='../data/processed',
                        help='Path to processed data directory')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=0.001,
                        help='Learning rate')
    parser.add_argument('--output_dir', type=str, default='../export',
                        help='Directory to save trained models')
    return parser.parse_args()


def load_data(data_dir):
    """
    Load and preprocess training data.
    TODO: Implement data loading from processed directory.
    """
    print(f"📂 Loading data from {data_dir}")
    
    # Placeholder - implement actual data loading
    # Expected format:
    # - X_train: numpy array of mel spectrograms
    # - y_train: one-hot encoded labels
    # - X_val, y_val: validation data
    
    raise NotImplementedError("Data loading not yet implemented")
    
    return X_train, y_train, X_val, y_val


def train():
    """Main training function."""
    args = parse_args()
    
    print("🦞 Starting Baby Cry Classifier Training")
    print("=" * 50)
    print(f"📊 Data directory: {args.data_dir}")
    print(f"📈 Epochs: {args.epochs}")
    print(f"📦 Batch size: {args.batch_size}")
    print(f"🎯 Learning rate: {args.learning_rate}")
    print("=" * 50)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load data
    try:
        X_train, y_train, X_val, y_val = load_data(args.data_dir)
    except NotImplementedError:
        print("\n⚠️  Skipping training - dataset not yet available")
        print("📝 Next steps:")
        print("   1. Download dataset (see docs/DATASET.md)")
        print("   2. Preprocess audio files")
        print("   3. Run this script again")
        return
    
    # Create model
    print("\n🏗️  Creating model...")
    model = create_model()
    model = compile_model(model, learning_rate=args.learning_rate)
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6
        ),
        keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(args.output_dir, 'best_model.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        )
    ]
    
    # Train
    print("\n🚀 Starting training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks
    )
    
    # Evaluate
    print("\n📊 Evaluating model...")
    test_loss, test_acc, test_prec, test_rec = model.evaluate(X_val, y_val)
    print(f"✅ Test Accuracy: {test_acc:.4f}")
    print(f"✅ Test Precision: {test_prec:.4f}")
    print(f"✅ Test Recall: {test_rec:.4f}")
    
    # Export to TFLite
    print("\n📱 Exporting to TensorFlow Lite...")
    export_to_tflite(model, os.path.join(args.output_dir, 'cry_classifier.tflite'))
    
    # Save training history
    import pickle
    with open(os.path.join(args.output_dir, 'training_history.pkl'), 'wb') as f:
        pickle.dump(history.history, f)
    
    print("\n🎉 Training completed!")
    print(f"📁 Models saved to: {args.output_dir}")


if __name__ == '__main__':
    train()
