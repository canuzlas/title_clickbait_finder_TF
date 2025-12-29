/**
 * Clickbait Avcısı - Chrome Extension
 * ====================================
 * Bu script, popup.html'deki formu yönetir ve
 * FastAPI backend'ine istek gönderir.
 */

// API endpoint (localhost)
const API_BASE_URL = 'http://127.0.0.1:8000';

// DOM elementleri
const headlineInput = document.getElementById('headline');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const resultDiv = document.getElementById('result');
const resultIcon = document.getElementById('resultIcon');
const resultLabel = document.getElementById('resultLabel');
const resultScore = document.getElementById('resultScore');
const progressFill = document.getElementById('progressFill');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

/**
 * API sağlık kontrolü yap
 */
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.model_loaded) {
                statusDot.classList.remove('offline');
                statusDot.classList.add('online');
                statusText.textContent = 'API Bağlı ✓';
                analyzeBtn.disabled = false;
            } else {
                statusDot.classList.remove('online');
                statusDot.classList.add('offline');
                statusText.textContent = 'Model Yüklenmedi';
                analyzeBtn.disabled = true;
            }
        } else {
            throw new Error('API yanıt vermedi');
        }
    } catch (error) {
        statusDot.classList.remove('online');
        statusDot.classList.add('offline');
        statusText.textContent = 'API Bağlantısı Yok';
        analyzeBtn.disabled = true;
        console.error('API Health Check Error:', error);
    }
}

/**
 * Clickbait tahmini yap
 */
async function analyzeHeadline(text) {
    const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ text: text })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API hatası oluştu');
    }
    
    return await response.json();
}

/**
 * Sonucu göster
 */
function showResult(result) {
    // Önceki sınıfları temizle
    resultDiv.classList.remove('clickbait', 'normal');
    
    if (result.is_clickbait) {
        resultDiv.classList.add('clickbait');
        resultIcon.textContent = '🚨';
        resultLabel.textContent = 'CLICKBAIT UYARISI!';
    } else {
        resultDiv.classList.add('normal');
        resultIcon.textContent = '✅';
        resultLabel.textContent = 'Normal Başlık';
    }
    
    resultScore.textContent = `Skor: ${(result.score * 100).toFixed(1)}% | Güven: ${result.confidence}%`;
    progressFill.style.width = `${result.score * 100}%`;
    
    resultDiv.classList.add('show');
}

/**
 * Hata göster
 */
function showError(message) {
    errorDiv.textContent = `❌ ${message}`;
    errorDiv.classList.add('show');
}

/**
 * UI'ı sıfırla
 */
function resetUI() {
    errorDiv.classList.remove('show');
    resultDiv.classList.remove('show');
    loadingDiv.classList.remove('show');
}

/**
 * Ana analiz fonksiyonu
 */
async function handleAnalyze() {
    const headline = headlineInput.value.trim();
    
    // Validasyon
    if (!headline) {
        showError('Lütfen bir başlık girin!');
        return;
    }
    
    if (headline.length < 5) {
        showError('Başlık çok kısa! En az 5 karakter girin.');
        return;
    }
    
    // UI'ı hazırla
    resetUI();
    loadingDiv.classList.add('show');
    analyzeBtn.disabled = true;
    
    try {
        const result = await analyzeHeadline(headline);
        loadingDiv.classList.remove('show');
        showResult(result);
    } catch (error) {
        loadingDiv.classList.remove('show');
        showError(error.message || 'Bir hata oluştu. API çalışıyor mu?');
        console.error('Analyze Error:', error);
    } finally {
        analyzeBtn.disabled = false;
    }
}

// Event Listeners
analyzeBtn.addEventListener('click', handleAnalyze);

// Enter tuşuna basınca da analiz yap
headlineInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleAnalyze();
    }
});

// Sayfa yüklendiğinde API'yi kontrol et
document.addEventListener('DOMContentLoaded', () => {
    checkApiHealth();
    
    // Her 10 saniyede API'yi kontrol et
    setInterval(checkApiHealth, 10000);
});

// Input değişince hataları temizle
headlineInput.addEventListener('input', () => {
    if (errorDiv.classList.contains('show')) {
        errorDiv.classList.remove('show');
    }
});
