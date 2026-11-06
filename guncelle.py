import urllib.request
import re
import ssl

# SSL Ayarları
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def url_getir(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=20) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[-] İndirme hatası ({url}): {e}")
        return ""

# ==========================================
# 1. 1080p FULL HD CANLI SPOR KANALLARI
# ==========================================
PREMIUM_SPOR_KANALLARI = [
    {
        "ad": "TRT Spor HD [1080p]",
        "kategori": "⚽ Spor: Türkiye HD",
        "logo": "https://raw.githubusercontent.com/iptv-org/epg/master/sites/tvplus.com.tr/trt-spor.png",
        "link": "https://tv-trtsporyildiz.medya.trt.com.tr/master.m3u8"
    },
    {
        "ad": "TRT Spor Yıldız HD [1080p]",
        "kategori": "⚽ Spor: Türkiye HD",
        "logo": "https://raw.githubusercontent.com/iptv-org/epg/master/sites/tvplus.com.tr/trt-spor-yildiz.png",
        "link": "https://tv-trtsporyildiz.medya.trt.com.tr/master.m3u8"
    },
    {
        "ad": "A Spor HD [1080p]",
        "kategori": "⚽ Spor: Türkiye HD",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/23/A_Spor_logo.png",
        "link": "https://aspor-live.ercdn.net/aspor/aspor.m3u8"
    },
    {
        "ad": "Fenerbahçe TV (FB TV) HD",
        "kategori": "⚽ Spor: Kulüp Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/tr/6/67/FB_TV_logo.png",
        "link": "https://fbtv-live.ercdn.net/fbtv/fbtv.m3u8"
    },
    {
        "ad": "TJK TV HD [1080p]",
        "kategori": "⚽ Spor: Türkiye HD",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/e/e0/TJK_TV_logo.png",
        "link": "https://tjktv-live.ercdn.net/tjktv/tjktv.m3u8"
    },
    {
        "ad": "Sports TV HD",
        "kategori": "⚽ Spor: Türkiye HD",
        "logo": "https://upload.wikimedia.org/wikipedia/tr/2/26/Sports_TV_logo.png",
        "link": "https://sportstv-live.ercdn.net/sportstv/sportstv.m3u8"
    },
    {
        "ad": "Red Bull TV HD [1080p Extreme & Motor]",
        "kategori": "🏎️ Spor: Dünya & Motor Sporları",
        "logo": "https://raw.githubusercontent.com/iptv-org/tv-logos/master/countries/at/red-bull-tv.png",
        "link": "https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8"
    },
    {
        "ad": "FIFA+ Live HD",
        "kategori": "🏎️ Spor: Dünya & Motor Sporları",
        "logo": "https://raw.githubusercontent.com/iptv-org/tv-logos/master/countries/ch/fifa-plus.png",
        "link": "https://fifa-fifaplus-1-eu.rakuten.wurl.tv/playlist.m3u8"
    }
]

def kategori_belirle(kanal_adi):
    adi = kanal_adi.lower()
    if any(k in adi for k in ["spor", "sport", "tjk", "fb tv", "bjk", "gs tv"]):
        return "⚽ Spor: Diğer"
    if any(k in adi for k in ["haber", "news", "ntv", "cnn", "haberturk", "sözcü", "sozcu", "halk tv", "tele1", "tv100", "bloomberg", "tgrt", "ekol"]):
        return "📰 Haber Kanalları"
    if any(k in adi for k in ["trt 1", "trt1", "atv", "kanal d", "show", "star tv", "startv", "now", "fox", "tv8", "teve2", "beyaz tv", "kanal 7", "360"]):
        return "🇹🇷 Ulusal Kanallar (HD)"
    if any(k in adi for k in ["belgesel", "dmax", "tlc", "yaban", "history"]):
        return "🦁 Belgesel & Yaşam"
    if any(k in adi for k in ["çocuk", "cocuk", "minika", "cartoon"]):
        return "🧸 Çocuk & Çizgi Dizi"
    if any(k in adi for k in ["müzik", "muzik", "kral", "power", "dream", "number 1"]):
        return "🎵 Canlı Müzik"
    if any(k in adi for k in ["diyanet", "semerkand", "lalegül", "kuran"]):
        return "🕌 Dini & Kültür"
    return "🏙️ Yerel & Diğer"

