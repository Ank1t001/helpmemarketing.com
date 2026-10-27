#!/usr/bin/env python3
"""Public image derivatives for the Instagram content view (edition 001).

  python3 -I social_images.py SCREENSHOTS_DIR

Each derivative is a crop of one sanitised post screenshot from the private evidence package. The crop keeps
the post as Instagram showed it (media, the account header with any paid-partnership label, and the caption)
and leaves out the page around it. The one change inside the crop: the row of like, comment and share counts
is covered with the panel's own background colour, so the image does not invite a comparison of displayed
counts (the study does not compare them). The original screenshot is never modified; the derivative is a new
WebP file under /assets/index/business-spend/social/. The script prints each file's provenance for
social_narrative.json and refuses if a source screenshot's hash differs from the one recorded in social.json.
"""
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw

KIT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(KIT))
OUT_DIR = os.path.join(ROOT, 'assets', 'index', 'business-spend', 'social')

# post id: (source screenshot, crop box (left, top, right, bottom), counts row to cover (left, top, right, bottom) in source pixels, output name)
SPECS = {
    'airwallex-ig-Dcrv-4rhQEc': ('airwallex-post-2026-08-30-Dcrv-4rhQEc.png', (412, 31, 1085, 631), (758, 503, 1078, 539), 'airwallex-thejoshvfx-2026-08-30.webp'),
    'airwallex-ig-Db8jAJeDQ5J': ('airwallex-post-2026-08-12-Db8jAJeDQ5J.png', (341, 31, 1156, 631), (828, 503, 1150, 539), 'airwallex-sf30-2026-08-12.webp'),
}
SANITISATION = ('The collector hid the viewer\'s navigation, avatar, notifications, messages, comment box, comments and commenter names before capture. '
                'In this derivative the row of like, comment and share counts is covered with the panel\'s background colour; nothing else in the crop is changed.')


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    with open(os.path.join(KIT, 'social.json'), encoding='utf-8') as f:
        posts = {p['id']: p for p in json.load(f)['posts']}
    os.makedirs(OUT_DIR, exist_ok=True)
    out = {}
    for pid, (src, box, cover, name) in SPECS.items():
        p = posts[pid]
        path = os.path.join(argv[1], src)
        if src != p['capture_ref'] or sha(path) != p['capture_sha256']:
            raise SystemExit('Refused: %s does not match the capture recorded for %s' % (src, pid))
        im = Image.open(path).convert('RGB')
        bg = im.getpixel((cover[0] + 4, cover[1] - 4))
        work = im.copy()
        ImageDraw.Draw(work).rectangle(cover, fill=bg)
        crop = work.crop(box)
        dest = os.path.join(OUT_DIR, name)
        crop.save(dest, 'WEBP', quality=82, method=6)
        out[pid] = {'src': '/assets/index/business-spend/social/' + name, 'width': crop.width, 'height': crop.height,
                    'from': src, 'from_sha256': p['capture_sha256'], 'crop': list(box), 'covered': list(cover),
                    'sanitisation': SANITISATION, 'sha256': sha(dest)}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
