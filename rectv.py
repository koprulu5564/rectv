import json
import urllib.request
import urllib.parse
import os
import re
import sys
from typing import Dict, List, Optional, Any

def log_message(message: str):
    print(f"[DEBUG] {message}", file=sys.stderr)

def get_current_main_url() -> str:
    try:
        kotlin_url = "https://raw.githubusercontent.com/kerimmkirac/cs-kerim/master/RecTV/src/main/kotlin/com/keyiflerolsun/RecTV.kt"
        req = urllib.request.Request(kotlin_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            if match := re.search(r'override\s+var\s+mainUrl\s*=\s*"([^"]+)"', content):
                return match.group(1)
    except Exception as e:
        log_message(f"URL kontrol hatası: {e}")
    
    return "https://m.prectv50.sbs"

def check_url_accessible(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'okhttp/4.12.0'}, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        log_message(f"URL erişilebilirlik hatası: {e}")
        return False

def fetch_data(url: str) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'okhttp/4.12.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        log_message(f"Veri çekme hatası: {e} - URL: {url}")
        return None

def generate_m3u():
    api_key = os.environ.get('API_KEY', "4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452")
    main_url = get_current_main_url()
    
    if not check_url_accessible(main_url):
        log_message("Ana URL erişilemez, güncel URL alınıyor...")
        main_url = get_current_main_url()

    kategoriler = {
        "Canlı Yayınlar": {
            'endpoint': "/api/channel/by/filtres/0/0/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Son Eklenen Filmler": {
            'endpoint': "/api/movie/by/filtres/0/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Son Eklenen Diziler": {
            'endpoint': "/api/serie/by/filtres/0/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Aile Filmleri": {
            'endpoint': "/api/movie/by/filtres/14/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Aksiyon Filmleri": {
            'endpoint': "/api/movie/by/filtres/1/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Animasyon Filmleri": {
            'endpoint': "/api/movie/by/filtres/13/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Belgeseller": {
            'endpoint': "/api/movie/by/filtres/19/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Bilim Kurgu Filmleri": {
            'endpoint': "/api/movie/by/filtres/4/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Dram Filmleri": {
            'endpoint': "/api/movie/by/filtres/2/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Fantastik Filmleri": {
            'endpoint': "/api/movie/by/filtres/10/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Komedi Filmleri": {
            'endpoint': "/api/movie/by/filtres/3/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Korku Filmleri": {
            'endpoint': "/api/movie/by/filtres/8/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Macera Filmleri": {
            'endpoint': "/api/movie/by/filtres/17/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        "Romantik Filmleri": {
            'endpoint': "/api/movie/by/filtres/5/created/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        }
    }

    m3u_content = "#EXTM3U\n"
    m3u_content += f'#EXTINF:-1 tvg-logo="{main_url}/static/img/logo.png",RecTV Tam Liste\n'
    m3u_content += f"{main_url}/static/img/logo.png\n\n"

    for kategori_adi, ayar in kategoriler.items():
        kanallar = {}
        
        for sayfa in ayar['sayfalar']:
            endpoint = ayar['endpoint'].replace('SAYFA', str(sayfa)).replace('{api_key}', api_key)
            url = main_url + endpoint
            veri = fetch_data(url)
            
            if not veri:
                log_message(f"Veri alınamadı: {url}")
                continue
            
            for item in veri:
                if not item.get('sources') or not item.get('title'):
                    continue
                
                stream_url = item['sources'][0]['url']
                if not stream_url.startswith('http'):
                    continue
                
                kanal = {
                    'ad': item['title'].strip(),
                    'logo': item.get('image', ''),
                    'url': stream_url
                }
                kanallar[kanal['url']] = kanal
        
        for kanal in kanallar.values():
            m3u_content += "#EXTINF:-1"
            if kanal['logo']:
                m3u_content += f" tvg-logo=\"{kanal['logo']}\""
            m3u_content += f" group-title=\"{kategori_adi}\",{kanal['ad']}\n"
            m3u_content += f"#EXTVLCOPT:http-user-agent=googleuseragent\n"
            m3u_content += f"{kanal['url']}\n"
        
        log_message(f"{kategori_adi} - {len(kanallar)} kanal eklendi")
        m3u_content += "\n"

    try:
        with open('rectv_full.m3u', 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        log_message(f"M3U dosyası oluşturuldu - Toplam {sum(len(v) for v in kategoriler.values())} içerik")
    except Exception as e:
        log_message(f"Dosya yazma hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_m3u()
