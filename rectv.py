import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Any
import os
import re

def get_current_main_url():
    """GitHub'dan güncel main URL'yi al"""
    backup_url = "https://m.prectv50.sbs"  # Varsayılan URL
    
    try:
        # GitHub'dan Kotlin dosyasını al
        kotlin_url = "https://raw.githubusercontent.com/kerimmkirac/cs-kerim/master/RecTV/src/main/kotlin/com/keyiflerolsun/RecTV.kt"
        req = urllib.request.Request(
            kotlin_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            
            # Regex ile mainUrl değerini bul
            match = re.search(r'override\s+var\s+mainUrl\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
            
    except Exception as e:
        print(f"URL kontrol hatası: {e}")
    
    return backup_url

def check_url_accessible(url):
    """URL'nin erişilebilir olup olmadığını kontrol et"""
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'okhttp/4.12.0'},
            method='HEAD'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except:
        return False

def generate_m3u():
    # API key (GitHub Secrets'tan alınacak)
    api_key = os.environ.get('API_KEY', "4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452")
    
    # Main URL'yi al ve kontrol et
    main_url = get_current_main_url()
    if not check_url_accessible(main_url):
        print(f"Main URL ({main_url}) erişilemiyor, GitHub'dan güncel URL alınıyor...")
        main_url = get_current_main_url()
        print(f"Yeni URL: {main_url}")
    
    # Kategoriler
    kategoriler = {
        "Canlı Yayınlar": {
            'endpoint': "/api/channel/by/filtres/0/0/SAYFA/{api_key}",
            'sayfalar': list(range(0, 8))
        },
        # Diğer kategoriler aynı şekilde devam eder...
    }

    # ... (önceki kodun geri kalanı aynı) ...

if __name__ == "__main__":
    generate_m3u()
