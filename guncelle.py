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
        print(f"[-] İndirme hatası: {e}")
        return ""

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

def m3u_guncelle():
    print("[*] Senin verdiğin m3u.ch kaynak linki taranıyor...")
    kaynak_url = "https://m3u.ch/pl/1d84259d4bf3a9832067b3c4be608cbe_6f37cddc89cc539132a35d2ac0248c89.m3u"
    icerik = url_getir(kaynak_url)
    
    if not icerik:
        print("[-] Kaynak indirilemedi, işlem iptal edildi.")
        return

    m3u_satirlari = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" '
        'x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" cache="1000"\n\n'
    ]

    satirlar = icerik.splitlines()
    kanal_sayisi = 0

    for i in range(len(satirlar)):
        satir = satirlar[i].strip()
        if satir.startswith("#EXTINF"):
            if i + 1 < len(satirlar):
                link = satirlar[i+1].strip()
                if link.startswith("http"):
                    kanal_adi = satir.split(",")[-1].strip() if "," in satir else "Kanal"
                    
                    # Eğer listede kendi grubu yoksa otomatik kategori ekle
                    if 'group-title="' not in satir:
                        kat = kategori_belirle(kanal_adi)
                        satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{kat}"')

                    m3u_satirlari.append(f"{satir}\n{link}\n")
                    kanal_sayisi += 1

    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.writelines(m3u_satirlari)

    print(f"[🚀] Başarılı! Toplam {kanal_sayisi} adet canlı kanal 'canli_tv.m3u' dosyasına yazıldı.")

if __name__ == "__main__":
    m3u_guncelle()
