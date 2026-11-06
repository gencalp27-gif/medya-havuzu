import urllib.request
import re
import ssl
from concurrent.futures import ThreadPoolExecutor

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
        print(f"[-] Kaynak indirilemedi ({url}): {e}")
        return ""

def link_calisiyor_mu(kanal):
    """Bozuk ve ölü sunucuları eler"""
    link = kanal["link"]
    if "162.212.179.32" in link:
        return None
    try:
        req = urllib.request.Request(link, headers=HEADERS, method="GET")
        with urllib.request.urlopen(req, context=ctx, timeout=4) as res:
            if res.status in [200, 206, 301, 302]:
                return kanal
    except Exception:
        return None
    return None

# ==============================================================================
# 1. %100 AÇILAN GARANTİLİ FULL HD ULUSAL VE SPOR KANALLARI
# ==============================================================================
GARANTILI_KANALLAR = [
    {
        "ad": "TRT 1 HD [1080p]",
        "kategori": "🇹🇷 Ulusal Kanallar",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/8/85/TRT_1_logo_%282021-%29.svg",
        "link": "https://tv-trt1.medya.trt.com.tr/master.m3u8"
    },
    {
        "ad": "TRT Spor HD [1080p]",
        "kategori": "⚽ Spor Kanalları",
        "logo": "https://raw.githubusercontent.com/iptv-org/epg/master/sites/tvplus.com.tr/trt-spor.png",
        "link": "https://tv-trtsporyildiz.medya.trt.com.tr/master.m3u8"
    },
    {
        "ad": "A Spor HD [1080p]",
        "kategori": "⚽ Spor Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/23/A_Spor_logo.png",
        "link": "https://aspor-live.ercdn.net/aspor/aspor.m3u8"
    },
    {
        "ad": "Fenerbahçe TV (FB TV) HD",
        "kategori": "⚽ Spor Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/tr/6/67/FB_TV_logo.png",
        "link": "https://fbtv-live.ercdn.net/fbtv/fbtv.m3u8"
    },
    {
        "ad": "TJK TV HD",
        "kategori": "⚽ Spor Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/e/e0/TJK_TV_logo.png",
        "link": "https://tjktv-live.ercdn.net/tjktv/tjktv.m3u8"
    },
    {
        "ad": "Sports TV HD",
        "kategori": "⚽ Spor Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/tr/2/26/Sports_TV_logo.png",
        "link": "https://sportstv-live.ercdn.net/sportstv/sportstv.m3u8"
    },
    {
        "ad": "TRT Haber HD",
        "kategori": "📰 Haber Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/7/72/TRT_Haber_logo_%282020-present%29.svg",
        "link": "https://tv-trthaber.medya.trt.com.tr/master.m3u8"
    },
    {
        "ad": "NTV HD",
        "kategori": "📰 Haber Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/b/b5/NTV_logo.png",
        "link": "https://dogus-live.daioncdn.net/ntv/ntv.m3u8"
    },
    {
        "ad": "CNN Türk HD",
        "kategori": "📰 Haber Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/4/4e/CNN_T%C3%BCrk_logo.svg",
        "link": "https://ca242648.fastcdn.com/cnnturk/live.m3u8"
    },
    {
        "ad": "Habertürk HD",
        "kategori": "📰 Haber Kanalları",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/1/18/Habert%C3%BCrk_TV_logo.png",
        "link": "https://haberturktv-live.ercdn.net/haberturktv/haberturktv.m3u8"
    },
    {
        "ad": "TRT Belgesel HD",
        "kategori": "🦁 Belgesel & Yaşam",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/0/07/TRT_Belgesel_logo_%282019%29.png",
        "link": "https://tv-trtbelgesel.medya.trt.com.tr/master.m3u8"
    },
    {
        "ad": "DMAX HD",
        "kategori": "🦁 Belgesel & Yaşam",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/23/DMAX_logo.svg",
        "link": "https://dogus-live.daioncdn.net/dmax/dmax.m3u8"
    },
    {
        "ad": "TLC HD",
        "kategori": "🦁 Belgesel & Yaşam",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/7/74/TLC_Logo.svg",
        "link": "https://dogus-live.daioncdn.net/tlc/tlc.m3u8"
    },
    {
        "ad": "TRT Çocuk HD",
        "kategori": "🧸 Çocuk & Çizgi Dizi",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/e/e6/TRT_%C3%87ocuk_logo_%282021%29.svg",
        "link": "https://tv-trtcocuk.medya.trt.com.tr/master.m3u8"
    }
]

def kategori_belirle(kanal_adi):
    adi = kanal_adi.lower()
    if any(k in adi for k in ["spor", "sport", "tjk", "fb tv", "bjk", "gs tv"]):
        return "⚽ Spor Kanalları"
    if any(k in adi for k in ["haber", "news", "ntv", "cnn", "haberturk", "sözcü", "sozcu", "halk tv", "tele1", "tv100", "bloomberg", "tgrt"]):
        return "📰 Haber Kanalları"
    if any(k in adi for k in ["trt", "atv", "kanal d", "show", "star", "now", "fox", "tv8", "teve2", "beyaz", "kanal 7"]):
        return "🇹🇷 Ulusal Kanallar"
    if any(k in adi for k in ["belgesel", "dmax", "tlc", "yaban"]):
        return "🦁 Belgesel & Yaşam"
    if any(k in adi for k in ["çocuk", "cocuk", "minika", "cartoon"]):
        return "🧸 Çocuk & Çizgi Dizi"
    return "🏙️ Genel & Yerel"

