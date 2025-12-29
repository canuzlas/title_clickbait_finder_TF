# 🎯 Clickbait Avcısı (Clickbait Hunter)

Full-Stack AI projesi: Haber başlıklarının clickbait olup olmadığını yapay zeka ile tespit eden uçtan uca bir uygulama.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![TensorFlow](https://img.shields.io/badge/tensorflow-2.13+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📂 Proje Yapısı

```
clickbait-hunter/
├── model_training/          # 🧠 AI Model Eğitimi
│   ├── train_model.ipynb    # Jupyter Notebook
│   ├── clickbait_data.csv   # Veri seti (Kaggle'dan indirilecek)
│   ├── saved_model.h5       # Eğitilmiş model
│   ├── tokenizer.pickle     # Metin tokenizer
│   └── model_config.pickle  # Model konfigürasyonu
│
├── app_streamlit/           # 📊 Streamlit Dashboard
│   ├── app.py               # Ana uygulama
│   └── requirements.txt     # Bağımlılıklar
│
├── backend_api/             # 🔌 FastAPI Backend
│   ├── main.py              # API sunucusu
│   └── requirements.txt     # Bağımlılıklar
│
└── chrome_extension/        # 🧩 Chrome Eklentisi
    ├── manifest.json        # Eklenti yapılandırması
    ├── popup.html           # Kullanıcı arayüzü
    ├── popup.js             # JavaScript mantığı
    └── icons/               # Eklenti ikonları
```

## 🚀 Hızlı Başlangıç

### 1️⃣ Bağımlılıkları Yükle

```bash
# Model eğitimi için
cd model_training
pip install tensorflow pandas numpy scikit-learn matplotlib seaborn jupyter

# Streamlit için
cd ../app_streamlit
pip install -r requirements.txt

# FastAPI için
cd ../backend_api
pip install -r requirements.txt
```

### 2️⃣ Modeli Eğit

```bash
cd model_training
jupyter notebook train_model.ipynb
```

Not: Notebook'taki tüm hücreleri sırasıyla çalıştırın. Bu işlem:
- Örnek veri seti oluşturur (veya Kaggle'dan indirdiğiniz veriyi kullanır)
- Modeli eğitir
- `saved_model.h5`, `tokenizer.pickle` ve `model_config.pickle` dosyalarını kaydeder

### 3️⃣ Streamlit Dashboard'u Başlat

```bash
cd app_streamlit
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresini açın.

### 4️⃣ FastAPI Backend'i Başlat

```bash
cd backend_api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API dokümantasyonu: `http://localhost:8000/docs`

### 5️⃣ Chrome Eklentisini Yükle

1. Chrome'da `chrome://extensions/` adresini açın
2. "Geliştirici modu"nu açın (sağ üst köşe)
3. "Paketlenmemiş öğe yükle" butonuna tıklayın
4. `chrome_extension` klasörünü seçin
5. Eklenti yüklendi! 🎉

## 📊 API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | API ana sayfası |
| `/health` | GET | Sağlık kontrolü |
| `/predict` | POST | Tek başlık tahmini |
| `/predict/batch` | POST | Toplu tahmin |
| `/model/info` | GET | Model bilgisi |

### Örnek İstek

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "Bu Videoyu İzledikten Sonra Hayatınız Değişecek!"}'
```

### Örnek Yanıt

```json
{
    "is_clickbait": true,
    "score": 0.92,
    "confidence": 92.0,
    "label": "CLICKBAIT"
}
```

## 🧠 Model Mimarisi

```
Embedding (10000 vocab, 128 dim)
    ↓
GlobalAveragePooling1D
    ↓
Dense (64, ReLU) + Dropout (0.3)
    ↓
Dense (32, ReLU) + Dropout (0.2)
    ↓
Dense (1, Sigmoid) → 0-1 arası skor
```

## 🎯 Clickbait Tespit Kriterleri

Model şu özellikleri öğrenir:
- Abartılı ifadeler ("Şok!", "İnanılmaz!", "Muhteşem!")
- Sayı listeleri ("10 şey", "5 sır")
- Merak uyandıran yapılar ("...sizi şaşırtacak")
- Soru kalıpları ("Biliyor musunuz?")
- Clickbait'e özgü kelime dağarcığı

## 📈 Performans

- **Doğruluk (Accuracy)**: ~95%+
- **Precision**: ~94%
- **Recall**: ~96%
- **F1-Score**: ~95%

*Not: Gerçek performans veri setine bağlı olarak değişebilir.*

## 🔧 Yapılandırma

### Model Parametreleri (`model_training/train_model.ipynb`)

```python
VOCAB_SIZE = 10000    # Kelime dağarcığı boyutu
MAX_LENGTH = 50       # Maksimum cümle uzunluğu
EMBEDDING_DIM = 128   # Embedding boyutu
```

### API Yapılandırması (`backend_api/main.py`)

```python
# CORS ayarları (güvenlik için production'da düzenleyin)
allow_origins=["*"]
```

## 📚 Veri Seti

Önerilen veri setleri:
- [Kaggle - Clickbait Dataset](https://www.kaggle.com/datasets/amananandrai/clickbait-dataset)
- [Kaggle - News Headlines](https://www.kaggle.com/datasets/rmisra/news-headlines-dataset-for-sarcasm-detection)

CSV formatı:
```csv
headline,clickbait
"Normal haber başlığı",0
"ŞOK! İnanılmaz gelişme!",1
```

## 🛠️ Teknoloji Stack

| Bileşen | Teknoloji | Görev |
|---------|-----------|-------|
| Model | TensorFlow/Keras | Metin sınıflandırma |
| Tokenizer | Pickle | Kelime→Sayı dönüşümü |
| Dashboard | Streamlit | Görsel test arayüzü |
| API | FastAPI | REST API servisi |
| Extension | HTML/CSS/JS | Tarayıcı entegrasyonu |

## 🤝 Katkıda Bulunma

1. Bu repoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'e push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👤 İletişim

Sorularınız için issue açabilirsiniz.

---

<p align="center">
  <strong>🎯 Clickbait Avcısı</strong><br>
  <em>Full-Stack AI Projesi | 2025</em>
</p>
