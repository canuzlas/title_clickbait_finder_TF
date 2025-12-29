# 🎯 Clickbait Avcısı (Clickbait Hunter)

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![TensorFlow](https://img.shields.io/badge/tensorflow-2.13+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Clickbait Avcısı**, haber başlıklarının "tık tuzağı" (clickbait) olup olmadığını Yapay Zeka (AI) ve Doğal Dil İşleme (NLP) teknolojileriyle analiz eden kapsamlı bir Full-Stack projesidir.

Proje, modern web teknolojilerini ve gelişmiş derin öğrenme modellerini birleştirerek kullanıcıların manipülatif başlıklara karşı bilinçlenmesini sağlar.

---

## 🌟 Özellikler

-   **🧠 Gelişmiş AI Modeli**: TensorFlow ve Keras ile eğitilmiş, yüksek doğruluklu metin sınıflandırma modeli.
-   **🔌 RESTful API**: FastAPI tabanlı, hızlı ve ölçeklenebilir backend servisi.
-   **📊 İnteraktif Dashboard**: Streamlit ile geliştirilmiş, kullanıcı dostu analiz arayüzü.
-   **🌍 Çoklu Dil Desteği**: Türkçe ve İngilizce başlıkları otomatik algılayıp analiz edebilme (Deep Translator entegrasyonu).
-   **🧩 Chrome Eklentisi**: Tarayıcı üzerinde gezindiğiniz haber sitelerindeki başlıkları anlık olarak analiz etme imkanı.
-   **🍎 Apple Silicon Desteği**: Mac M1/M2/M3 işlemciler için optimize edilmiş GPU hızlandırmalı kurulum.

---

## 📂 Proje Mimarisi

```
news_title_clickbait_alarm/
├── model_training/          # 🧠 AI Model Eğitimi
│   ├── train.py             # Python Script (Eğitim Süreci)
│   ├── clickbait_data.csv   # Veri Seti
│   └── ...                  # Model çıktıları (.h5, .pickle)
│
├── backend_api/             # � Backend API
│   ├── main.py              # FastAPI Uygulaması
│   └── requirements.txt     # API Bağımlılıkları
│
├── app_streamlit/           # � Kullanıcı Arayüzü
│   ├── app.py               # Streamlit Dashboard
│   └── requirements.txt     # UI Bağımlılıkları
│
├── chrome_extension/        # 🧩 Tarayıcı Eklentisi
│   ├── manifest.json        # Eklenti Konfigürasyonu
│   ├── popup.html           # Eklenti Arayüzü
│   └── ...
│
└── debug_model.py           # 🛠️ Hızlı Test Aracı
```

---

## 🚀 Kurulum Rehberi

### Ön Gereksinimler

-   Python 3.9 veya üzeri
-   [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (Önerilen) veya `pip`

### 🍎 Mac M2 / Apple Silicon Kurulumu (Önemli!)

Mac M1/M2/M3 kullanıcıları, GPU hızlandırmasından (Metal Performance Shaders) yararlanmak için aşağıdaki adımları takip etmelidir:

```bash
# 1. Yeni bir Conda ortamı oluşturun
conda create -n clickbait_m2 python=3.9 -y
conda activate clickbait_m2

# 2. Apple TensorFlow bağımlılıklarını yükleyin
conda install -c apple tensorflow-deps -y

# 3. Temel TensorFlow ve Metal eklentisini yükleyin
pip install tensorflow-macos
pip install tensorflow-metal

# 4. Proje genel bağımlılıklarını yükleyin
pip install pandas numpy scikit-learn matplotlib seaborn jupyter deep-translator fastapi uvicorn streamlit
```

### 💻 Standart Kurulum (Windows / Linux / Intel Mac)

```bash
# Sanal ortam oluşturun (Opsiyonel ama önerilir)
python -m venv venv
source venv/bin/activate  # Windows için: venv\Scripts\activate

# Gerekli paketleri yükleyin
pip install tensorflow pandas numpy scikit-learn matplotlib seaborn jupyter deep-translator fastapi uvicorn streamlit
```

---

## 💡 Kullanım

### Adım 1: Modeli Eğitin 🧠

Sistemi kullanmaya başlamadan önce yapay zeka modelinin eğitilmesi gerekir.

1.  `model_training` klasörüne gidin.
2.  Eğitim scriptini çalıştırın:
    ```bash
    python train.py
    ```
3.  Bu işlem sonucunda `saved_model.h5`, `tokenizer.pickle` ve `model_config.pickle` dosyaları oluşturulacaktır.

*Alternatif olarak hızlı test için:*
```bash
python debug_model.py
```

### Adım 2: Backend API'yi Başlatın 🔌

API, modelin dış dünyaya açılan kapısıdır. Chrome eklentisi ve diğer servisler bu API'yi kullanır.

```bash
cd backend_api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*API şu adreste çalışacaktır:* `http://localhost:8000`
*Dokümantasyon:* `http://localhost:8000/docs`

### Adım 3: Dashboard'u Başlatın 📊

Görsel arayüz üzerinden analiz yapmak için Streamlit uygulamasını çalıştırın.

```bash
cd app_streamlit
streamlit run app.py
```
*Tarayıcınızda otomatik olarak açılacaktır (Genellikle http://localhost:8501).*

### Adım 4: Chrome Eklentisini Yükleyin 🧩

1.  Google Chrome'u açın ve adres çubuğuna `chrome://extensions/` yazın.
2.  Sağ üst köşedeki **"Geliştirici modu" (Developer mode)** anahtarını açın.
3.  Sol üstte beliren **"Paketlenmemiş öğe yükle" (Load unpacked)** butonuna tıklayın.
4.  Proje klasöründeki `chrome_extension` dizinini seçin.
5.  Artık tarayıcınızın sağ üst köşesinde Clickbait Avcısı ikonunu görebilirsiniz! 🎉

---

## 📡 API Uç Noktaları (Endpoints)

| Metot | Yol | Açıklama |
| :--- | :--- | :--- |
| `GET` | `/` | API durumunu kontrol eder. |
| `GET` | `/active_model` | Yüklü modelin parametrelerini döndürür. |
| `POST` | `/predict` | Tek bir başlığı analiz eder. |
| `POST` | `/predict/batch` | Birden fazla başlığı aynı anda analiz eder. |

**Örnek İstek (/predict):**
```json
{
  "text": "Bu Videoyu İzledikten Sonra Hayatınız Değişecek!"
}
```

---

## 🤝 Katkıda Bulunma

1.  Projeyi Fork'layın.
2.  Yeni bir Branch oluşturun (`git checkout -b feature/HarikaOzellik`).
3.  Değişikliklerinizi Commit'leyin (`git commit -m 'Harika bir özellik eklendi'`).
4.  Branch'inizi Push'layın (`git push origin feature/HarikaOzellik`).
5.  Bir Pull Request (PR) açın.

---

## 📄 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

---

<p align="center">
  <strong>2025 | Clickbait Avcısı Projesi</strong>
</p>
