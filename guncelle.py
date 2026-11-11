
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import concurrent.futures
import ipaddress
import json
import os
import re
import socket
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "kaynaklar.json"

TIMEOUT = 12
MAX_BYTES = 15 * 1024 * 1024
MAX_WORKERS = 8

USER_AGENT = "MedyaHavuzu/3.0"
MEDIA_EXTENSIONS = (
    ".m3u8", ".mp4", ".webm", ".mkv", ".ts", ".mpd"
)

ATTRIBUTE_PATTERN = re.compile(
    r'([\w-]+)="([^"]*)"'
)

EPISODE_PATTERN = re.compile(
    r"S(\d{1,2})\s*E(\d{1,3})|"
    r"(\d{1,2})\.\s*[Ss]ezon.{0,25}?"
    r"(\d{1,3})\.\s*[Bb]ölüm",
    re.IGNORECASE
)


def safe_url(url):
    url = str(url or "").strip()
    parsed = urllib.parse.urlsplit(url)

    if parsed.scheme not in ("https", "http"):
        return ""

    if not parsed.hostname:
        return ""

    if parsed.username or parsed.password:
        return ""

    try:
        host = parsed.hostname
        addresses = socket.getaddrinfo(
            host, None, type=socket.SOCK_STREAM
        )
        for entry in addresses:
            ip = ipaddress.ip_address(entry[4][0])
            if not ip.is_global:
                return ""
    except (OSError, ValueError):
        return ""

    return url


def download(url, limit=MAX_BYTES):
    if not safe_url(url):
        raise ValueError("Güvenli olmayan adres")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    with urllib.request.urlopen(
        request, timeout=TIMEOUT
    ) as response:
        if response.status != 200:
            raise RuntimeError(
                f"HTTP {response.status}"
            )

        data = response.read(limit + 1)

        if len(data) > limit:
            raise RuntimeError(
                "Kaynak boyut sınırını aştı"
            )

        return data


def is_turkish(name, group, language):
    value = (
        f"{name} {group} {language}"
    ).casefold()

    keywords = [
        "türkçe", "turkce", "turkish",
        "yerli", "dublaj", "altyazı",
        "altyazi", "tr-tr"
    ]

    if any(word in value for word in keywords):
        return True

    return bool(
        re.search(r"(?<![a-z])tr(?![a-z])", value)
    )


def detect_type(name, group, preferred):
    if preferred in ("film", "dizi"):
        return preferred

    text = f"{name} {group}".casefold()

    if EPISODE_PATTERN.search(name):
        return "dizi"

    if any(word in text for word in [
        "dizi", "series", "episode", "sezon"
    ]):
        return "dizi"

    return "film"


def parse_playlist(content, source):
    if not content.lstrip("\ufeff \n\r").startswith(
        "#EXTM3U"
    ):
        raise ValueError("Geçersiz M3U dosyası")

    results = []
    current = None

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("#EXTINF:"):
            attributes = dict(
                ATTRIBUTE_PATTERN.findall(line)
            )

            name = (
                line.split(",", 1)[1].strip()
                if "," in line else ""
            )

            current = (name, attributes)
            continue

        if not line or line.startswith("#"):
            continue

        if current is None:
            continue

        name, attributes = current
        current = None

        url = safe_url(line)

        if not url or not name:
            continue

        group = attributes.get("group-title", "")
        language = attributes.get(
            "tvg-language",
            source.get("dil", "")
        )

        kind = detect_type(
            name,
            group,
            source.get("tur", "otomatik")
        )

        if source.get("yalniz_turkce", True):
            if not is_turkish(name, group, language):
                continue

        if kind == "dizi":
            if source.get("bolum_zorunlu", True):
                if not EPISODE_PATTERN.search(name):
                    continue

        if not group:
            group = (
                "Türkçe Diziler"
                if kind == "dizi"
                else "Türkçe Filmler"
            )

        results.append({
            "name": name,
            "url": url,
            "type": kind,
            "group": group,
            "language": language,
            "logo": attributes.get("tvg-logo", ""),
            "id": attributes.get("tvg-id", "")
        })

    return results


