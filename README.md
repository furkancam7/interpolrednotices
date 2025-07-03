# Interpol Red Notices System

Bu proje, Interpol tarafından yayınlanan arananlar verisini çeken, kuyruğa yazan, veritabanına kaydeden ve web arayüzünde gösteren modern bir sistemdir.

##  Mimari

Sistem 4 ana container'dan oluşmaktadır:

- **PostgreSQL**: Veritabanı sistemi
- **RabbitMQ**: Mesaj kuyruğu sistemi
- **Scraper (Container A)**: Interpol verilerini çeken servis
- **WebApp (Container B)**: Web sunucu ve consumer servisi

##  Özellikler

-  **Modern Teknoloji Stack**: Python 3.11, SQLAlchemy, Flask, RabbitMQ, PostgreSQL
-  **Nesne Tabanlı Programlama**: Tüm sınıflar OOP prensiplerine uygun
-  **Environment Configuration**: Tüm değişkenler environment üzerinden yönetilebilir
-  **Docker Containerization**: Tam Docker desteği
- **Real-time Updates**: Gerçek zamanlı veri güncellemeleri




##  Kurulum

### 1. Projeyi Klonlayın

```bash
git clone <repository-url>
cd interpol-red-notices
```

### 2. Environment Dosyasını Oluşturun

```bash
# Linux/Mac için
cp env.example .env

# Windows PowerShell için
copy env.example .env
```

**Not:** `.env` dosyası zaten oluşturulmuş ve yapılandırılmıştır. Tüm environment değişkenleri Docker container'ları için uygun şekilde ayarlanmıştır.

Gerekirse `.env` dosyasındaki değerleri düzenleyin.

### 3. Docker Compose ile Başlatın

```bash
docker-compose up -d
```

### 4. Servislerin Başlamasını Bekleyin

```bash
docker-compose logs -f
```

##  Erişim

- **Web Uygulaması**: http://localhost:8080
- **RabbitMQ Management**: http://localhost:15672
  - Kullanıcı adı: `admin`
  - Şifre: `admin123`
- **PostgreSQL**: localhost:5432
  - Veritabanı: `interpol_db`
  - Kullanıcı: `postgres`
  - Şifre: `postgres`

##  Proje Yapısı

```
interpol-red-notices/
├── Container_A/                 # Scraper Service
│   ├── scraper_producer.py     # Ana scraper uygulaması
│   ├── requirements.txt        # Python bağımlılıkları
│   └── Dockerfile             # Container A Dockerfile
├── Container_B/                 # Web Application
│   ├── webapp.py              # Flask web uygulaması
│   ├── consumer_db.py         # RabbitMQ consumer
│   ├── models.py              # SQLAlchemy modelleri
│   ├── database.py            # Veritabanı yönetimi
│   ├── requirements.txt       # Python bağımlılıkları
│   ├── templates/             # HTML template'leri
│   │   ├── index.html         # Ana sayfa
│   │   └── error.html         # Hata sayfası
│   └── Dockerfile            # Container B Dockerfile
├── Container_C/                 # RabbitMQ
│   └── Dockerfile            # RabbitMQ Dockerfile
├── docker-compose.yml         # Docker Compose konfigürasyonu
├── env.example               # Environment değişkenleri örneği
└── README.md                 # Bu dosya
```

## 🔧 Konfigürasyon

### Environment Değişkenleri

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| `DB_HOST` | PostgreSQL host | `postgres` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Veritabanı adı | `interpol_db` |
| `DB_USER` | Veritabanı kullanıcısı | `postgres` |
| `DB_PASSWORD` | Veritabanı şifresi | `postgres` |
| `RABBITMQ_HOST` | RabbitMQ host | `rabbitmq` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ kullanıcısı | `admin` |
| `RABBITMQ_PASSWORD` | RabbitMQ şifresi | `admin123` |
| `QUEUE_NAME` | Kuyruk adı | `red_notices_queue` |
| `SCRAPING_INTERVAL` | Scraping aralığı (saniye) | `300` |
| `PORT` | Web uygulaması portu | `5000` |
| `FLASK_DEBUG` | Flask debug modu | `false` |
| `SECRET_KEY` | Flask secret key | `your-secret-key` |

## Test

### Manuel Test

1. **Web Uygulaması Testi**:
   ```bash
   curl http://localhost:8080/health
   ```

2. **API Testi**:
   ```bash
   curl http://localhost:8080/api/red-notices
   ```

3. **RabbitMQ Testi**:
   ```bash
   docker exec interpol_rabbitmq rabbitmq-diagnostics ping
   ```

### Otomatik Test

```bash
# Tüm servislerin sağlık kontrolü
docker-compose ps

# Log kontrolü
docker-compose logs scraper
docker-compose logs webapp
docker-compose logs consumer
```

##  Monitoring

### Health Check Endpoints

- **Web App**: `http://localhost:8080/health`
- **RabbitMQ**: `http://localhost:15672`
- **PostgreSQL**: `docker exec interpol_postgres pg_isready`

### Log Monitoring

```bash
# Tüm logları görüntüle
docker-compose logs -f

# Belirli servisin loglarını görüntüle
docker-compose logs -f scraper
docker-compose logs -f webapp
docker-compose logs -f consumer
```

## Veri Akışı

1. **Scraper (Container A)**:
   - Interpol web sitesinden veri çeker
   - RabbitMQ kuyruğuna gönderir
   - Belirli aralıklarla çalışır (varsayılan: 5 dakika)

2. **Consumer (Container B)**:
   - RabbitMQ kuyruğundan mesajları okur
   - PostgreSQL veritabanına kaydeder
   - Güncellemeleri tespit eder

3. **WebApp (Container B)**:
   - Veritabanından verileri çeker
   - Modern web arayüzünde gösterir
   - API endpoint'leri sağlar

##  Sorun Giderme

### Yaygın Sorunlar

1. **Servisler Başlamıyor**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **Veritabanı Bağlantı Hatası**:
   ```bash
   docker-compose logs postgres
   docker-compose restart postgres
   ```

3. **RabbitMQ Bağlantı Hatası**:
   ```bash
   docker-compose logs rabbitmq
   docker-compose restart rabbitmq
   ```

4. **Scraper Çalışmıyor**:
   ```bash
   docker-compose logs scraper
   docker-compose restart scraper
   ```

### Log Seviyeleri

- **INFO**: Normal işlemler
- **WARNING**: Uyarılar
- **ERROR**: Hatalar
- **DEBUG**: Detaylı debug bilgileri



- Interpol - Veri kaynağı
- Docker - Containerization
- Flask - Web framework
- SQLAlchemy - ORM
- RabbitMQ - Message queue
- PostgreSQL - Database