# ==============================================================================
# 2. M3U.CH CANLI TV TARAMA (KIRIK LİNK KORUMALI)
# ==============================================================================
def m3uch_saglam_kanallari_getir():
    print("[*] m3u.ch taranıyor ve ölü linkler temizleniyor...")
    kaynak_url = "https://m3u.ch/pl/1d84259d4bf3a9832067b3c4be608cbe_6f37cddc89cc539132a35d2ac0248c89.m3u"
    icerik = url_getir(kaynak_url)
    if not icerik:
        return []

    aday_kanallar = []
    satirlar = icerik.splitlines()
    for i in range(len(satirlar)):
        satir = satirlar[i].strip()
        if satir.startswith("#EXTINF") and i + 1 < len(satirlar):
            link = satirlar[i+1].strip()
            if link.startswith("http") and "162.212.179.32" not in link:
                kanal_adi = satir.split(",")[-1].strip() if "," in satir else "Kanal"
                if 'group-title="' not in satir:
                    kat = kategori_belirle(kanal_adi)
                    satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{kat}"')
                aday_kanallar.append({"extinf": satir, "link": link})

    calisanlar = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        sonuclar = executor.map(link_calisiyor_mu, aday_kanallar[:150])
        for s in sonuclar:
            if s:
                calisanlar.append(f"{s['extinf']}\n{s['link']}\n")

    print(f"[+] {len(calisanlar)} adet çalışan canlı kanal eklendi.")
    return calisanlar

# ==============================================================================
# 3. TÜM FİLM VE DİZİ ARŞİVLERİNİ TOPLAMA MOTORU
# ==============================================================================
def tum_film_ve_dizileri_getir():
    print("[*] Tüm Türkçe film ve dizi arşivleri çekiliyor...")
    
    # Açık M3U Film ve Dizi Havuzları
    vod_kaynaklari = [
        "https://raw.githubusercontent.com/GitLatte/patr0n/refs/heads/site/lists/power-sinema.m3u"
    ]
    
    vod_listesi = []
    
    for url in vod_kaynaklari:
        icerik = url_getir(url)
        if not icerik:
            continue
            
        satirlar = icerik.splitlines()
        for i in range(len(satirlar)):
            satir = satirlar[i].strip()
            if satir.startswith("#EXTINF") and i + 1 < len(satirlar):
                link = satirlar[i+1].strip()
                if link.startswith("http") and "162.212.179.32" not in link:
                    baslik = satir.split(",")[-1].strip() if "," in satir else "İçerik"
                    
                    # Sezon/Bölüm geçiyorsa Dizi, geçmiyorsa Film klasörüne ayır
                    if any(x in baslik.lower() for x in ["sezon", "bölüm", "bolum", "s0", "s1", "e0", "dizi"]):
                        yeni_grup = "🍿 Diziler"
                    else:
                        kategori_bul = re.search(r'group-title="([^"]*)"', satir)
                        if kategori_bul and kategori_bul.group(1):
                            mevcut = kategori_bul.group(1).strip()
                            yeni_grup = mevcut if mevcut.startswith("🎬") else f"🎬 Filmler: {mevcut}"
                        else:
                            yeni_grup = "🎬 Filmler: Sinema"
                            
                    if 'group-title="' in satir:
                        satir = re.sub(r'group-title="[^"]*"', f'group-title="{yeni_grup}"', satir)
                    else:
                        satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{yeni_grup}"')
                        
                    vod_listesi.append(f"{satir}\n{link}\n")

    print(f"[+] Toplam {len(vod_listesi)} adet film ve dizi hazırlandı!")
    return vod_listesi

# ==============================================================================
# 4. MASTER M3U BİRLEŞTİRİCİ
# ==============================================================================
def master_m3u_olustur():
    canli_kanallar = m3uch_saglam_kanallari_getir()
    vod_arsivi = tum_film_ve_dizileri_getir()

    # Bağımsız film/dizi dosyası (filmler.m3u)
    if vod_arsivi:
        with open("filmler.m3u", "w", encoding="utf-8") as f_vod:
            f_vod.write('#EXTM3U cache="1000"\n\n')
            f_vod.writelines(vod_arsivi)

    # Ana birleşik dosya (canli_tv.m3u)
    ana_liste = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" cache="1000"\n\n'
    ]

    # 1. Garantili 1080p Kanallar
    ana_liste.append("### ================= ⭐ GARANTİLİ FULL HD KANALLAR ================= ###\n")
    for k in GARANTILI_KANALLAR:
        extinf = f'#EXTINF:-1 tvg-logo="{k["logo"]}" group-title="{k["kategori"]}",{k["ad"]}'
        ana_liste.append(f"{extinf}\n{k['link']}\n")

    # 2. Test Edilmiş Canlı Kanallar
    if canli_kanallar:
        ana_liste.append("\n### ================= 📺 CANLI TV KANALLARI ================= ###\n")
        ana_liste.extend(canli_kanallar)

    # 3. Tüm Film ve Dizi Arşivi
    if vod_arsivi:
        ana_liste.append("\n### ================= 🎬 TÜM FİLM VE DİZİLER ================= ###\n")
        ana_liste.extend(vod_arsivi)

    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.writelines(ana_liste)

    print(f"[🚀] Tamamlandı! Garantili TV + {len(canli_kanallar)} Canlı Kanal + {len(vod_arsivi)} Film/Dizi tek listede!")

if __name__ == "__main__":
    master_m3u_olustur()