def verify_stream(item):
    url = item["url"]
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path.lower()

    if not path.endswith(MEDIA_EXTENSIONS):
        return False

    headers = {"User-Agent": USER_AGENT}

    if path.endswith((".mp4", ".webm", ".mkv", ".ts")):
        headers["Range"] = "bytes=0-2047"

    try:
        request = urllib.request.Request(
            url, headers=headers
        )

        with urllib.request.urlopen(
            request, timeout=TIMEOUT
        ) as response:
            if response.status not in (200, 206):
                return False

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            data = response.read(4096)

            if "text/html" in content_type:
                return False

            if b"<html" in data.lower():
                return False

            if path.endswith(".m3u8"):
                return data.lstrip().startswith(
                    b"#EXTM3U"
                )

            if path.endswith(".mpd"):
                return b"<MPD" in data

            return bool(data)

    except Exception as error:
        print(
            f"Yayın kontrol hatası: "
            f"{item['name']}: {error}"
        )
        return False


def sanitize(value):
    return re.sub(
        r'[\r\n"]', " ", str(value)
    ).strip()


def make_entry(item):
    name = sanitize(item["name"])
    group = sanitize(item["group"])
    logo = sanitize(item["logo"])
    language = sanitize(item["language"])
    tvg_id = sanitize(item["id"])

    return (
        f'#EXTINF:-1 tvg-id="{tvg_id}" '
        f'tvg-logo="{logo}" '
        f'tvg-language="{language}" '
        f'group-title="{group}",{name}\n'
        f'{item["url"]}\n'
    )


def atomic_write(path, content):
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=ROOT,
        delete=False
    ) as temporary:
        temporary.write(content)
        temporary_path = temporary.name

    os.replace(temporary_path, path)


def save_playlist(filename, items):
    if not items:
        print(
            f"{filename}: Yeni geçerli kayıt yok. "
            "Eski dosya korunuyor."
        )
        return

    content = "#EXTM3U\n"
    content += "".join(
        make_entry(item) for item in items
    )

    atomic_write(ROOT / filename, content)

    print(
        f"{filename}: {len(items)} kayıt yazıldı."
    )


def create_combined_playlist():
    sections = []

    for filename in (
        "canli_tv.m3u",
        "filmler.m3u",
        "diziler.m3u"
    ):
        path = ROOT / filename

        if not path.exists():
            continue

        content = path.read_text(
            encoding="utf-8-sig",
            errors="replace"
        )

        if not content.lstrip().startswith("#EXTM3U"):
            continue

        lines = content.splitlines()

        sections.extend(
            line for line in lines[1:]
        )

    if sections:
        atomic_write(
            ROOT / "tum_icerikler.m3u",
            "#EXTM3U\n"
            + "\n".join(sections)
            + "\n"
        )


def main():
    print("Medya Havuzu V3 başlatıldı.")

    if not CONFIG.exists():
        raise FileNotFoundError(
            "kaynaklar.json bulunamadı"
        )

    config = json.loads(
        CONFIG.read_text(encoding="utf-8")
    )

    sources = [
        source
        for source in config.get("kaynaklar", [])
        if source.get("aktif", False)
    ]

    all_items = {}
    errors = []

    for source in sources:
        name = source.get("ad", "Bilinmeyen")
        url = source.get("url", "")

        try:
            print(f"Kaynak taranıyor: {name}")

            data = download(url)

            content = data.decode(
                "utf-8-sig", errors="replace"
            )

            items = parse_playlist(
                content, source
            )

            for item in items:
                key = (
                    item["type"],
                    item["url"]
                )
                all_items[key] = item

            print(
                f"{name}: {len(items)} aday bulundu."
            )

        except Exception as error:
            errors.append({
                "kaynak": name,
                "hata": str(error)
            })

            print(
                f"Kaynak hatası: {name}: {error}"
            )

    valid = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:
        futures = {
            executor.submit(verify_stream, item): item
            for item in all_items.values()
        }

        for future in concurrent.futures.as_completed(
            futures
        ):
            item = futures[future]

            try:
                if future.result():
                    valid.append(item)
            except Exception as error:
                print(error)

    valid.sort(
        key=lambda item: (
            item["type"],
            item["group"].casefold(),
            item["name"].casefold()
        )
    )

    films = [
        item for item in valid
        if item["type"] == "film"
    ]

    series = [
        item for item in valid
        if item["type"] == "dizi"
    ]

    save_playlist("filmler.m3u", films)
    save_playlist("diziler.m3u", series)

    create_combined_playlist()

    report = {
        "surum": "3.0",
        "kaynak_sayisi": len(sources),
        "aday_sayisi": len(all_items),
        "dogrulanan_filmler": len(films),
        "dogrulanan_diziler": len(series),
        "hatalar": errors
    }

    atomic_write(
        ROOT / "durum.json",
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2
        ) + "\n"
    )

    print(json.dumps(
        report,
        ensure_ascii=False,
        indent=2
    ))


if __name__ == "__main__":
    main()
