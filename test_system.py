#!/usr/bin/env python3
"""
Interpol Red Notices System Test Script
Bu script sistemin tüm bileşenlerini test eder.
"""

import requests
import time
import json
import sys
from datetime import datetime


def test_web_app():
    """Web uygulamasını test eder"""
    print("🔍 Web uygulaması test ediliyor...")
    
    try:
        # Health check
        response = requests.get("http://localhost:8080/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f" Health check başarılı: {data}")
        else:
            print(f" Health check başarısız: {response.status_code}")
            return False
            
        # Ana sayfa
        response = requests.get("http://localhost:8080/", timeout=10)
        if response.status_code == 200:
            print(" Ana sayfa erişilebilir")
        else:
            print(f" Ana sayfa erişilemez: {response.status_code}")
            return False
            
        # API endpoint
        response = requests.get("http://localhost:8080/api/red-notices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f" API endpoint çalışıyor: {len(data)} kayıt bulundu")
        else:
            print(f" API endpoint çalışmıyor: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f" Web uygulaması test hatası: {e}")
        return False


def test_rabbitmq():
    """RabbitMQ'yu test eder"""
    print(" RabbitMQ test ediliyor...")
    
    try:
        response = requests.get("http://localhost:15672/api/overview", 
                              auth=('admin', 'admin123'), timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅RabbitMQ erişilebilir: {data.get('rabbitmq_version', 'Unknown')}")
            return True
        else:
            print(f" RabbitMQ erişilemez: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f" RabbitMQ test hatası: {e}")
        return False


def test_postgres():
    """PostgreSQL'i test eder"""
    print("🔍 PostgreSQL test ediliyor...")
    
    try:
        # Basit bir bağlantı testi
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="interpol_db",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        if version:
            print(f" PostgreSQL erişilebilir: {version[0]}")
        else:
            print(" PostgreSQL versiyon bilgisi alınamadı")
            return False
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f" PostgreSQL test hatası: {e}")
        return False


def test_docker_containers():
    """Docker container'larını test eder"""
    print(" Docker container'ları test ediliyor...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            containers = result.stdout.strip().split('\n')[1:]  # Header'ı atla
            expected_containers = [
                'interpol_postgres',
                'interpol_rabbitmq', 
                'interpol_scraper',
                'interpol_webapp',
                'interpol_consumer'
            ]
            
            running_containers = []
            for container in containers:
                if container.strip():
                    name = container.split('\t')[0]
                    status = container.split('\t')[1]
                    running_containers.append(name)
                    print(f" {name}: {status}")
            
            missing_containers = set(expected_containers) - set(running_containers)
            if missing_containers:
                print(f" Eksik container'lar: {missing_containers}")
                return False
            else:
                print(" Tüm container'lar çalışıyor")
                return True
        else:
            print(f" Docker komutu başarısız: {result.stderr}")
            return False
            
    except Exception as e:
        print(f" Docker test hatası: {e}")
        return False


def main():
    """Ana test fonksiyonu"""
    print("Interpol Red Notices System Test Başlatılıyor...")
    print(f" Test zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Docker Container'ları", test_docker_containers),
        ("PostgreSQL", test_postgres),
        ("RabbitMQ", test_rabbitmq),
        ("Web Uygulaması", test_web_app),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n {test_name} test ediliyor...")
        if test_func():
            passed += 1
        else:
            print(f" {test_name} testi başarısız!")
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f" Test Sonuçları: {passed}/{total} başarılı")
    
    if passed == total:
        print(" Tüm testler başarılı! Sistem çalışıyor.")
        print("\n Erişim Bilgileri:")
        print("   - Web Uygulaması: http://localhost:8080")
        print("   - RabbitMQ Management: http://localhost:15672")
        print("   - PostgreSQL: localhost:5432")
        return 0
    else:
        print("  Bazı testler başarısız. Lütfen logları kontrol edin.")
        print("\n Sorun Giderme:")
        print("   - docker-compose logs -f")
        print("   - docker-compose restart")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 