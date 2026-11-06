import urllib.request
import re

def kategori_belirle(kanal_adi):
    adi = kanal_adi.lower()
    
    # Spor
    if any(k in adi for k in ["spor", "sport", "tjk", "fb tv", "bjk", "gs tv", "futbol"]):
        return "⚽ Spor"
    
    # Haber
    if any(k in adi for k in ["haber", "news", "ntv", "cnn", "haberturk", "sözcü", "sozcu", "halk tv", "tele1", "tv100", "bloomberg", "tgrt", "ekol", "bengü"]):
        return "📰 Haber"
        
    # Çocuk
    if any(k in adi for k in ["çocuk", "cocuk", "minika", "cartoon", "disney", "bebe"]):
        return "🧸 Çocuk"
        
    # Belgesel & Yaşam
    if any(k in adi for k in ["belgesel", "dmax", "tlc", "yaban", "history", "nat geo", "geography"]):
        return "🦁 Belgesel & Yaşam"
        
    # Müzik
    if any(k in adi for k in ["müzik", "muzik", "kral", "power", "dream", "number 1", "nr1"]):
        return "🎵 Müzik"
        
    # Dini
    if any(k in adi for k in ["diyanet", "semerkand", "lalegül", "lalegul", "rehber", "hilal", "kuran"]):
        return "🕌 Dini & Kültür"
        
    # Ulusal
    if any(k in adi for k in ["trt 1", "trt1", "atv", "kanal d", "show", "star tv", "startv", "now tv", "now", "fox", "tv8", "teve2", "beyaz tv", "kanal 7", "360"]):
        return "🇹🇷 Ulusal Kanallar"
        
    # Geriye kalanlar
    return "🏙️ Yerel & Diğer"

def m3u_olustur():
    print("[*] Kanallar çekiliyor ve kategorize ediliyor...")
    kaynak_url = "https://iptv-org.github.io/iptv/countries/tr.m3u"
    
    req = urllib.request.Request(kaynak_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        icerik = response.read().decode('utf-8')
    
    kanallar = []
    satirlar = icerik.splitlines()
    
    for i in range(len(satirlar)):
        satir = satirlar[i].strip()
        if satir.startswith("#EXTINF"):
            if i + 1 < len(satirlar):
                link = satirlar[i+1].strip()
                if link.startswith("http"):
                    # Kanal adını ayıkla (, işaretinden sonrası)
                    kanal_adi = satir.split(",")[-1].strip() if "," in satir else "Bilinmeyen Kanal"
                    
                    kategori = kategori_belirle(kanal_adi)
                    
                    # group-title etiketini güncelle veya ekle
                    if 'group-title="' in satir:
                        yeni_satir = re.sub(r'group-title="[^"]*"', f'group-title="{kategori}"', satir)
                    else:
                        yeni_satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{kategori}"')
                    
                    kanallar.append({
                        "kategori": kategori,
                        "ad": kanal_adi,
                        "extinf": yeni_satir,
                        "link": link
                    })
    
    # Kategorileri öncelik sırasına göre diz
    oncelik = {
        "🇹🇷 Ulusal Kanallar": 1,
        "📰 Haber": 2,
        "⚽ Spor": 3,
        "🦁 Belgesel & Yaşam": 4,
        "🧸 Çocuk": 5,
        "🎵 Müzik": 6,
        "🕌 Dini & Kültür": 7,
        "🏙️ Yerel & Diğer": 8
    }
    
    kanallar.sort(key=lambda k: (oncelik.get(k["kategori"], 9), k["ad"]))
    
    # M3U içeriğini hazırla
    m3u_cikti = '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz"\n\n'
    for k in kanallar:
        m3u_cikti += f"{k['extinf']}\n{k['link']}\n"
    
    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_cikti)
        
    print(f"[+] Toplam {len(kanallar)} kanal kategorize edildi ve kaydedildi!")

if __name__ == "__main__":
    m3u_olustur()
