import urllib.request

def m3u_olustur():
    print("[*] Güncel yayınlar çekiliyor...")
    kaynak_url = "https://iptv-org.github.io/iptv/countries/tr.m3u"
    
    req = urllib.request.Request(kaynak_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        icerik = response.read().decode('utf-8')
    
    # EPG (Yayın akışı) başlığı
    m3u_cikti = '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz"\n\n'
    
    satirlar = icerik.splitlines()
    for i in range(len(satirlar)):
        satir = satirlar[i].strip()
        if satir.startswith("#EXTINF"):
            if i + 1 < len(satirlar):
                link = satirlar[i+1].strip()
                if link.startswith("http"):
                    m3u_cikti += f"{satir}\n{link}\n"
    
    with open("canli_tv.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_cikti)
        
    print("[+] canli_tv.m3u başarıyla güncellendi!")

if __name__ == "__main__":
    m3u_olustur()
