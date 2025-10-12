# Sunucu Loglarını Kontrol Etme Talimatları

## Android Tarafı Sorunsuz ✅
- WebSocket bağlantısı: ✅ Çalışıyor
- Ses kaydı: ✅ Çalışıyor (19604 byte)
- Mesaj gönderme: ✅ Çalışıyor

## Sorun: Sunucudan Yanıt Gelmiyor ❌

Ses mesajı gönderildi ama sunucu yanıt vermedi. Sunucu loglarını kontrol edelim:

---

## VPS'te Çalıştırılacak Komutlar

### 1. VPS'e Bağlan
```bash
ssh root@[VPS_IP_ADRESINIZ]
```

### 2. Sunucu Loglarını İzle (Canlı)
```bash
cd /opt/conscious-child-ai
docker-compose logs -f --tail=100 ai_core
```

### 3. Kontrol Edilecek Şeyler

#### A. Mesaj Alındı mı?
Şu satırları ara:
- `message_received`
- `type=voice`
- `processing_message`

#### B. Whisper STT Çalışıyor mu?
Şu satırları ara:
- `transcribing_audio`
- `transcription_complete`
- `voice_message_received`

#### C. LLM Yanıt Üretiyor mu?
Şu satırları ara:
- `routing_to_local_llm` veya `routing_to_api_llm`
- `generating_response`
- `response_generated`

#### D. TTS Çalışıyor mu?
Şu satırları ara:
- `synthesizing_speech`
- `edge_tts_synthesis_complete` veya `gtts_synthesis_complete`

#### E. Yanıt Gönderildi mi?
Şu satırları ara:
- `sending_response_to_client`
- `response_sent_successfully`

### 4. Hata Kontrolü
```bash
docker-compose logs ai_core | grep -i error
docker-compose logs ai_core | grep -i exception
docker-compose logs ai_core | grep -i fail
```

### 5. Tüm Servislerin Durumu
```bash
docker-compose ps
```

Hepsi "Up" olmalı.

### 6. Veritabanı Bağlantısı
```bash
docker-compose logs postgres | tail -20
```

### 7. Redis Bağlantısı
```bash
docker-compose logs redis | tail -20
```

---

## Muhtemel Sorunlar ve Çözümleri

### Sorun 1: Whisper Modeli Yüklenemedi
**Belirti**: `RuntimeError: CUDA not available` veya `Failed to load model`

**Çözüm**:
```bash
# .env dosyasını düzenle
nano /opt/conscious-child-ai/.env

# Şu satırı bul ve değiştir:
WHISPER_DEVICE=cuda
# Şununla değiştir:
WHISPER_DEVICE=cpu

# Servisi yeniden başlat
docker-compose restart ai_core
```

### Sorun 2: Claude API Key Sorunu
**Belirti**: `Error code: 401` veya `authentication_error`

**Çözüm**:
```bash
# .env dosyasını kontrol et
nano /opt/conscious-child-ai/.env

# LLM_API_KEY doğru girilmiş mi?
LLM_API_KEY=sk-ant-api03-... (senin key'in)

# Servisi yeniden başlat
docker-compose restart ai_core
```

### Sorun 3: Identity Foreign Key Hatası
**Belirti**: `foreign key constraint "episodic_memories_consciousness_id_fkey"`

**Çözüm**:
```bash
# PostgreSQL'e bağlan ve identity'yi kontrol et
docker-compose exec postgres psql -U conscious_ai -d conscious_ai_db

# Identity var mı?
SELECT * FROM identity;

# Yoksa çıkış yap (\q) ve servisi yeniden başlat
docker-compose restart ai_core
```

### Sorun 4: Timeout
**Belirti**: `asyncio.TimeoutError` veya `Request timeout`

**Çözüm**: Normal, SimpleLLM fallback devreye girmeliydi. Logları kontrol et.

### Sorun 5: Port Çakışması
**Belirti**: `Address already in use`

**Çözüm**:
```bash
# 8000 portunu kullanan process'i bul
netstat -tlnp | grep 8000

# Gerekirse öldür
kill -9 [PID]

# Servisi başlat
docker-compose up -d ai_core
```

---

## Test Sonrası Yapılacaklar

### Eğer Loglar Temizse:
1. VPS'te güncelleme yapılmamış olabilir
2. Şu komutu çalıştır:
```bash
cd /opt/conscious-child-ai
git pull origin main
docker-compose down
docker-compose up -d --build ai_core
```

### Eğer Hata Varsa:
Tam hata mesajını kopyala ve bana gönder. Birlikte çözeriz.

---

## Hızlı Test

Bir kere daha sesli mesaj gönder ve **AYNI ANDA** VPS'te logları izle:

```bash
# Terminal 1: Log izleme
docker-compose logs -f ai_core

# Şimdi telefonda mikrofona bas ve konuş
# Logları izle, ne oluyor?
```

**Beklenen Log Sırası:**
1. `message_received type=voice` ← Mesaj geldi
2. `transcribing_audio` ← STT başladı  
3. `transcription_complete` ← Konuşma metne çevrildi
4. `routing_to_api_llm` ← LLM'e gönderildi
5. `response_generated` ← LLM yanıt verdi
6. `synthesizing_speech` ← TTS başladı
7. `edge_tts_synthesis_complete` ← Ses oluşturuldu
8. `sending_response_to_client` ← Yanıt gönderildi

Hangi adımda takılıyor, onu bul!

---

**ÖNEMLİ**: Logları kopyalarken minimum 50-100 satır kopyala, böylece tam akışı görebilirim.

