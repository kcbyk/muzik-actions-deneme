"""Find complete public releases, handling rate limits and network errors explicitly."""
import json
import os
import sys
import urllib.error
import urllib.request


def is_ready(tag):
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GH_TOKEN']
    url = f'https://api.github.com/repos/{repo}/releases/tags/{tag}'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
        'User-Agent': 'audio-cache-workflow', 'X-GitHub-Api-Version': '2022-11-28',
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            release = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return False
        raise
    return not release.get('draft', False) and any(
        a.get('name') == 'track.mp3' and a.get('state') == 'uploaded' and a.get('size', 0) > 0
        for a in release.get('assets', [])
    )


if __name__ == '__main__':
    ready = is_ready(os.environ['CACHE_TAG'])
    if '--outputs' in sys.argv:
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write(f'ready={str(ready).lower()}\n')
    else:
        sys.exit(0 if ready else 1)
