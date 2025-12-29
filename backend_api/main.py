"""
🔌 Clickbait Avcısı - FastAPI Backend
=====================================
Chrome Extension için REST API servisi.

Çalıştırmak için: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import tensorflow as tf
import pickle
import re
import os
from pathlib import Path
from typing import Optional
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI(
    title="🎯 Clickbait Avcısı API",
    description="Haber başlıklarının clickbait olup olmadığını tespit eden API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS ayarları - Chrome Extension'ın erişebilmesi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver (geliştirme için)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model yolları
# Model yolları
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model_training"
MODEL_PATH = MODEL_DIR / "saved_model.h5"
TOKENIZER_PATH = MODEL_DIR / "tokenizer.pickle"
CONFIG_PATH = MODEL_DIR / "model_config.pickle"

# Global değişkenler
model = None
tokenizer = None
config = None


# Request/Response modelleri
class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="Analiz edilecek başlık")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Bu Videoyu İzledikten Sonra Hayatınız Değişecek!"
            }
        }


class PredictResponse(BaseModel):
    is_clickbait: bool = Field(..., description="Clickbait mi?")
    score: float = Field(..., description="Clickbait skoru (0-1)")
    confidence: float = Field(..., description="Güven yüzdesi")
    label: str = Field(..., description="Etiket")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_clickbait": True,
                "score": 0.92,
                "confidence": 92.0,
                "label": "CLICKBAIT"
            }
        }


class BatchPredictRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=50, description="Analiz edilecek başlıklar listesi")


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str


def load_model_and_tokenizer():
    """Model ve tokenizer'ı yükle"""
    global model, tokenizer, config
    
    try:
        if not MODEL_PATH.exists():
            logger.warning(f"Model dosyası bulunamadı: {MODEL_PATH}")
            return False
        
        logger.info("Model yükleniyor...")
        model = tf.keras.models.load_model(str(MODEL_PATH))
        
        with open(TOKENIZER_PATH, 'rb') as f:
            tokenizer = pickle.load(f)
        
        with open(CONFIG_PATH, 'rb') as f:
            config = pickle.load(f)
        
        logger.info("✅ Model başarıyla yüklendi!")
        return True
    
    except Exception as e:
        logger.error(f"❌ Model yüklenirken hata: {e}")
        return False


def clean_text(text: str) -> str:
    """Metni temizle ve normalize et"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\sğüşıöçĞÜŞİÖÇ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def predict_clickbait(text: str) -> dict:
    """Clickbait tahmini yap"""
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    
    from deep_translator import GoogleTranslator

    # 1. Translate
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        translated_text = text

    # 2. Predict
    cleaned = clean_text(translated_text)
    sequence = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(sequence, maxlen=config['max_length'], padding='post', truncating='post')
    
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
        if re.search(pattern, translated_text):
            is_safe = True
            break
            
    if is_safe and score > 0.5:
        logger.info(f"Heuristic applied: Safe pattern detected for '{translated_text}'")
        score = min(score, 0.3) # Force to Normal

    is_clickbait = score > 0.5
    
    return {
        'is_clickbait': is_clickbait,
        'score': round(score, 4),
        'confidence': round(score * 100 if is_clickbait else (1 - score) * 100, 2),
        'label': 'CLICKBAIT' if is_clickbait else 'NORMAL',
        'original_text': text,
        'translated_text': translated_text
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Uygulama başlatıldığında modeli yükle"""
    load_model_and_tokenizer()


# Endpoints
@app.get("/", tags=["Root"])
async def root():
    """API ana sayfası"""
    return {
        "message": "🎯 Clickbait Avcısı API'ye Hoş Geldiniz!",
        "docs": "/docs",
        "health": "/health",
        "predict": "/predict"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """API sağlık kontrolü"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "version": "1.0.0"
    }


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict(request: PredictRequest):
    """
    Tek bir başlık için clickbait tahmini yap.
    
    - **text**: Analiz edilecek haber başlığı
    """
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model henüz yüklenmedi. Lütfen önce modeli eğitin."
        )
    
    try:
        result = predict_clickbait(request.text)
        return result
    except Exception as e:
        logger.error(f"Tahmin hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(request: BatchPredictRequest):
    """
    Birden fazla başlık için toplu clickbait tahmini yap.
    
    - **texts**: Analiz edilecek haber başlıkları listesi (max 50)
    """
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model henüz yüklenmedi. Lütfen önce modeli eğitin."
        )
    
    try:
        results = []
        for text in request.texts:
            result = predict_clickbait(text)
            result['text'] = text
            results.append(result)
        
        # İstatistikler
        clickbait_count = sum(1 for r in results if r['is_clickbait'])
        
        return {
            "results": results,
            "summary": {
                "total": len(results),
                "clickbait_count": clickbait_count,
                "normal_count": len(results) - clickbait_count,
                "clickbait_ratio": round(clickbait_count / len(results) * 100, 2)
            }
        }
    except Exception as e:
        logger.error(f"Toplu tahmin hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info", tags=["Model"])
async def model_info():
    """Model hakkında bilgi al"""
    if config is None:
        raise HTTPException(status_code=503, detail="Model henüz yüklenmedi.")
    
    return {
        "vocab_size": config['vocab_size'],
        "max_length": config['max_length'],
        "embedding_dim": config['embedding_dim'],
        "model_loaded": model is not None
    }


# Çalıştırma
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
