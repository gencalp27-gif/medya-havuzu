import urllib.request
import re
import html
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://dizibal.org/'
}

def url_getir(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

# ==========================================
# 1. CANLI TV MOTORU (KATEGORİLİ)
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
    print("[*] Canlı TV yayınları çekiliyor...")
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
    return kanallar

# ==========================================
# 2. DOĞRUDAN OYNATILABİLİR VOD MOTORU (.m3u8)
# ==========================================
def vod_icerikleri_getir():
    print("[*] Filmler ve diziler için oynatılabilir video akışları taranıyor...")
    vodlar = []

    # Dizibal'dan popüler içeriklerin afiş ve başlıklarını çek
    html_data = url_getir("https://dizibal.org/filmler")
    
    # Gerçek çalışan yedek/örnek HLS akış havuzu (Oynatıcının siyah ekranda kalmaması için)
    # Kendi Cloudflare Worker veya Vidmoly linklerini buraya yönlendirebilirsin
    canli_stream_havuzu = [
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
    ]

    sayac = 0
    if html_data:
        # Görsel ve başlık eşleştirmesi
        for match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']+)["\']', html_data):
            afis, baslik = match.group(1), html.unescape(match.group(2).strip())
            if "Film izle" in baslik or len(baslik) > 3:
                temiz_baslik = baslik.replace("Film izle", "").strip()
                if not afis.startswith("http"):
                    afis = "https://dizibal.org" + afis
                
                # Oynatılabilir doğrudan video linki
                video_akisi = canli_stream_havuzu[sayac % len(canli_stream_havuzu)]
                
                extinf = f'#EXTINF:-1 tvg-logo="{afis}" group-title="🎬 Filmler: Vizyon & Popüler",{temiz_baslik}'
                vodlar.append({"extinf": extinf, "link": video_akisi})
                sayac += 1
                if sayac >= 25:
                    break

    # Diziler
    dizi_html = url_getir("https://dizibal.org/diziler")
    dizi_sayac = 0
    if dizi_html:
        for match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']+)["\']', dizi_html):
            afis, baslik = match.group(1), html.unescape(match.group(2).strip())
            if "Dizi izle" in baslik or len(baslik) > 3:
                temiz_baslik = baslik.replace("Dizi izle", "").strip()
                if not afis.startswith("http"):
                    afis = "https://dizibal.org" + afis
                
                video_akisi = canli_stream_havuzu[dizi_sayac % len(canli_stream_havuzu)]
                
                extinf = f'#EXTINF:-1 tvg-logo="{afis}" group-title="🍿 Diziler: Popüler & Yerli",{temiz_baslik} - S01 E01'
                vodlar.append({"extinf": extinf, "link": video_akisi})
                dizi_sayac += 1
                if dizi_sayac >= 20:
                    break

    print(f"[+] {len(vodlar)} adet oynatılabilir VOD içeriği hazırlandı.")
    return vodlar

# ==========================================
# 3. MASTER M3U ÜRETİCİ
# ==========================================
def master_m3u_olustur():
    canli_liste = canli_tv_getir()
    vod_liste = vod_icerikleri_getir()

    cikti = (
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'tvg-shift="0" cache="500"\n\n'
    )

    for k in canli_liste:
        cikti += f"{k['extinf']}\n{k['link']}\n"

    for v in vod_liste:
        cikti += f"{v['extinf']}\n{v['link']}\n"

    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.write(cikti)

    print(f"[🚀] Başarılı! Toplam {len(canli_liste) + len(vod_liste)} adet içerik kaydedildi.")

if __name__ == "__main__":
    master_m3u_olustur()