# ==========================================
# 2. POWER-SİNEMA FİLM HAVUZU ÇEKİCİ
# ==========================================
def sinema_filmlerini_getir():
    print("[*] Power-Sinema film havuzu çekiliyor...")
    sinema_url = "https://raw.githubusercontent.com/GitLatte/patr0n/refs/heads/site/lists/power-sinema.m3u"
    icerik = url_getir(sinema_url)
    
    if not icerik:
        return []

    filmler = []
    satirlar = icerik.splitlines()
    for i in range(len(satirlar)):
        satir = satirlar[i].strip()
        if satir.startswith("#EXTINF"):
            if i + 1 < len(satirlar):
                link = satirlar[i+1].strip()
                if link.startswith("http"):
                    # Kategori yoksa şık bir film kategorisi ekle
                    if 'group-title="' not in satir:
                        satir = satir.replace("#EXTINF:-1", '#EXTINF:-1 group-title="🎬 Sinema Arşivi"')
                    filmler.append(f"{satir}\n{link}\n")

    print(f"[+] Toplam {len(filmler)} adet film başarıyla çekildi.")
    return filmler

# ==========================================
# 3. MASTER M3U ÜRETİCİ (BİRLEŞTİRME)
# ==========================================
def master_m3u_olustur():
    print("[*] Canlı yayınlar ve filmler birleştiriliyor...")
    
    # 1. Başlık ve EPG
    cikti = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" cache="1000"\n'
    ]

    # 2. HD Spor Kanalları
    cikti.append("\n### ================= ⚽ CANLI SPOR KANALLARI (1080p HD) ================= ###\n")
    for spor in PREMIUM_SPOR_KANALLARI:
        extinf = f'#EXTINF:-1 tvg-logo="{spor["logo"]}" group-title="{spor["kategori"]}",{spor["ad"]}'
        cikti.append(f"{extinf}\n{spor['link']}\n")

    # 3. Ulusal ve Diğer Canlı TV Kanalları
    canli_icerik = url_getir("https://iptv-org.github.io/iptv/countries/tr.m3u")
    if canli_icerik:
        cikti.append("\n### ================= 🇹🇷 ULUSAL VE DİĞER KANALLAR ================= ###\n")
        satirlar = canli_icerik.splitlines()
        for i in range(len(satirlar)):
            satir = satirlar[i].strip()
            if satir.startswith("#EXTINF"):
                if i + 1 < len(satirlar):
                    link = satirlar[i+1].strip()
                    if link.startswith("http"):
                        kanal_adi = satir.split(",")[-1].strip() if "," in satir else "Kanal"
                        if any(x in kanal_adi.lower() for x in ["trt spor", "a spor", "fenerbahçe", "fb tv", "tjk tv"]):
                            continue
                        kategori = kategori_belirle(kanal_adi)
                        if 'group-title="' in satir:
                            satir = re.sub(r'group-title="[^"]*"', f'group-title="{kategori}"', satir)
                        else:
                            satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{kategori}"')
                        cikti.append(f"{satir}\n{link}\n")

    # 4. Power-Sinema Filmleri
    filmler = sinema_filmlerini_getir()
    if filmler:
        cikti.append("\n### ================= 🎬 FİLM VE SİNEMA ARŞİVİ ================= ###\n")
        cikti.extend(filmler)

    # Dosyaya kaydet
    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.writelines(cikti)

    print(f"[🚀] Tamamlandı! Canlı kanallar ve {len(filmler)} film tek bir listede toplandı.")

if __name__ == "__main__":
    master_m3u_olustur()
