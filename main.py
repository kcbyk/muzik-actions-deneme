"""Yalnızca indirme/dönüştürme izniniz olan içeriklerde kullanın."""
import os
from pathlib import Path
import subprocess
import sys

import imageio_ffmpeg
from cache_key import request_details

MAX_BYTES = 80 * 1024 * 1024
MAX_SECONDS = 600


def run(args, timeout):
    subprocess.run(args, check=True, timeout=timeout)


def main():
    _, source, _ = request_details()
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
