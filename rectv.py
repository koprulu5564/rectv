import json
import urllib.request
import urllib.error
import re
import os
import sys
from typing import Dict, List, Optional, Set

# API Konfigürasyon
DEFAULT_BASE_URL = 'https://m.prectv50.sbs'
SOURCE_URL = 'https://raw.githubusercontent.com/kerimmkirac/cs-kerim2/main/RecTV/src/main/kotlin/com/kerimmkirac/RecTV.kt'
API_KEY = '4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452'
SUFFIX = f'/{API_KEY}'

# Kullanıcı ayarları
USER_AGENT = 'googleusercontent'
REFERER = 'https://twitter.com/'

def is_base_url_working(base_url: str) -> bool:
    """Base URL'nin çalışıp çalışmadığını kontrol et"""
    test_url = f"{base_url}/api/channel/by/filtres/0/0/0{SUFFIX}"
    try:
        req = urllib.request.Request(
            test_url,
            headers={'User-Agent': 'okhttp/4.12.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except:
        return False

def get_dynamic_base_url() -> str:
    """GitHub'dan dinamik olarak Base URL'yi al"""
    try:
        with urllib.request.urlopen(SOURCE_URL) as response:
            content = response.read().decode('utf-8')
            if match := re.search(r'override\s+var\s+mainUrl\s*=\s*"([^"]+)"', content):
                return match.group(1)
    except Exception as e:
        print(f"GitHub'dan URL alınamadı: {e}", file=sys.stderr)
    return DEFAULT_BASE_URL

def fetch_data(url: str) -> Optional[List[Dict]]:
    """API'den veri çek"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': USER_AGENT,
                'Referer': REFERER
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"API hatası ({url}): {e}", file=sys.stderr)
        return None

def process_content(content: Dict, category_name: str) -> str:
    """İçeriği M3U formatına dönüştür"""
    m3u_lines = []
    if not content.get('sources'):
        return ''
    
    for source in content['sources']:
        if source.get('type') == 'm3u8' and source.get('url'):
            title = content.get('title', '')
            image = content.get('image', '')
            content_id = content.get('id', '')
            
            m3u_lines.append(
                f'#EXTINF:-1 tvg-id="{content_id}" tvg-name="{title}" '
                f'tvg-logo="{image}" group-title="{category_name}", {title}\n'
                f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n'
                f'#EXTVLCOPT:http-referrer={REFERER}\n'
                f"{source['url']}\n"
            )
    return ''.join(m3u_lines)

def main():
    # Base URL'yi belirle
    base_url = DEFAULT_BASE_URL if is_base_url_working(DEFAULT_BASE_URL) else get_dynamic_base_url()
    print(f"Kullanılan Base URL: {base_url}", file=sys.stderr)
    
    m3u_content = ["#EXTM3U\n"]
    
    # CANLI YAYINLAR (0-3 arası sayfalar)
    for page in range(4):
        url = f"{base_url}/api/channel/by/filtres/0/0/{page}{SUFFIX}"
        if data := fetch_data(url):
            for content in data:
                m3u_content.append(process_content(content, "Canlı Yayınlar"))
    
    # FİLMLER (Tüm kategoriler)
    movie_categories = {
        "0": "Son Filmler",
        "14": "Aile",
        "1": "Aksiyon",
        "13": "Animasyon",
        "19": "Belgesel Filmleri",
        "4": "Bilim Kurgu",
        "2": "Dram",
        "10": "Fantastik",
        "3": "Komedi",
        "8": "Korku",
        "17": "Macera",
        "5": "Romantik"
    }
    
    for category_id, category_name in movie_categories.items():
        for page in range(8):  # 0-7 arası sayfalar
            url = f"{base_url}/api/movie/by/filtres/{category_id}/created/{page}{SUFFIX}"
            if data := fetch_data(url):
                for content in data:
                    m3u_content.append(process_content(content, category_name))
    
    # DİZİLER
    for page in range(8):  # 0-7 arası sayfalar
        url = f"{base_url}/api/serie/by/filtres/0/created/{page}{SUFFIX}"
        if data := fetch_data(url):
            for content in data:
                m3u_content.append(process_content(content, "Son Diziler"))
    
    # Dosyaya yaz
    with open('rectv_full.m3u', 'w', encoding='utf-8') as f:
        f.write(''.join(m3u_content))
    print("M3U dosyası başarıyla oluşturuldu!", file=sys.stderr)

if __name__ == "__main__":
    main()
