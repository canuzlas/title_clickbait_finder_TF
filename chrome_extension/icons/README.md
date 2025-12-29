# Chrome Extension Icons

Bu klasör Chrome eklentisi için ikon dosyalarını içerir.

## Gerekli İkonlar

Chrome eklentisi için aşağıdaki boyutlarda PNG ikonlar gereklidir:

- `icon16.png` (16x16 piksel) - Araç çubuğu
- `icon32.png` (32x32 piksel) - Windows
- `icon48.png` (48x48 piksel) - Eklenti yönetimi sayfası
- `icon128.png` (128x128 piksel) - Chrome Web Store

## İkon Oluşturma

SVG dosyasını PNG'ye dönüştürmek için:

### Online Araç
1. [CloudConvert](https://cloudconvert.com/svg-to-png) sitesini kullanın
2. SVG dosyasını yükleyin
3. Her boyut için ayrı ayrı dönüştürün

### Komut Satırı (ImageMagick gerekli)
```bash
# ImageMagick yükleyin
brew install imagemagick  # macOS

# SVG'den PNG'ye dönüştür
convert -background none -resize 16x16 icon.svg icon16.png
convert -background none -resize 32x32 icon.svg icon32.png
convert -background none -resize 48x48 icon.svg icon48.png
convert -background none -resize 128x128 icon.svg icon128.png
```

### Python ile (Pillow + cairosvg)
```python
import cairosvg

sizes = [16, 32, 48, 128]
for size in sizes:
    cairosvg.svg2png(
        url='icon16.svg',
        write_to=f'icon{size}.png',
        output_width=size,
        output_height=size
    )
```

## Tasarım Önerileri

- 🎯 Hedef tahtası teması (clickbait "avcısı" konsepti)
- Mor-mavi gradient arka plan (#667eea → #764ba2)
- Beyaz iç daire
- Basit ve tanınabilir tasarım
