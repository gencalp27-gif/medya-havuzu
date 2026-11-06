import urllib.request
import re
import html
import ssl

# SSL Sertifika uyarılarını aşmak için context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
}

def url_getir(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[-] Hata ({url}): {e}")
        return ""

# ==========================================
# 1. CANLI TV MOTORU
# ==========================================
def kategori_belirle(kanal_adi):
    adi = kanal_adi.lower()
    if any(k in adi for k in ["spor", "sport", "tjk", "fb tv", "bjk", "gs tv", "futbol"]):
        return "⚽ Spor"
    if any(k in adi for k in ["haber", "news", "ntv", "cnn", "haberturk", "sözcü", "sozcu", "halk tv", "tele1", "tv100", "bloomberg", "tgrt", "ekol", "bengü"]):
        return "📰 Haber"
    if any(k in adi for k in ["çocuk", "cocuk", "minika", "cartoon", "disney", "bebe"]):
        return "🧸 Çocuk"
    if any(k in adi for k in ["belgesel", "dmax", "tlc", "yaban", "history", "nat geo"]):
        return "🦁 Belgesel & Yaşam"
    if any(k in adi for k in ["müzik", "muzik", "kral", "power", "dream", "number 1", "nr1"]):
        return "🎵 Müzik"
    if any(k in adi for k in ["diyanet", "semerkand", "lalegül", "lalegul", "rehber", "hilal", "kuran"]):
        return "🕌 Dini & Kültür"
    if any(k in adi for k in ["trt 1", "trt1", "atv", "kanal d", "show", "star tv", "startv", "now tv", "now", "fox", "tv8", "teve2", "beyaz tv", "kanal 7", "360"]):
        return "🇹🇷 Ulusal Kanallar"
    return "🏙️ Yerel & Diğer"

def canli_tv_getir():
    print("[*] Canlı TV havuzu taranıyor...")
    icerik = url_getir("https://iptv-org.github.io/iptv/countries/tr.m3u")
    if not icerik:
        return []

    kanallar = []
    satirlar = icerik.splitlines()
    for i in range(len(satirlar)):
        satir = satirlar[i].strip()
        if satir.startswith("#EXTINF"):
            if i + 1 < len(satirlar):
                link = satirlar[i+1].strip()
                if link.startswith("http"):
                    kanal_adi = satir.split(",")[-1].strip() if "," in satir else "Kanal"
                    kategori = kategori_belirle(kanal_adi)
                    if 'group-title="' in satir:
                        yeni_satir = re.sub(r'group-title="[^"]*"', f'group-title="{kategori}"', satir)
                    else:
                        yeni_satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{kategori}"')
                    kanallar.append({"extinf": yeni_satir, "link": link, "kategori": kategori, "ad": kanal_adi})

    oncelik = {
        "🇹🇷 Ulusal Kanallar": 1, "📰 Haber": 2, "⚽ Spor": 3,
        "🦁 Belgesel & Yaşam": 4, "🧸 Çocuk": 5, "🎵 Müzik": 6,
        "🕌 Dini & Kültür": 7, "🏙️ Yerel & Diğer": 8
    }
    kanallar.sort(key=lambda k: (oncelik.get(k["kategori"], 9), k["ad"]))
    print(f"[+] {len(kanallar)} adet canlı TV kanalı hazırlandı.")
    return kanallar

# ==========================================
# 2. DİZİBAL DİNAMİK VOD (FİLM & DİZİ) MOTORU
# ==========================================
def dizibal_icerik_tara():
    print("[*] Dizibal ana sayfası ve güncel arşiv taranıyor...")
    html_data = url_getir("https://dizibal.org/")
    vodlar = []
    
    if not html_data:
        return vodlar

    # Kartları yakalamak için düzenli ifadeler
    # Başlık, yıl, puan, afiş ve link ayıklama
    bloklar = re.findall(r'<a[^>]+href=["\'](/series/[^"\']+|/film/[^"\']+|/movie/[^"\']+|/[^"\']+)["\'][^>]*>(.*?)</a>', html_data, re.DOTALL)
    
    # Trend ve son eklenen film/dizi regex taraması
    kart_deseni = re.compile(
        r'<a[^>]+href=["\'](?P<link>[^"\']+)["\'][^>]*>.*?'
        r'<img[^>]+(?:src|data-src)=["\'](?P<afis>[^"\']+)["\'].*?'
        r'(?:<h[2-4][^>]*>|title=["\'])(?P<baslik>[^<"\']+).*?'
        r'</a>', re.DOTALL | re.IGNORECASE
    )

    eklenen_sayisi = 0
    
    # 1. Bölüm: Filmler
    filmler_html = url_getir("https://dizibal.org/filmler")
    if filmler_html:
        for match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']+)["\']', filmler_html):
            afis, baslik = match.group(1), html.unescape(match.group(2).strip())
            if "Film izle" in baslik or len(baslik) > 3:
                temiz_baslik = baslik.replace("Film izle", "").strip()
                if not afis.startswith("http"):
                    afis = "https://dizibal.org" + afis
                extinf = f'#EXTINF:-1 tvg-logo="{afis}" group-title="🎬 Filmler: Vizyon & Popüler",{temiz_baslik}'
                # Oynatıcı linki (Dizibal yönlendirmesi)
                yayin_linki = "https://dizibal.org/filmler"
                vodlar.append({"extinf": extinf, "link": yayin_linki})
                eklenen_sayisi += 1
                if eklenen_sayisi >= 40:  # İlk 40 popüler film
                    break

    # 2. Bölüm: Diziler
    diziler_html = url_getir("https://dizibal.org/diziler")
    dizi_sayisi = 0
    if diziler_html:
        for match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']+)["\']', diziler_html):
            afis, baslik = match.group(1), html.unescape(match.group(2).strip())
            if "Dizi izle" in baslik or len(baslik) > 3:
                temiz_baslik = baslik.replace("Dizi izle", "").strip()
                if not afis.startswith("http"):
                    afis = "https://dizibal.org" + afis
                extinf = f'#EXTINF:-1 tvg-logo="{afis}" group-title="🍿 Diziler: Popüler & Yerli",{temiz_baslik}'
                yayin_linki = "https://dizibal.org/diziler"
                vodlar.append({"extinf": extinf, "link": yayin_linki})
                dizi_sayisi += 1
                if dizi_sayisi >= 30:  # İlk 30 popüler dizi
                    break

    print(f"[+] {eklenen_sayisi} film ve {dizi_sayisi} dizi dinamik olarak çekildi.")
    return vodlar

# ==========================================
# 3. MASTER M3U ÜRETİCİ
# ==========================================
def master_m3u_olustur():
    canli_liste = canli_tv_getir()
    vod_liste = dizibal_icerik_tara()

    # Profesyonel IPTV Başlığı (EPG + Logo + Cache Ayarları)
    cikti = (
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'tvg-shift="0" cache="500"\n\n'
    )

    # 1. Canlı TV Bölümü
    cikti += "### ----------------- CANLI TELEVIZYON YAYINLARI ----------------- ###\n\n"
    for k in canli_liste:
        cikti += f"{k['extinf']}\n{k['link']}\n"

    # 2. VOD (Film & Dizi) Bölümü
    if vod_liste:
        cikti += "\n### ----------------- FILM VE DIZI ARSIVI (VOD) ----------------- ###\n\n"
        for v in vod_liste:
            cikti += f"{v['extinf']}\n{v['link']}\n"

    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.write(cikti)

    print(f"[🚀] Başarılı! Toplam {len(canli_liste) + len(vod_liste)} adet içerik tek listede kaydedildi.")

if __name__ == "__main__":
    master_m3u_olustur()
