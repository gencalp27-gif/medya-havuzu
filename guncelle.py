import urllib.request
import re
import ssl
import html

# SSL Doğrulama Ayarları
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

def url_getir(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=25) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[-] İndirme hatası ({url}): {e}")
        return ""

# ==============================================================================
# 1. 1080p FULL HD SPOR VE ÖZEL KANALLAR
# ==============================================================================
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
        "ad": "Red Bull TV HD [1080p - Extreme & Motor]",
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

# ==============================================================================
# 2. CANLI TV VE KANAL HAVUZU
# ==============================================================================
def canli_kanallari_topla():
    print("[*] Canlı TV ve spor yayınları derleniyor...")
    kanallar = []
    
    # 1. Öncelikli 1080p Spor Kanalları
    for spor in PREMIUM_SPOR_KANALLARI:
        extinf = f'#EXTINF:-1 tvg-logo="{spor["logo"]}" group-title="{spor["kategori"]}",{spor["ad"]}'
        kanallar.append(f"{extinf}\n{spor['link']}\n")

    # 2. Türkiye Açık Yayın Havuzu
    acik_yayinlar = url_getir("https://iptv-org.github.io/iptv/countries/tr.m3u")
    if acik_yayinlar:
        satirlar = acik_yayinlar.splitlines()
        for i in range(len(satirlar)):
            satir = satirlar[i].strip()
            if satir.startswith("#EXTINF"):
                if i + 1 < len(satirlar):
                    link = satirlar[i+1].strip()
                    if link.startswith("http"):
                        kanal_adi = satir.split(",")[-1].strip() if "," in satir else "Kanal"
                        # Mükerrer ana spor kanallarını atla
                        if any(x in kanal_adi.lower() for x in ["trt spor", "a spor", "fenerbahçe", "fb tv", "tjk tv"]):
                            continue
                        kategori = kategori_belirle(kanal_adi)
                        if 'group-title="' in satir:
                            satir = re.sub(r'group-title="[^"]*"', f'group-title="{kategori}"', satir)
                        else:
                            satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{kategori}"')
                        kanallar.append(f"{satir}\n{link}\n")

    print(f"[+] Toplam {len(kanallar)} canlı kanal hazırlandı.")
    return kanallar

# ==============================================================================
# 3. FİLM VE SİNEMA HAVUZU (CVNFLIX & POWERSİNEMA MOTORU)
# ==============================================================================
def sinema_filmlerini_topla():
    print("[*] Türkçe film ve sinema arşivi taranıyor...")
    # IMDb kimlikli ve Türkçe dublaj/altyazılı doğrulanmış film havuzu
    film_kaynak_url = "https://raw.githubusercontent.com/GitLatte/patr0n/refs/heads/site/lists/power-sinema.m3u"
    icerik = url_getir(film_kaynak_url)
    
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
                    # Kategori adını düzenle ve "🎬 Filmler" başlığı altına al
                    kategori_bul = re.search(r'group-title="([^"]*)"', satir)
                    if kategori_bul and kategori_bul.group(1):
                        kat = kategori_bul.group(1).strip()
                        if not kat.startswith("🎬"):
                            yeni_kat = f"🎬 Filmler: {kat}"
                        else:
                            yeni_kat = kat
                        satir = re.sub(r'group-title="[^"]*"', f'group-title="{yeni_kat}"', satir)
                    else:
                        satir = satir.replace("#EXTINF:-1", '#EXTINF:-1 group-title="🎬 Filmler"')

                    filmler.append(f"{satir}\n{link}\n")

    print(f"[+] Toplam {len(filmler)} film '🎬 Filmler' kategorisiyle hazırlandı.")
    return filmler

# ==============================================================================
# 4. MASTER PLAYLIST ÜRETİCİSİ (BİRLEŞTİRME VE ÇİFT ÇIKTI)
# ==============================================================================
def master_m3u_olustur():
    canli_kanallar = canli_kanallari_topla()
    filmler = sinema_filmlerini_topla()

    # --- 1. ÇIKTI: filmler.m3u (Yalnızca Sinema Filmleri) ---
    if filmler:
        with open("filmler.m3u", "w", encoding="utf-8") as f_out:
            f_out.write('#EXTM3U cache="1000"\n\n')
            f_out.writelines(filmler)
        print("[💾] 'filmler.m3u' bağımsız olarak kaydedildi.")

    # --- 2. ÇIKTI: canli_tv.m3u (Tüm Canlı Kanallar + Filmler) ---
    ana_liste = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" cache="1000"\n\n'
    ]
    
    # Canlı TV Bölümü
    ana_liste.append("### ================= 📺 CANLI TV VE SPOR KANALLARI ================= ###\n")
    ana_liste.extend(canli_kanallar)

    # Filmler Bölümü
    if filmler:
        ana_liste.append("\n### ================= 🎬 TÜRKÇE FİLM VE SİNEMA ARŞİVİ ================= ###\n")
        ana_liste.extend(filmler)

    with open("canli_tv.m3u", "w", encoding="utf-8") as f_master:
        f_master.writelines(ana_liste)

    print(f"[🚀] 'canli_tv.m3u' başarıyla kaydedildi! (Toplam içerik: {len(canli_kanallar) + len(filmler)})")

if __name__ == "__main__":
    master_m3u_olustur()
