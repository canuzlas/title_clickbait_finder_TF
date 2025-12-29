import os
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
from deep_translator import GoogleTranslator

# Paths
BASE_DIR = "model_training"
MODEL_PATH = os.path.join(BASE_DIR, "saved_model.h5")
TOKENIZER_PATH = os.path.join(BASE_DIR, "tokenizer.pickle")
CONFIG_PATH = os.path.join(BASE_DIR, "model_config.pickle")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\sğüşıöçĞÜŞİÖÇ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    print("Loading artifacts...")
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(TOKENIZER_PATH, 'rb') as f:
        tokenizer = pickle.load(f)
    with open(CONFIG_PATH, 'rb') as f:
        config = pickle.load(f)
        
    MAX_LENGTH = config['max_length']
    
    test_cases = [
        ("You Won't Believe What Happened Next!", "Clickbait (English)"),
        ("Government Announces New Tax Policy", "Normal (English)"),
        ("Bu Videoyu İzledikten Sonra Hayatınız Değişecek!", "Clickbait (Turkish)"),
        ("Merkez Bankası Faiz Kararını Açıkladı", "Normal (Turkish)"),
        ("Dolar kuru bugün ne kadar oldu?", "Neutral Question (TR)"),
        ("İstanbul'da yarın okullar tatil mi?", "Neutral Question (TR)"),
        ("Fenerbahçe Galatasaray maçı kaç kaç bitti?", "Sports Result (TR)"),
        ("Hazine ve Maliye Bakanlığı açıklama yaptı", "Gov News (TR)"),
        ("Ankara'da trafik kazası: 3 yaralı", "Local News (TR)"),
        ("dsfjjdsf dsfjdslfj dsfjldsfj", "Pure OOV Nonsense"),
        ("Bu bir deneme yazısıdır Türkçe karakterler içerir", "Raw Turkish (OOV Simulation)")
    ]
    
    print("\n--- Testing Model Predictions ---")
    print(f"{'Input':<50} | {'Type':<20} | {'Trans':<5} | {'Score':<10} | {'Pred'}")
    print("-" * 110)
    
    for text, label in test_cases:
        # Determine if translation is needed (simple heuristic: contains non-ascii or logic)
        # We'll just always translate Turkish ones for this test
        processed_text = text
        translated = "No"
        
        if "(Turkish)" in label or "(TR)" in label:
            try:
                processed_text = GoogleTranslator(source='auto', target='en').translate(text)
                translated = "Yes"
            except Exception as e:
                print(f"Translation error: {e}")
        elif "OOV" in label:
            translated = "Skip"
            processed_text = text
        
        cleaned = clean_text(processed_text)
        seq = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding='post', truncating='post')
        
        score = float(model.predict(padded, verbose=0)[0][0])
        pred_label = "CLICKBAIT" if score > 0.5 else "NORMAL"
        
        print(f"{text[:50]:<50} | {label:<20} | {translated:<5} | {score:.4f}     | {pred_label}")

if __name__ == "__main__":
    main()
