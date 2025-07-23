import json
import urllib.request
import os
import sys
from typing import Dict, List, Set

# API Konfigürasyon
API_BASE_URL = "https://m.prectv50.sbs"
API_KEY = os.getenv('API_KEY', "4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452")

# TÜM KATEGORİLER (PHP'dekiyle birebir aynı)
CATEGORIES = {
    "Canlı Yayınlar": {
        'endpoint': "/api/channel/by/filtres/0/0/SAYFA/",
        'pages': range(0, 5)  # Canlılar için 0-4
    },
    "Son Eklenen Filmler": {
        'endpoint': "/api/movie/by/filtres/0/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Son Eklenen Diziler": {
        'endpoint': "/api/serie/by/filtres/0/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Aile Filmleri": {
        'endpoint': "/api/movie/by/filtres/14/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Aksiyon Filmleri": {
        'endpoint': "/api/movie/by/filtres/1/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Animasyon Filmleri": {
        'endpoint': "/api/movie/by/filtres/13/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Belgeseller": {
        'endpoint': "/api/movie/by/filtres/19/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Bilim Kurgu Filmleri": {
        'endpoint': "/api/movie/by/filtres/4/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Dram Filmleri": {
        'endpoint': "/api/movie/by/filtres/2/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Fantastik Filmleri": {
        'endpoint': "/api/movie/by/filtres/10/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Komedi Filmleri": {
        'endpoint': "/api/movie/by/filtres/3/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Korku Filmleri": {
        'endpoint': "/api/movie/by/filtres/8/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Macera Filmleri": {
        'endpoint': "/api/movie/by/filtres/17/created/SAYFA/",
        'pages': range(0, 8)
    },
    "Romantik Filmleri": {
        'endpoint': "/api/movie/by/filtres/5/created/SAYFA/",
        'pages': range(0, 8)
    }
}

def fetch_data(url: str) -> List[Dict]:
    """API'den veri çekme fonksiyonu (optimize edilmiş)"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'okhttp/4.12.0',
                'Accept': 'application/json'
            },
            timeout=15
        )
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"[HATA] {url} - {str(e)}", file=sys.stderr)
    return []

def process_category(category: str, config: Dict) -> str:
    """Kategori işleme fonksiyonu"""
    m3u_content = ""
    unique_urls = set()  # Tekrar eden URL'leri engelle
    
    for page in config['pages']:
        url = f"{API_BASE_URL}{config['endpoint'].replace('SAYFA', str(page))}{API_KEY}"
        items = fetch_data(url)
        
        for item in items if items else []:
            try:
                if not item.get('sources') or not item.get('title'):
                    continue
                    
                stream_url = item['sources'][0]['url']
                if not stream_url or stream_url in unique_urls:
                    continue
                    
                unique_urls.add(stream_url)
                
                # M3U satırını oluştur
                m3u_content += "#EXTINF:-1"
                if item.get('image'):
                    m3u_content += f' tvg-logo="{item["image"]}"'
                m3u_content += f' group-title="{category}",{item["title"]}\n'
                m3u_content += f"#EXTVLCOPT:http-user-agent=googleuseragent\n{stream_url}\n"
            except Exception as e:
                print(f"[HATA] İşlenemedi: {item} - {str(e)}", file=sys.stderr)
    
    return m3u_content

def generate_m3u():
    """Ana M3U oluşturma fonksiyonu"""
    try:
        with open('rectv_full.m3u', 'w', encoding='utf-8') as f:
            # M3U Başlık
            f.write("#EXTM3U\n")
            f.write(f'#EXTINF:-1 tvg-logo="{API_BASE_URL}/static/img/logo.png",RecTV Tam Liste\n')
            f.write(f"{API_BASE_URL}/static/img/logo.png\n\n")
            
            # Tüm kategorileri işle
            for category, config in CATEGORIES.items():
                print(f"İşleniyor: {category}...", file=sys.stderr)
                category_content = process_category(category, config)
                f.write(category_content)
                print(f"Tamamlandı: {category} ({category_content.count('#EXTINF')} içerik)", file=sys.stderr)
                
        print("M3U başarıyla oluşturuldu!", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[KRİTİK HATA] {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    sys.exit(0 if generate_m3u() else 1)
