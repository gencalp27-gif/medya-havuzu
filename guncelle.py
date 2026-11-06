import urllib.request
import urllib.parse
import re
import html
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9'
}

def guvenli_url(url):
    """URL içindeki Türkçe karakterleri ve boşlukları temizler (Çökmeyi önler)"""
    try:
        parcalar = urllib.parse.urlsplit(url.strip())
        yol = urllib.parse.quote(parcalar.path, safe="/%&=:+-._~")
        sorgu = urllib.parse.quote(parcalar.query, safe="/?&=:+-,._~")
        return urllib.parse.urlunsplit((parcalar.scheme, parcalar.netloc, yol, sorgu, parcalar.fragment))
    except Exception:
        return url

def url_getir(url, referer=None, timeout=8):
    try:
        temiz_url = guvenli_url(url)
        h = HEADERS.copy()
        if referer:
            h['Referer'] = referer
        req = urllib.request.Request(temiz_url, headers=h)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[-] Atlandı ({url[:40]}...): {e}")
        return ""

# ==============================================================================
# 1. CANLI TV MOTORU (SENİN M3U.CH LİNKİN)
# ==============================================================================
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

def canli_tv_getir():
    print("[*] m3u.ch canlı TV kanalları çekiliyor...")
    kaynak_url = "https://m3u.ch/pl/1d84259d4bf3a9832067b3c4be608cbe_6f37cddc89cc539132a35d2ac0248c89.m3u"
    icerik = url_getir(kaynak_url, timeout=20)
    if not icerik:
        return []

    kanallar = []
    satirlar = icerik.splitlines()
    for i in range(len(satirlar)):
        satir = satirlar[i].strip()
        if satir.startswith("#EXTINF") and i + 1 < len(satirlar):
            link = satirlar[i+1].strip()
            # VLC'de hata verdiren ölü sunucuyu filtrele
            if link.startswith("http") and "162.212.179.32" not in link:
                kanal_adi = satir.split(",")[-1].strip() if "," in satir else "Kanal"
                if 'group-title="' not in satir:
                    kat = kategori_belirle(kanal_adi)
                    satir = satir.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{kat}"')
                kanallar.append(f"{satir}\n{link}\n")

    print(f"[+] {len(kanallar)} adet canlı TV kanalı hazırlandı.")
    return kanallar

# ==============================================================================
# 2. MANITUX NUVIO PLUGINS MOTORU (HATA KORUMALI)
# ==============================================================================
def manitux_provider_domain_bul(provider_id, varsayilan_domain):
    try:
        js_url = f"https://raw.githubusercontent.com/manitux-app/nuvi-test-plugins/main/providers/{provider_id}.js"
        js_kod = url_getir(js_url, timeout=6)
        if js_kod:
            eslesme = re.search(r'https?://[a-zA-Z0-9.-]+\.[a-z]{2,6}', js_kod)
            if eslesme and "github" not in eslesme.group(0) and "google" not in eslesme.group(0):
                return eslesme.group(0).rstrip("/")
    except Exception:
        pass
    return varsayilan_domain

