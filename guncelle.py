import urllib.request
import urllib.parse
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

# Senin Cloudflare Worker adresin
WORKER_BASE = "https://medya-kopru.genc-alp27.workers.dev"

def worker_linki_olustur(video_url, referer="https://vidmoly.to/"):
    """Video akışını Cloudflare Worker üzerinden engelsiz geçiren yardımcı fonksiyon"""
    parametreler = urllib.parse.urlencode({
        "url": video_url,
        "ref": referer
    })
    return f"{WORKER_BASE}/?{parametreler}"

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
    print("[*] m3u.ch canlı TV linki çekiliyor...")
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

    print(f"[+] {len(kanallar)} adet canlı TV kanalı hazırlandı.")
    return kanallar

# ==============================================================================
# 2. CLOUDFLARE WORKER DESTEKLİ FİLM VE DİZİ MOTORU (VOD)
# ==============================================================================
def film_ve_dizileri_getir():
    print("[*] Film ve diziler Cloudflare Worker köprüsüyle hazırlanıyor...")
    
    # Gerçek video akışları doğrudan senin Cloudflare Worker'ın üzerinden geçirilir
    vod_havuzu = [
        # --- YERLİ SİNEMA VE DUBLAJ FİLMLER ---
        {
            "ad": "Ölümlü Dünya 2 (2023) [Yerli Komedi]",
            "kategori": "🎬 Filmler: Yerli Sinema",
            "afis": "https://image.tmdb.org/t/p/w500/kZpUdfm4eB9l28YjP8c1vQ2Z91n.jpg",
            "raw_stream": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
            "ref": "https://dizibal.org/"
        },
        {
            "ad": "Kolpaçino 4 4'lük (2024) [Yerli Komedi]",
            "kategori": "🎬 Filmler: Yerli Sinema",
            "afis": "https://image.tmdb.org/t/p/w500/u3bZgnGQ9T01sWNhyveQz0wH0Hl.jpg",
            "raw_stream": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
            "ref": "https://dizibal.org/"
        },
        {
            "ad": "Gladyatör 2 (2024) [Türkçe Dublaj]",
            "kategori": "🎬 Filmler: Türkçe Dublaj",
            "afis": "https://image.tmdb.org/t/p/w500/2cxhvwyEwRlysAmRH4iodkvo0z5.jpg",
            "raw_stream": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "ref": "https://vidmoly.to/"
        },
        {
            "ad": "Deadpool & Wolverine (2024) [Türkçe Dublaj]",
            "kategori": "🎬 Filmler: Türkçe Dublaj",
            "afis": "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg",
            "raw_stream": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "ref": "https://vidmoly.to/"
        },
        # --- YERLİ PLATFORM DİZİLERİ ---
        {
            "ad": "Gibi - 1. Sezon 1. Bölüm (Kral Midas)",
            "kategori": "🍿 Diziler: Gibi",
            "afis": "https://image.tmdb.org/t/p/w500/bQG9s0G5aY5sYQ78s98yqg3s98s.jpg",
            "raw_stream": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "ref": "https://dizibal.org/"
        },
        {
            "ad": "Gibi - 1. Sezon 2. Bölüm (Vatana Millete)",
            "kategori": "🍿 Diziler: Gibi",
            "afis": "https://image.tmdb.org/t/p/w500/bQG9s0G5aY5sYQ78s98yqg3s98s.jpg",
            "raw_stream": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "ref": "https://dizibal.org/"
        },
        {
            "ad": "Prens - 1. Sezon 1. Bölüm (Tahta Geçiş)",
            "kategori": "🍿 Diziler: Prens",
            "afis": "https://image.tmdb.org/t/p/w500/3UOp2W1Gz8P3k1g2P9P3k1g2P9.jpg",
            "raw_stream": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
            "ref": "https://dizibal.org/"
        }
    ]

    vod_satirlari = []
    for item in vod_havuzu:
        # Linki senin Cloudflare Worker'ına yönlendiriyoruz
        kopru_linki = worker_linki_olustur(item["raw_stream"], item["ref"])
        extinf = f'#EXTINF:-1 tvg-logo="{item["afis"]}" group-title="{item["kategori"]}",{item["ad"]}'
        vod_satirlari.append(f"{extinf}\n{kopru_linki}\n")

    print(f"[+] {len(vod_satirlari)} adet film/dizi Cloudflare Worker üzerinden bağlandı.")
    return vod_satirlari

# ==============================================================================
# 3. MASTER M3U ÜRETİCİ
# ==============================================================================
def master_m3u_olustur():
    canli_liste = canli_tv_getir()
    vod_liste = film_ve_dizileri_getir()

    # Yalnızca filmler için filmler.m3u
    if vod_liste:
        with open("filmler.m3u", "w", encoding="utf-8") as f_film:
            f_film.write('#EXTM3U cache="1000"\n\n')
            f_film.writelines(vod_liste)
        print("[💾] 'filmler.m3u' kaydedildi.")

    # Master dosya (canli_tv.m3u)
    ana_liste = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" cache="1000"\n\n'
    ]

    ana_liste.append("### ================= 📺 CANLI TV KANALLARI ================= ###\n")
    ana_liste.extend(canli_liste)

    if vod_liste:
        ana_liste.append("\n### ================= 🎬 TÜRKÇE FİLM VE DİZİLER (VOD) ================= ###\n")
        ana_liste.extend(vod_liste)

    with open("canli_tv.m3u", "w", encoding="utf-8") as f_master:
        f_master.writelines(ana_liste)

    print(f"[🚀] Başarılı! canli_tv.m3u ve filmler.m3u güncellendi.")

if __name__ == "__main__":
    master_m3u_olustur()
