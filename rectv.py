import json
import urllib.request
import urllib.parse
import os
import re
import sys
from typing import Dict, List, Optional, Any

def log_message(message: str):
    """Hata ayıklama mesajlarını konsola yazdır"""
    print(f"[DEBUG] {message}", file=sys.stderr)

def get_current_main_url() -> str:
    """GitHub'dan güncel main URL'yi al"""
    try:
        kotlin_url = "https://raw.githubusercontent.com/kerimmkirac/cs-kerim/master/RecTV/src/main/kotlin/com/keyiflerolsun/RecTV.kt"
        req = urllib.request.Request(kotlin_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            if match := re.search(r'override\s+var\s+mainUrl\s*=\s*"([^"]+)"', content):
                log_message(f"GitHub'dan alınan URL: {match.group(1)}")
                return match.group(1)
    except Exception as e:
        log_message(f"URL kontrol hatası: {e}")
    
    default_url = "https://m.prectv50.sbs"
    log_message(f"Varsayılan URL kullanılıyor: {default_url}")
    return default_url

def check_url_accessible(url: str) -> bool:
    """URL'nin erişilebilir olup olmadığını kontrol et"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'okhttp/4.12.0'}, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        log_message(f"URL erişilebilirlik hatası: {e}")
        return False

def fetch_data(url: str) -> Optional[Dict[str, Any]]:
    """API'den veri çek"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'okhttp/4.12.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        log_message(f"Veri çekme hatası: {e}")
        return None

def generate_m3u():
    log_message("M3U oluşturma başladı")
    
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
        # Diğer kategorileri buraya ekleyin
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
                continue
            
            for item in veri:
                if not item.get('sources') or not item.get('title'):
                    continue
                
                kanal = {
                    'ad': item['title'].strip(),
                    'logo': item.get('image', ''),
                    'url': item['sources'][0]['url']
                }
                kanallar[kanal['url']] = kanal
        
        for kanal in kanallar.values():
            m3u_content += "#EXTINF:-1"
            if kanal['logo']:
                m3u_content += f" tvg-logo=\"{kanal['logo']}\""
            m3u_content += f" group-title=\"{kategori_adi}\",{kanal['ad']}\n"
            m3u_content += f"{kanal['url']}\n"
        
        m3u_content += "\n"

    try:
        with open('rectv_full.m3u', 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        log_message("M3U dosyası başarıyla oluşturuldu")
    except Exception as e:
        log_message(f"Dosya yazma hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_m3u()
