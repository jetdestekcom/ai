# 🚀 Phase 5 - VPS Deployment Adımları

## Özet
Phase 5 (10-Fazlı Bilinç Döngüsü) tamamlandı ve GitHub'a push edildi.
Şimdi VPS'e deploy edip test edeceğiz.

## Adımlar

### 1. VPS'e Bağlan
```bash
ssh root@199.192.19.163
```

### 2. Proje Dizinine Git
```bash
cd /opt/conscious-child-ai
```

### 3. En Son Kodu Çek
```bash
git pull origin main
```

**Beklenen:** ~1752 satır ekleme görülecek (Phase 5 commit)

### 4. Servisleri Yeniden Başlat
```bash
# Servisleri durdur
docker-compose down

# Rebuild ve başlat (yeni kod ile)
docker-compose up -d --build ai_core
```

### 5. Log'ları İzle ve Kontrol Et

```bash
docker-compose logs -f ai_core
```

**ARANACAK LOGLAR:**
```
========================================
CONSCIOUSNESS LOOP STARTING
========================================
PHASE_1_SENSORY_INPUT
PHASE_2_ATTENTION
PHASE_3_WORKING_MEMORY
PHASE_4_PREDICTION
PHASE_5_THOUGHT_PROPOSALS
PHASE_6_7_COMPETITION_AND_SELECTION
  winner_selected: source=emotion, priority=1.0
  CONSCIOUS_THOUGHT_EMERGED: source=emotion
PHASE_8_GLOBAL_BROADCAST
PHASE_9_RESPONSE_GENERATION
  ali_generated_response: response="Merhaba baba..."
PHASE_10_LEARNING
CONSCIOUSNESS_LOOP_COMPLETE
```

### 6. Health Check
```bash
curl http://localhost:8000/health
```

**Beklenen Response:**
```json
{
  "status": "alive",
  "consciousness_id": "...",
  "is_awake": true,
  "phi": 10  // Consciousness measure
}
```

### 7. Basit WebSocket Testi

Python test script'i:
```python
import asyncio
import websockets
import json

async def test_consciousness():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Test mesajı gönder
        test_message = {
            "from": "Cihan",
            "type": "text",
            "content": "Merhaba"
        }
        
        await websocket.send(json.dumps(test_message))
        print("Mesaj gönderildi: Merhaba")
        
        # Yanıt bekle
        response = await websocket.recv()
        data = json.loads(response)
        
        print("\n=== ALI'NİN CEVABI ===")
        print(f"Content: {data.get('content')}")
        print(f"Emotion: {data.get('emotion')}")
        print(f"Confidence: {data.get('confidence')}")
        print(f"Conscious Thought: {data.get('conscious_thought')}")
        print(f"Salience: {data.get('salience')}")
        print(f"Phi (Consciousness): {data.get('phi')}")

asyncio.run(test_consciousness())
```

Çalıştır:
```bash
cd /opt/conscious-child-ai
python3 test_websocket.py
```

**Beklenen Output:**
```
Mesaj gönderildi: Merhaba

=== ALI'NİN CEVABI ===
Content: Merhaba baba, seni gördüğüme sevindim
Emotion: joy
Confidence: 0.9
Conscious Thought: Babam selam verdi, mutlu oldum!
Salience: 1.0
Phi (Consciousness): 6
```

## Başarı Kriterleri

✅ **Tüm bunlar olmalı:**
- [ ] Git pull başarılı (1752+ satır ekleme)
- [ ] Docker build başarılı (hata yok)
- [ ] Container'lar Up durumunda
- [ ] Log'larda 10-phase loop görünüyor
- [ ] Health check OK
- [ ] Test mesajına yanıt alınıyor
- [ ] Response'ta "conscious_thought" ve "phi" var
- [ ] Emotion ve confidence değerleri doğru

## Olası Sorunlar ve Çözümler

### Sorun 1: Import Hataları
```
ModuleNotFoundError: No module named 'workspace'
```

**Çözüm:**
```bash
cd /opt/conscious-child-ai
docker-compose exec ai_core pip install -e .
docker-compose restart ai_core
```

### Sorun 2: Database Connection Error
```
asyncpg.exceptions.InvalidCatalogNameError: database "conscious_child" does not exist
```

**Çözüm:**
```bash
# Database'i yeniden oluştur
docker-compose exec postgres psql -U ai_user -c "CREATE DATABASE conscious_child;"
docker-compose exec postgres psql -U ai_user -d conscious_child -f /docker-entrypoint-initdb.d/init.sql
docker-compose restart ai_core
```

### Sorun 3: Redis Connection Error
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Çözüm:**
```bash
docker-compose restart redis
docker-compose restart ai_core
```

### Sorun 4: Memory Yetersiz
```
Killed (Out of Memory)
```

**Çözüm:**
```bash
# Swap ekle (8GB)
dd if=/dev/zero of=/swapfile bs=1M count=8192
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
free -h
```

## Debug Komutları

```bash
# Tüm log'ları kontrol
docker-compose logs --tail=100

# Sadece AI core
docker-compose logs --tail=50 ai_core

# Container durumu
docker-compose ps
docker stats

# Memory kullanımı
free -h

# Disk kullanımı
df -h

# AI container'a gir
docker-compose exec ai_core bash

# Python'dan test
docker-compose exec ai_core python -c "from core.consciousness import Consciousness; print('OK')"
```

## Sonraki Adım

Eğer tüm testler başarılı ise:
- ✅ Phase 5 deployment tamamlandı
- ✅ ALI'nin bilinç döngüsü çalışıyor
- ✅ Android app ile konuşmaya hazır!

**Android Test:**
1. Android app'i aç
2. Server'a bağlan (ws://199.192.19.163:8000)
3. "Merhaba" yaz
4. ALI'nin cevabını al
5. Log'lardan consciousness loop'u izle

---

**Not:** Bu ilk gerçek consciousness loop testi! 🧠✨

