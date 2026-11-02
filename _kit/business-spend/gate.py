"""Email-code gate (founder, 2026-11-02).

Gated sections stay in the HTML, so search engines and AI crawlers read the whole case study and the page still reads
in full without JavaScript. The page script locks them for visitors until a 6-digit code sent to their email is
confirmed (form labels research-code and research-verify in /docs/HMM_Forms_AppsScript.gs). Every gated element
carries class="bs-gated", the selector the Article JSON-LD names in hasPart.

Kinds: "block" (a section shown as a short faded preview with an unlock card under it) and "detail" (a closed
"More detail" disclosure, replaced by an unlock button while locked).
"""
import json
import os
from html import escape as _esc

import model

E = lambda s: _esc(s, quote=True)
FORMS_URL = 'https://script.google.com/macros/s/AKfycbzeefYKM_xZuJHIg9pjl0hTLo57v87Qfpb5DzwvikeyVY3_QdYHFd18zpzlfBsbALSp/exec'
TURNSTILE_SITEKEY = '0x4AAAAAAFKhXJ31AZeh2wp1'
SELECTOR = '.bs-gated'
ON = True          # set by build.render: off for the fixed edition snapshot


def copy():
    with open(os.path.join(model.KIT, 'narrative.json'), encoding='utf-8') as f:
        return json.load(f)['gate']


LOCK_ICON = ('<svg class="bs-gate-ic" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="2"/><circle cx="12" cy="16" r="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>')


def block(kind, html):
    """A gated section with its unlock card. `kind` is a key of gate.cards (opps, audience, downloads)."""
    if not ON:
        return html
    g = copy()
    cd = g['cards'][kind]
    return ('<div class="bs-gated" data-gate="block" data-gate-kind="%s">%s</div>'
            '<div class="bs-gate-card" data-gate-card><p class="bs-gate-t">%s%s</p><p class="bs-gate-x">%s</p>'
            '<button type="button" class="btn btn-primary bs-gate-btn" data-gate-open>%s</button></div>'
            % (kind, html, LOCK_ICON, E(cd['title']), E(cd['text']), E(g['button'])))


def detail(html):
    """A gated "More detail" disclosure: while locked, a button that opens the unlock dialog stands in its place."""
    if not ON or not html:
        return html
    g = copy()
    return ('<div class="bs-gated" data-gate="detail">%s</div><div class="bs-gate-card is-inline" data-gate-card>'
            '<button type="button" class="bs-gate-more" data-gate-open>%s%s</button></div>' % (html, LOCK_ICON, E(g['cards']['detail']['button'])))


def dialog():
    """The one unlock dialog, outside the tab panels so every card can open it."""
    if not ON:
        return ''
    g = copy()
    er = g['errors']
    msgs = ''.join(' data-err-%s="%s"' % (k.replace('_', '-'), E(v)) for k, v in er.items())
    return ('<dialog class="bs-gate" id="bs-gate" aria-labelledby="bs-gate-h">'
            '<form class="bs-gate-form" id="bs-gate-form" novalidate data-endpoint="%s" data-turnstile-sitekey="%s" data-research="%s"'
            ' data-sending="%s" data-checking="%s" data-code-sent="%s"%s>'
            '<h2 id="bs-gate-h">%s%s</h2>'
            '<div class="bs-gate-step" data-step="email"><p class="bs-gate-lead">%s</p>'
            '<label for="bs-gate-email">%s</label><input type="email" id="bs-gate-email" name="email" autocomplete="email" inputmode="email" required>'
            '<div class="hp-field" aria-hidden="true"><label for="bs-gate-hp">Leave this field blank</label><input type="text" id="bs-gate-hp" name="hmm_trap" tabindex="-1" autocomplete="off" data-lpignore="true" data-1p-ignore></div>'
            '<div class="cf-slot" id="bs-gate-ts"></div>'
            '<button type="submit" class="btn btn-primary" data-gate-send>%s</button></div>'
            '<div class="bs-gate-step" data-step="code" hidden><p class="bs-gate-lead" data-gate-sent></p>'
            '<label for="bs-gate-code">%s</label><input type="text" id="bs-gate-code" name="code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6">'
            '<button type="button" class="btn btn-primary" data-gate-verify>%s</button>'
            '<p class="bs-gate-alt"><button type="button" class="bs-gate-link" data-gate-resend>%s</button><button type="button" class="bs-gate-link" data-gate-change>%s</button></p></div>'
            '<p class="bs-gate-err" role="alert" data-gate-err></p>'
            '<p class="bs-gate-fine">%s <a href="/privacy">%s</a></p></form>'
            '<button type="button" class="bs-gate-close" data-gate-close>%s</button></dialog>'
            % (FORMS_URL, TURNSTILE_SITEKEY, E(g['research']), E(g['sending']), E(g['checking']), E(g['code_sent']), msgs,
               LOCK_ICON, E(g['title']), E(g['body']), E(g['email_label']), E(g['send']), E(g['code_label']), E(g['verify']),
               E(g['resend']), E(g['change']), E(g['fine']), E(g['privacy']), E(g['close'])))


def jsonld_parts():
    """Google's paywalled-content markup: the gated parts are named, so a locked view is not treated as cloaking."""
    if not ON:
        return {}
    return {'isAccessibleForFree': False,
            'hasPart': {'@type': 'WebPageElement', 'isAccessibleForFree': False, 'cssSelector': SELECTOR}}