def sayfadan_m3u8_cikar(sayfa_url, ana_domain):
    try:
        detay_html = url_getir(sayfa_url, referer=ana_domain, timeout=5)
        if not detay_html:
            return None

        dogrudan = re.search(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', detay_html)
        if dogrudan:
            return dogrudan.group(1)

        iframeler = re.findall(r'<iframe[^>]+(?:src|data-src)=["\']([^"\']+)["\']', detay_html)
        for iframe in iframeler[:2]:
            if iframe.startswith("//"):
                iframe = "https:" + iframe
            elif iframe.startswith("/"):
                iframe = ana_domain + iframe
            if any(x in iframe for x in ["youtube.com", "google.com", "facebook"]):
                continue
            
            iframe_html = url_getir(iframe, referer=sayfa_url, timeout=4)
            m3u8_bul = re.search(r'["\'](https?://[^"\']+\.(?:m3u8|mp4)[^"\']*)["\']', iframe_html)
            if m3u8_bul:
                return m3u8_bul.group(1)
    except Exception:
        pass
    return None

def manitux_katalog_tara():
    print("[*] Manitux Nuvio Plugins kaynakları taranıyor...")
    vod_listesi = []

    kaynaklar = [
        {
            "id": "dizibal",
            "ad": "DiziBal",
            "domain": "https://dizibal.org",
            "sayfalar": [
                ("/filmler", "🎬 Filmler: DiziBal Yeni"),
                ("/diziler", "🍿 Diziler: DiziBal Popüler")
            ]
        },
        {
            "id": "hdfilmcehennemi",
            "ad": "HDFilmCehennemi",
            "domain": "https://www.hdfilmcehennemi.nl",
            "sayfalar": [
                ("/", "🎬 Filmler: HDFilmCehennemi")
            ]
        },
        {
            "id": "filmmakinesi",
            "ad": "FilmMakinesi",
            "domain": "https://filmmakinesi.to",
            "sayfalar": [
                ("/film-izle/", "🎬 Filmler: FilmMakinesi")
            ]
        },
        {
            "id": "filmekseni",
            "ad": "FilmEkseni",
            "domain": "https://filmekseni.vip",
            "sayfalar": [
                ("/", "🎬 Filmler: FilmEkseni")
            ]
        },
        {
            "id": "diziyou",
            "ad": "DiziYou",
            "domain": "https://diziyou.one",
            "sayfalar": [
                ("/", "🍿 Diziler: DiziYou")
            ]
        }
    ]

    for k in kaynaklar:
        try:
            guncel_domain = manitux_provider_domain_bul(k["id"], k["domain"])
            print(f" -> {k['ad']} kontrol ediliyor ({guncel_domain})...")

            for yol, kategori_adi in k["sayfalar"]:
                html_icerik = url_getir(guncel_domain + yol, referer=guncel_domain, timeout=7)
                if not html_icerik:
                    continue

                kartlar = re.findall(
                    r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?<img[^>]+(?:src|data-src)=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']+)["\']',
                    html_icerik, re.DOTALL | re.IGNORECASE
                )

                sayac = 0
                for link, afis, baslik in kartlar:
                    temiz_baslik = html.unescape(baslik).replace("izle", "").replace("Film", "").replace("Dizi", "").strip()
                    if len(temiz_baslik) < 2:
                        continue

                    if not link.startswith("http"):
                        link = guncel_domain + ("/" if not link.startswith("/") else "") + link
                    if not afis.startswith("http"):
                        afis = guncel_domain + ("/" if not afis.startswith("/") else "") + afis

                    stream_url = sayfadan_m3u8_cikar(link, guncel_domain) or link

                    extinf = f'#EXTINF:-1 tvg-logo="{afis}" group-title="{kategori_adi}",{temiz_baslik}'
                    vod_listesi.append(f"{extinf}\n{stream_url}\n")
                    
                    sayac += 1
                    if sayac >= 12:
                        break
        except Exception as e:
            print(f"[-] {k['ad']} atlandı: {e}")

    print(f"[+] Manitux kaynaklarından toplam {len(vod_listesi)} içerik çekildi.")
    return vod_listesi

# ==============================================================================
# 3. MASTER M3U BİRLEŞTİRİCİ
# ==============================================================================
def master_m3u_olustur():
    canli_kanallar = canli_tv_getir()
    manitux_vod = manitux_katalog_tara()

    if manitux_vod:
        with open("filmler.m3u", "w", encoding="utf-8") as f_vod:
            f_vod.write('#EXTM3U cache="1000"\n\n')
            f_vod.writelines(manitux_vod)

    ana_liste = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz" cache="1000"\n\n'
    ]

    ana_liste.append("### ================= 📺 CANLI TV KANALLARI ================= ###\n")
    ana_liste.extend(canli_kanallar)

    if manitux_vod:
        ana_liste.append("\n### ================= 🎬 MANITUX FİLM VE DİZİLER ================= ###\n")
        ana_liste.extend(manitux_vod)

    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.writelines(ana_liste)

    print(f"[🚀] Bitti! {len(canli_kanallar)} Canlı Kanal + {len(manitux_vod)} VOD kaydedildi.")

if __name__ == "__main__":
    try:
        master_m3u_olustur()
    except Exception as genel_hata:
        print(f"Genel hata yakalandı: {genel_hata}")
