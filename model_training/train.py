import os
import re
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense, Dropout, LSTM
from sklearn.model_selection import train_test_split

# --- Configuration ---
# Use paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "clickbait_data.csv")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "saved_model.h5")
TOKENIZER_SAVE_PATH = os.path.join(BASE_DIR, "tokenizer.pickle")
CONFIG_SAVE_PATH = os.path.join(BASE_DIR, "model_config.pickle")

VOCAB_SIZE = 10000
MAX_LENGTH = 50
EMBEDDING_DIM = 128
OOV_TOKEN = "<OOV>"
EPOCHS = 5
BATCH_SIZE = 32

def check_gpu():
    print("TensorFlow Version:", tf.__version__)
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✅ GPU Detected: {gpus}")
        for gpu in gpus:
            print(f"   Name: {gpu.name}, Type: {gpu.device_type}")
    else:
        print("⚠️ No GPU detected. Training will run on CPU.")

def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Data file not found at: {DATA_PATH}\nPlease ensure 'clickbait_data.csv' is in the 'model_training' directory.")
    print(f"Loading data from: {DATA_PATH}")
    return pd.read_csv(DATA_PATH)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\sğüşıöçĞÜŞİÖÇ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_model():
    model = Sequential([
        Embedding(VOCAB_SIZE, EMBEDDING_DIM, input_length=MAX_LENGTH),
        GlobalAveragePooling1D(),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def main():
    check_gpu()
    
    print("Loading data...")
    try:
        df = load_data()
    except Exception as e:
        print(e)
        return

    print(f"Data loaded: {len(df)} rows")
    
    print("Preprocessing...")
    if 'headline' not in df.columns or 'clickbait' not in df.columns:
        print("❌ Error: CSV must contain 'headline' and 'clickbait' columns.")
        return

    df['cleaned_headline'] = df['headline'].apply(clean_text)
    
    tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token=OOV_TOKEN)
    tokenizer.fit_on_texts(df['cleaned_headline'])
    
    sequences = tokenizer.texts_to_sequences(df['cleaned_headline'])
    X = pad_sequences(sequences, maxlen=MAX_LENGTH, padding='post', truncating='post')
    y = df['clickbait'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Building model...")
    model = create_model()
    model.summary()
    
    print("Starting training...")
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE, validation_split=0.2)
    
    print("Evaluating...")
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {accuracy:.4f}")
    
    print("Saving artifacts...")
    # 1. Save Model (.h5)
    model.save(MODEL_SAVE_PATH)
    print(f"Model saved to: {MODEL_SAVE_PATH}")
    
    # 2. Save Tokenizer
    with open(TOKENIZER_SAVE_PATH, 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Tokenizer saved to: {TOKENIZER_SAVE_PATH}")

    # 3. Save Config (Required by Backend/Streamlit)
    config = {
        'vocab_size': VOCAB_SIZE,
        'max_length': MAX_LENGTH,
        'embedding_dim': EMBEDDING_DIM
    }
    with open(CONFIG_SAVE_PATH, 'wb') as handle:
        pickle.dump(config, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Config saved to: {CONFIG_SAVE_PATH}")
    
    print("✅ Training completed successfully!")

if __name__ == "__main__":
    main()
