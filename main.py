"""Yalnızca indirme/dönüştürme izniniz olan içeriklerde kullanın."""
import os
from pathlib import Path
import subprocess
import sys
import uuid
from urllib.parse import urlparse

import imageio_ffmpeg

MAX_QUERY = 180
MAX_BYTES = 80 * 1024 * 1024
MAX_SECONDS = 600


def validated_input():
    raw_id = os.environ.get('REQUEST_ID', '')
    try:
        request_id = str(uuid.UUID(raw_id, version=4))
    except (ValueError, AttributeError):
        raise ValueError('REQUEST_ID geçerli bir UUID v4 olmalı')
    if request_id != raw_id.lower():
        raise ValueError('REQUEST_ID kanonik UUID v4 biçiminde olmalı')
    query = os.environ.get('SEARCH_QUERY', '').strip()
    if not query or len(query) > MAX_QUERY or any(ord(ch) < 32 for ch in query):
        raise ValueError('Arama terimi boş, çok uzun veya geçersiz')
    if '://' in query:
        u = urlparse(query)
        allowed = {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be'}
        if u.scheme != 'https' or u.hostname not in allowed or u.username or u.password or u.port not in (None, 443):
            raise ValueError('Yalnızca HTTPS YouTube bağlantıları kabul edilir')
        if u.hostname == 'youtu.be' and not u.path.strip('/'):
            raise ValueError('Video kimliği eksik')
        source = query
    else:
        # Arama ilk sonucu seçer; bunun doğru veya izinli içerik olduğunu garanti etmez.
        source = 'ytsearch1:' + query
    return request_id, source


def run(args, timeout):
    subprocess.run(args, check=True, timeout=timeout)


def main():
    _, source = validated_input()
    out = Path('output')
    out.mkdir(exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if os.environ.get('TEST_MODE', '').lower() == 'true':
        # İzin gerektiren bir üçüncü taraf kaynağına erişmeden hattı doğrula.
        run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi',
             '-i', 'sine=frequency=440:duration=3', '-c:a', 'libmp3lame',
             '-b:a', '128k', str(out / 'track.mp3')], timeout=30)
        print('YouTube yerine üretilmiş test tonu kullanıldı.')
        return
    # Ayrı argümanlar kullanılır; sorgu shell komutu olarak çalıştırılmaz.
    # Bilinmeyen süreli veya 10 dakikadan uzun videolar reddedilir.
    run([
        sys.executable, '-m', 'yt_dlp', '--no-playlist', '--no-progress',
        '--no-cache-dir', '--restrict-filenames', '--max-filesize', str(MAX_BYTES),
        '--match-filter', f'duration > 0 & duration <= {MAX_SECONDS}',
        '-f', 'bestaudio/best', '-o', str(out / 'source.%(ext)s'), '--', source,
    ], timeout=600)
    candidates = [p for p in out.glob('source.*') if p.is_file() and not p.name.endswith(('.part', '.ytdl'))]
    if len(candidates) != 1 or candidates[0].stat().st_size > MAX_BYTES:
        raise RuntimeError('İzinli boyutta tek bir kaynak dosya oluşturulamadı')
    run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(candidates[0]),
         '-vn', '-map_metadata', '-1', '-t', str(MAX_SECONDS), '-c:a', 'libmp3lame',
         '-b:a', '128k', str(out / 'track.mp3')], timeout=300)
    if not (out / 'track.mp3').is_file() or (out / 'track.mp3').stat().st_size == 0:
        raise RuntimeError('MP3 oluşturulamadı')
    candidates[0].unlink()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f'İşlem başarısız: {exc}', file=sys.stderr)
        sys.exit(1)
