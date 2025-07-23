import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Any
import os

def generate_m3u():
    # API ayarları
    api_url = "https://m.prectv50.sbs"
    api_key = "4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452"
    
    # Kategoriler
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

    # Önbellek için sözlük
    cache = {}

    def veri_cek(url: str) -> Optional[Dict[str, Any]]:
        if url in cache:
            return cache[url]
        
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'okhttp/4.12.0'
                }
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                cache[url] = result
                return result
        except:
            return None

    # M3U başlığı
    m3u_content = "#EXTM3U\n"
    m3u_content += f'#EXTINF:-1 tvg-logo="{api_url}/static/img/logo.png",RecTV Tam Liste\n'
    m3u_content += f"{api_url}/static/img/logo.png\n\n"

    # Kategorileri işle
    for kategori_adi, ayar in kategoriler.items():
        kanallar = {}
        
        # Sayfaları tara
        for sayfa in ayar['sayfalar']:
            endpoint = ayar['endpoint'].replace('SAYFA', str(sayfa)).replace('{api_key}', api_key)
            url = api_url + endpoint
            veri = veri_cek(url)
            
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
                
                # Benzersiz URL kontrolü
                kanallar[kanal['url']] = kanal
        
        # Kanal ekle
        for kanal in kanallar.values():
            m3u_content += "#EXTINF:-1"
            if kanal['logo']:
                m3u_content += f" tvg-logo=\"{kanal['logo']}\""
            m3u_content += f" group-title=\"{kategori_adi}\",{kanal['ad']}\n"
            m3u_content += f"{kanal['url']}\n"
        
        m3u_content += "\n"

    # Arama parametresi kontrolü (GitHub Actions'ta kullanılmayacak)
    if os.environ.get('ARA'):
        aranan = urllib.parse.quote(os.environ['ARA'].strip())
        sonuclar = veri_cek(f"{api_url}/api/search/{aranan}/{api_key}/")
        
        if sonuclar:
            m3u_content += f'#EXTINF:-1 tvg-logo="{api_url}/static/img/logo.png" group-title="Arama Sonuçları","{os.environ["ARA"]}" için sonuçlar\n'
            m3u_content += f"{api_url}/static/img/logo.png\n"
            
            tum_sonuclar = (sonuclar.get('channels', []) + 
                           sonuclar.get('posters', []))
            
            for sonuc in tum_sonuclar:
                if not sonuc.get('sources') or not sonuc.get('title'):
                    continue
                
                m3u_content += "#EXTINF:-1"
                if sonuc.get('image'):
                    m3u_content += f" tvg-logo=\"{sonuc['image']}\""
                m3u_content += f" group-title=\"Arama\",{sonuc['title']}\n"
                m3u_content += f"{sonuc['sources'][0]['url']}\n"
    
    # M3U dosyasını oluştur
    with open('rectv_full.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)

if __name__ == "__main__":
    generate_m3u()
