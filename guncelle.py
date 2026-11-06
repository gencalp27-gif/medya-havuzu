import urllib.request
import re
import json

# --- 1. CANLI TV KATEGORİLEME ---
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

def canli_kanallari_al():
    print("[*] Canlı TV yayınları çekiliyor...")
    kaynak_url = "https://iptv-org.github.io/iptv/countries/tr.m3u"
    req = urllib.request.Request(kaynak_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            icerik = response.read().decode('utf-8')
    except Exception as e:
        print(f"[-] Canlı TV çekilemedi: {e}")
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

# --- 2. FİLM VE DİZİLER (VOD) ---
def vod_icerikleri_al():
    """
    Film ve dizi içeriklerini tek M3U çatısı altına ekler.
    Buradaki listeyi genişletebilir veya Dizibal scraper'ı ile besleyebilirsin.
    """
    print("[*] Film ve dizi arşivleri hazırlanıyor...")
    vod_listesi = []
    
    # Örnek Filmler (Türkçe Dublaj & Yerli)
    ornek_filmler = [
        {
            "ad": "Gladyatör 2 (2024) [Türkçe Dublaj]",
            "kategori": "🎬 Filmler: Türkçe Dublaj",
            "afis": "https://image.tmdb.org/t/p/w500/2cxhvwyEwRlysAmRH4iodkvo0z5.jpg",
            "link": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" # Test stream linki
        },
        {
            "ad": "Ölümlü Dünya 2 (2023) [Yerli]",
            "kategori": "🎬 Filmler: Yerli Sinema",
            "afis": "https://image.tmdb.org/t/p/w500/kZpUdfm4eB9l28YjP8c1vQ2Z91n.jpg",
            "link": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        }
    ]
    
    # Örnek Diziler (Yerli Platform & Popüler Yapımlar)
    ornek_diziler = [
        {
            "ad": "Gibi - S01 E01 (Kral Midas)",
            "kategori": "🍿 Diziler: Gibi",
            "afis": "https://image.tmdb.org/t/p/w500/bQG9s0G5aY5sYQ78s98yqg3s98s.jpg",
            "link": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        },
        {
            "ad": "Gibi - S01 E02 (Vatana Millete)",
            "kategori": "🍿 Diziler: Gibi",
            "afis": "https://image.tmdb.org/t/p/w500/bQG9s0G5aY5sYQ78s98yqg3s98s.jpg",
            "link": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        },
        {
            "ad": "FROM - S01 E01 (Uzun Gece)",
            "kategori": "🍿 Diziler: FROM",
            "afis": "https://image.tmdb.org/t/p/w500/pRtJagIxpfODzzb0T0NAvZSzErC.webp",
            "link": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        }
    ]
    
    for f in ornek_filmler + ornek_diziler:
        extinf = f'#EXTINF:-1 tvg-logo="{f["afis"]}" group-title="{f["kategori"]}",{f["ad"]}'
        vod_listesi.append({"extinf": extinf, "link": f["link"]})
        
    return vod_listesi

# --- 3. TEK BİR DOSYADA BİRLEŞTİRME ---
def tek_m3u_birlestir():
    kanallar = canli_kanallari_al()
    vodlar = vod_icerikleri_al()
    
    m3u_cikti = '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz"\n\n'
    
    # 1. Kısım: Canlı TV Kanalları
    for k in kanallar:
        m3u_cikti += f"{k['extinf']}\n{k['link']}\n"
        
    # 2. Kısım: Filmler ve Diziler (VOD)
    for v in vodlar:
        m3u_cikti += f"{v['extinf']}\n{v['link']}\n"
        
    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_cikti)
        
    print(f"[+] Başarılı! {len(kanallar)} canlı kanal + {len(vodlar)} film/dizi 'canli_tv.m3u' içine yazıldı.")

if __name__ == "__main__":
    tek_m3u_birlestir()
