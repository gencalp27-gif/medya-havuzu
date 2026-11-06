import urllib.request
import re
import ssl

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
        with urllib.request.urlopen(req, context=ctx, timeout=30) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[-] İndirme hatası ({url}): {e}")
        return ""

# ==============================================================================
# 1. CANLI TV MOTORU (SENİN M3U.CH LİNKİN)
# ==============================================================================
def kategori_belirle(kanal_adi):
    adi = kanal_adi.lower()
    if any(k in adi for k in ["spor", "sport", "tjk", "fb tv", "bjk", "gs tv", "futbol"]):
        return "⚽ Spor Kanalları"
    if any(k in adi for k in ["haber", "news", "ntv", "cnn", "haberturk", "sözcü", "sozcu", "halk tv", "tele1", "tv100", "bloomberg", "tgrt", "ekol"]):
        return "📰 Haber Kanalları"
    if any(k in adi for k in ["trt 1", "trt1", "atv", "kanal d", "show", "star tv", "startv", "now", "fox", "tv8", "teve2", "beyaz tv", "kanal 7", "360"]):
        return "🇹🇷 Ulusal Kanallar (HD)"
    if any(k in adi for k in ["belgesel", "dmax", "tlc", "yaban", "history", "nat geo"]):
        return "🦁 Belgesel & Yaşam"
    if any(k in adi for k in ["çocuk", "cocuk", "minika", "cartoon", "disney"]):
        return "🧸 Çocuk & Çizgi Dizi"
    if any(k in adi for k in ["müzik", "muzik", "kral", "power", "dream", "number 1"]):
        return "🎵 Canlı Müzik"
    if any(k in adi for k in ["diyanet", "semerkand", "lalegül", "kuran"]):
        return "🕌 Dini & Kültür"
    return "🏙️ Genel & Yerel"

def canli_tv_getir():
    print("[*] Senin m3u.ch canlı TV linkin taranıyor...")
    kaynak_url = "https://m3u.ch/pl/1d84259d4bf3a9832067b3c4be608cbe_6f37cddc89cc539132a35d2ac0248c89.m3u"
    icerik = url_getir(kaynak_url)
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
                    if 'group-title="' not in satir:
                        kat = kategori_belirle(kanal_adi)
                        satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{kat}"')
                    kanallar.append(f"{satir}\n{link}\n")

    print(f"[+] {len(kanallar)} adet canlı kanal hazırlandı.")
    return kanallar

# ==============================================================================
# 2. DEV FİLM VE DİZİ ARŞİVİ MOTORU (VOD)
# ==============================================================================
def film_ve_dizi_arsivini_getir():
    print("[*] Yüzlerce film ve diziden oluşan arşiv çekiliyor...")
    sinema_kaynak_url = "https://raw.githubusercontent.com/GitLatte/patr0n/refs/heads/site/lists/power-sinema.m3u"
    icerik = url_getir(sinema_kaynak_url)
    
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
                        satir = satir.replace("#EXTINF:-1", '#EXTINF:-1 group-title="🎬 Filmler: Sinema"')

                    filmler.append(f"{satir}\n{link}\n")

    print(f"[+] {len(filmler)} adet film ve dizi kütüphaneye eklendi.")
    return filmler

# ==============================================================================
# 3. MASTER M3U ÜRETİCİ (HEPSİ TEK LİSTEDE)
# ==============================================================================
def master_m3u_olustur():
    canli_kanallar = canli_tv_getir()
    filmler = film_ve_dizi_arsivini_getir()

    ana_liste = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" cache="1000"\n\n'
    ]

    # 1. Bölüm: Canlı TV Kanalları
    ana_liste.append("### ================= 📺 CANLI TV KANALLARI ================= ###\n")
    ana_liste.extend(canli_kanallar)

    # 2. Bölüm: Filmler ve Sinema Arşivi
    if filmler:
        ana_liste.append("\n### ================= 🎬 FİLM VE DİZİ ARŞİVİ ================= ###\n")
        ana_liste.extend(filmler)

    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.writelines(ana_liste)

    print(f"[🚀] Başarılı! {len(canli_kanallar)} Canlı Kanal + {len(filmler)} Film tek bir dosyada ('canli_tv.m3u') birleştirildi.")

if __name__ == "__main__":
    master_m3u_olustur()
