"""
🎯 Clickbait Avcısı - Streamlit Dashboard
=========================================
Bu uygulama, haber başlıklarının clickbait olup olmadığını analiz eder.

Çalıştırmak için: streamlit run app.py
"""

import streamlit as st
import tensorflow as tf
import pickle
import re
import os
from pathlib import Path

# Sayfa yapılandırması
st.set_page_config(
    page_title="🎯 Clickbait Avcısı",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .result-box {
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .clickbait {
        background-color: #ffebee;
        border: 3px solid #e74c3c;
        color: #c0392b;
    }
    .normal {
        background-color: #e8f5e9;
        border: 3px solid #27ae60;
        color: #1e8449;
    }
    .score-bar {
        height: 30px;
        border-radius: 15px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Model yolları
# Model yolları
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model_training"
MODEL_PATH = MODEL_DIR / "saved_model.h5"
TOKENIZER_PATH = MODEL_DIR / "tokenizer.pickle"
CONFIG_PATH = MODEL_DIR / "model_config.pickle"


@st.cache_resource
def load_model():
    """Model ve tokenizer'ı yükle (cache'le)"""
    try:
        model = tf.keras.models.load_model(str(MODEL_PATH))
        with open(TOKENIZER_PATH, 'rb') as f:
            tokenizer = pickle.load(f)
        with open(CONFIG_PATH, 'rb') as f:
            config = pickle.load(f)
        return model, tokenizer, config
    except Exception as e:
        st.error(f"❌ Model yüklenemedi: {e}")
        st.info("💡 Önce model_training/train_model.ipynb notebook'unu çalıştırın.")
        return None, None, None


def clean_text(text):
    """Metni temizle ve normalize et"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\sğüşıöçĞÜŞİÖÇ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def predict_clickbait(text, model, tokenizer, max_length):
    """Clickbait tahmini yap"""
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    
    cleaned = clean_text(text)
    sequence = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(sequence, maxlen=max_length, padding='post', truncating='post')
    
    score = float(model.predict(padded, verbose=0)[0][0])
    
    # --- Heuristics to reduce False Positives ---
    safe_patterns = [
        r"(?i).*\b(dollar|euro|gold|currency|exchange rate)\b.*\?", # Money questions
        r"(?i).*\b(match|score|won|lost|game)\b.*\?",               # Sports questions
        r"(?i).*\b(school|holiday|vacation|class)\b.*\?",            # School questions
        r"(?i).*\b(weather|snow|rain|temperature|forecast)\b.*",     # Weather
        r"(?i).*\b(announced|statement|reported|said)\b.*",          # Official statements
    ]
    
    is_safe = False
    for pattern in safe_patterns:
        if re.search(pattern, text):
            is_safe = True
            break
            
    if is_safe and score > 0.5:
        # If it looks like a safe question but model thinks clickbait (common for Questions),
        # we act as a "Second Opinion" and lower the score.
        print(f"Heuristic applied: Safe pattern detected for '{text}'")
        score = min(score, 0.3) # Force to Normal
        
    is_clickbait = score > 0.5
    
    return {
        'is_clickbait': is_clickbait,
        'score': score,
        'confidence': score * 100 if is_clickbait else (1 - score) * 100
    }


# Ana başlık
st.markdown('<h1 class="main-header">🎯 Clickbait Avcısı</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("ℹ️ Hakkında")
    st.write("""
    Bu uygulama, yapay zeka kullanarak haber başlıklarının 
    **clickbait** olup olmadığını tespit eder.
    
    **Clickbait Nedir?**
    Okuyucuyu tıklamaya yönlendirmek için kullanılan 
    abartılı, merak uyandırıcı başlıklardır.
    """)
    
    st.header("📊 Model Bilgisi")
    model, tokenizer, config = load_model()
    if config:
        st.write(f"- **Kelime Dağarcığı:** {config['vocab_size']:,}")
        st.write(f"- **Max Uzunluk:** {config['max_length']}")
        st.write(f"- **Embedding Boyutu:** {config['embedding_dim']}")
    
    st.header("🔗 Proje")
    st.write("Full-Stack AI Projesi")
    st.write("- 🤖 TensorFlow/Keras Model")
    st.write("- 🌐 FastAPI Backend")
    st.write("- 🧩 Chrome Extension")

# Ana içerik
if model is None:
    st.warning("⚠️ Model dosyaları bulunamadı!")
    st.info("""
    ### Model Nasıl Eğitilir?
    1. `model_training/train_model.ipynb` notebook'unu açın
    2. Tüm hücreleri sırasıyla çalıştırın
    3. Bu sayfayı yenileyin
    """)
else:
    # Giriş alanı
    st.subheader("📝 Başlık Analizi")
    headline = st.text_input(
        "Haber başlığını girin:",
        placeholder="Örn: Bu Videoyu İzledikten Sonra Hayatınız Değişecek!",
        key="headline_input"
    )
    
    # Analiz butonu
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analiz Et (Translate & Analyze)", use_container_width=True, type="primary")
    
    # Sonuç gösterimi
    if analyze_button and headline:
        with st.spinner("🤖 Translating & Analyzing..."):
            # 1. Translate
            from deep_translator import GoogleTranslator
            try:
                translated_text = GoogleTranslator(source='auto', target='en').translate(headline)
            except Exception as e:
                st.error(f"Translation failed: {e}")
                translated_text = headline
            
            # Show translation
            st.info(f"**Translated Text:** {translated_text}")
            
            # 2. Predict
            result = predict_clickbait(translated_text, model, tokenizer, config['max_length'])
        
        st.markdown("---")
        st.subheader("📊 Sonuç")
        
        if result['is_clickbait']:
            st.markdown("""
            <div class="result-box clickbait">
                🚨 CLICKBAIT UYARISI!
            </div>
            """, unsafe_allow_html=True)
            st.error(f"Bu başlık %{result['confidence']:.1f} olasılıkla clickbait.")
        else:
            st.markdown("""
            <div class="result-box normal">
                ✅ Normal Başlık
            </div>
            """, unsafe_allow_html=True)
            st.success(f"Bu başlık %{result['confidence']:.1f} olasılıkla güvenilir.")
        
        # Skor çubuğu
        st.subheader("📈 Clickbait Skoru")
        st.progress(result['score'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Skor", f"{result['score']:.2%}")
        with col2:
            st.metric("Güven", f"{result['confidence']:.1f}%")
        with col3:
            st.metric("Durum", "Clickbait" if result['is_clickbait'] else "Normal")
    
    elif analyze_button:
        st.warning("⚠️ Lütfen bir başlık girin!")
    
    # Örnek başlıklar
    st.markdown("---")
    st.subheader("📚 Örnek Başlıklar")
    
    # Helper for updating input
    def update_headline(text):
        st.session_state.headline_input = text

    with col1:
        st.markdown("**🚨 Clickbait Örnekleri:**")
        clickbait_examples = [
            "Bu Videoyu İzledikten Sonra Hayatınız Değişecek!",
            "10 Şok Edici Gerçek - 7. Madde Sizi Çok Şaşırtacak!",
            "Kimse Bu Sırrı Bilmiyor!",
            "You Won't Believe What Happened Next!"
        ]
        for ex in clickbait_examples:
            st.button(ex, key=f"cb_{ex[:20]}", on_click=update_headline, args=(ex,))
    
    with col2:
        st.markdown("**✅ Normal Başlık Örnekleri:**")
        normal_examples = [
            "Merkez Bankası Faiz Kararını Açıkladı",
            "Hava Durumu: Yarın Yağmur Bekleniyor",
            "Türkiye-AB İlişkilerinde Yeni Dönem",
            "Government Announces New Policy"
        ]
        for ex in normal_examples:
            st.button(ex, key=f"n_{ex[:20]}", on_click=update_headline, args=(ex,))

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8rem;">
    🎯 Clickbait Avcısı | Full-Stack AI Projesi | 2025
</div>
""", unsafe_allow_html=True)
