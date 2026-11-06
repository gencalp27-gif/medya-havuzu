import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def url_getir(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=25) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[-] Hata ({url}): {e}")
        return ""

# ==========================================
# 1. 1080p SPOR VE ULUSAL KANALLAR
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
# 2. POWER-SİNEMA: ÖZEL "🎬 FİLMLER" AYRIŞTIRICI
# ==========================================
def sinema_filmlerini_hazirla():
    print("[*] Power-Sinema filmleri çekiliyor ve '🎬 Filmler' olarak ayrıştırılıyor...")
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
                    # Varsa mevcut kategoriyi bul
                    kategori_eslesme = re.search(r'group-title="([^"]*)"', satir)
                    if kategori_eslesme and kategori_eslesme.group(1):
                        mevcut_kat = kategori_eslesme.group(1).strip()
                        # Eğer zaten Filmler demiyorsa başına 🎬 Filmler ekle
                        if not mevcut_kat.startswith("🎬"):
                            yeni_kat = f"🎬 Filmler: {mevcut_kat}"
                        else:
                            yeni_kat = mevcut_kat
                        satir = re.sub(r'group-title="[^"]*"', f'group-title="{yeni_kat}"', satir)
                    else:
                        # Kategori hiç yoksa doğrudan 🎬 Filmler yap
                        satir = satir.replace("#EXTINF:-1", '#EXTINF:-1 group-title="🎬 Filmler"')

                    filmler.append(f"{satir}\n{link}\n")

    print(f"[+] Toplam {len(filmler)} film '🎬 Filmler' kategorisiyle ayrıştırıldı.")
    return filmler

# ==========================================
# 3. M3U OLUŞTURMA MOTORU
# ==========================================
def master_m3u_olustur():
    # 1. Filmleri hazırla
    filmler = sinema_filmlerini_hazirla()
    
    # 2. Yalnızca Filmler için ayrı bir M3U oluştur (filmler.m3u)
    if filmler:
        with open("filmler.m3u", "w", encoding="utf-8") as f_film:
            f_film.write('#EXTM3U cache="1000"\n\n')
            f_film.writelines(filmler)
        print("[+] Sadece filmlerden oluşan 'filmler.m3u' dosyası da ayrıca kaydedildi.")

    # 3. Ana Master Liste (canli_tv.m3u - Canlı TV + Filmler)
    ana_liste = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" cache="1000"\n'
    ]

    # Spor Kanalları
    ana_liste.append("\n### ================= ⚽ CANLI SPOR KANALLARI (1080p HD) ================= ###\n")
    for spor in PREMIUM_SPOR_KANALLARI:
        extinf = f'#EXTINF:-1 tvg-logo="{spor["logo"]}" group-title="{spor["kategori"]}",{spor["ad"]}'
        ana_liste.append(f"{extinf}\n{spor['link']}\n")

    # Ulusal ve Diğer TV Kanalları
    canli_icerik = url_getir("https://iptv-org.github.io/iptv/countries/tr.m3u")
    if canli_icerik:
        ana_liste.append("\n### ================= 🇹🇷 ULUSAL VE DİĞER KANALLAR ================= ###\n")
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
                        ana_liste.append(f"{satir}\n{link}\n")

    # Filmler Bölümü (Ayrı Kategori Olarak En Alta Eklenir)
    if filmler:
        ana_liste.append("\n### ================= 🎬 FİLM VE SİNEMA ARŞİVİ ================= ###\n")
        ana_liste.extend(filmler)

    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.writelines(ana_liste)

    print("[🚀] canli_tv.m3u ve filmler.m3u başarıyla güncellendi!")

if __name__ == "__main__":
    master_m3u_olustur()
