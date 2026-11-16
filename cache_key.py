"""Validate requests and derive a stable public-cache tag without storing queries."""
import hashlib
import os
import uuid
from urllib.parse import urlparse

MAX_QUERY = 180


def request_details():
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
        source = 'ytsearch1:' + query
    digest = hashlib.sha256(query.encode('utf-8')).hexdigest()
    # Test tones have a separate namespace and can never become real song hits.
    prefix = 'test-song-' if os.environ.get('TEST_MODE', '').lower() == 'true' else 'song-'
    return request_id, source, prefix + digest


if __name__ == '__main__':
    _, _, tag = request_details()
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write(f'tag={tag}\n')
