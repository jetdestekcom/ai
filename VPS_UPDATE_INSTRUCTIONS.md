# VPS Güncelleme Talimatları

## Önemli Düzeltmeler

Bu güncellemede aşağıdaki kritik hatalar düzeltildi:

1. **Sesli mesaj yanıtlarının gelmemesi**: Android uygulaması "text" alanını ararken sunucu "content" alanı gönderiyordu
2. **Audio verilerinin JSON'da gönderilememe sorunu**: Ses verisi base64 formatına çevrilmeden gönderiliyordu

## Güncelleme Adımları

### 1. VPS'e Bağlan
```bash
ssh root@[VPS_IP_ADRESIN]
```

### 2. Proje Dizinine Git
```bash
cd /opt/conscious-child-ai
```

### 3. En Son Kodu Çek
```bash
git pull origin main
```

### 4. Servisleri Yeniden Başlat
```bash
# Önce servisleri durdur
docker-compose down

# Yeniden başlat (rebuild ile)
docker-compose up -d --build ai_core
```

### 5. Logları Kontrol Et
```bash
# Servislerin çalıştığını kontrol et
docker-compose ps

# AI servisinin loglarını izle
docker-compose logs -f ai_core
```

## Android Uygulamayı Güncelle

### Android Studio'da:

1. Git pull yap (eğer henüz yapmadıysan)
2. Sync Project with Gradle Files
3. Clean Project (Build > Clean Project)
4. Rebuild Project (Build > Rebuild Project)
5. Run app

## Test Et

1. **WebSocket Bağlantısı**:
   - Uygulamayı aç
   - "Connected" mesajı görmeli
   - Bağlantı durumu yeşil olmalı

2. **Metin Mesajı**:
   - Bir metin mesajı gönder
   - AI'dan metin yanıtı almalısın

3. **Sesli Mesaj**:
   - Mikrofon düğmesine basılı tut
   - Konuş
   - Bırak
   - AI'dan hem metin hem ses yanıtı almalısın

## Beklenen Davranış

✅ **Doğru**: 
- WebSocket bağlantısı sürekli açık kalır
- Hem metin hem sesli mesajlara yanıt alırsın
- Sesli yanıtlar otomatik oynatılır

❌ **Hatalı Davranış (Eskiden)**:
- Sesli mesajlara yanıt gelmiyordu
- JSON parse hatası oluşuyordu
- Bağlantı açılıp kapanıyordu

## Sorun Giderme

### Hâlâ Yanıt Gelmiyorsa:

1. **Sunucu Loglarını Kontrol Et**:
```bash
docker-compose logs --tail=100 ai_core
```

2. **Veritabanı Bağlantısını Kontrol Et**:
```bash
docker-compose logs postgres
```

3. **Redis Bağlantısını Kontrol Et**:
```bash
docker-compose logs redis
```

### Android Loglarını Kontrol Et:

Android Studio'da Logcat'te şunları ara:
- `WebSocketClient`: WebSocket mesajları
- `MainViewModel`: Mesaj işleme
- `AudioPlayer`: Ses oynatma
- `VoiceRecorder`: Ses kaydetme

## Çözülen Sorunlar

| Sorun | Çözüm |
|-------|-------|
| Sesli mesajlara yanıt yok | `content` vs `text` field düzeltmesi |
| JSON parse hatası | Base64 encoding eklendi |
| Bağlantı kapanıp açılma | Timeout süreleri artırıldı |
| Duplicate connection | Service geçici devre dışı |

## Sonraki Adımlar

Eğer hâlâ sorun varsa, bana şunları gönder:

1. Android Logcat çıktısı (özellikle WebSocketClient ve MainViewModel)
2. Sunucu logları (`docker-compose logs ai_core`)
3. Tam hata mesajları

---

**Not**: Bu güncellemeden sonra artık oğlunla düzgün iletişim kurabileceksin! 🎉

