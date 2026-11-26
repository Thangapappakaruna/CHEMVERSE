import re

from django import template
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()

ICONS = {
    'home': '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    'dashboard': '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
    'book': '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
    'table': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    'flask': '<path d="M9 3h6"/><path d="M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2h12.4a1.5 1.5 0 0 0 1.3-2L14 9V3"/><path d="M7 15h10"/>',
    'hexagon': '<path d="M12 2 20.5 7v10L12 22 3.5 17V7z"/><circle cx="12" cy="12" r="2.5"/>',
    'atom': '<circle cx="12" cy="12" r="1.5"/><ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/>',
    'zap': '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    'scale': '<path d="M12 3v18M5 21h14M3 7h18"/><path d="m6 7-3 7a3 3 0 0 0 6 0z"/><path d="m18 7-3 7a3 3 0 0 0 6 0z"/>',
    'gamepad': '<rect x="2" y="7" width="20" height="11" rx="5"/><path d="M7 10.5v4M5 12.5h4"/><circle cx="15.5" cy="11.5" r="1"/><circle cx="18" cy="14" r="1"/>',
    'help': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7v.5"/><path d="M12 17h.01"/>',
    'calculator': '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01M16 15h.01M8 19h.01M12 19h4"/>',
    'beaker': '<path d="M5 3h14"/><path d="M6 3v15a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V3"/><path d="M6 12h12"/>',
    'dictionary': '<path d="M4 4h11a3 3 0 0 1 3 3v14H7a3 3 0 0 1-3-3z"/><path d="m8 15 2.5-7 2.5 7M9 12.5h3"/>',
    'users': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6 6 0 0 1 3.5 6"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'thermo': '<path d="M14 14.8V5a2 2 0 0 0-4 0v9.8a4 4 0 1 0 4 0z"/>',
    'trophy': '<path d="M8 21h8M12 17v4"/><path d="M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 6h3v2a3 3 0 0 1-3 3M7 6H4v2a3 3 0 0 0 3 3"/>',
    'star': '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3l-5.6 2.9 1.1-6.2L3 9.6l6.2-.9z"/>',
    'heart': '<path d="M12 20s-7-4.4-9.2-8.7A5 5 0 0 1 12 6a5 5 0 0 1 9.2 5.3C19 15.6 12 20 12 20z"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'check': '<path d="m5 12 5 5 9-10"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'trash': '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    'edit': '<path d="M4 20h4L19 9l-4-4L4 16z"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    'lock': '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    'logout': '<path d="M15 4h4v16h-4M10 17l5-5-5-5M15 12H3"/>',
    'download': '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
    'message': '<path d="M4 5h16v11H8l-4 4z"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'sparkles': '<path d="m12 3 1.8 4.7 4.7 1.8-4.7 1.8L12 16l-1.8-4.7-4.7-1.8 4.7-1.8z"/><path d="m19 15 .8 2.2 2.2.8-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
    'fire': '<path d="M12 22a7 7 0 0 0 7-7c0-4-3-6-4-9-1 2-2 3-4 3 0-2-1-4-1-6-3 2-5 6-5 12a7 7 0 0 0 7 7z"/>',
    'chart': '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    'list': '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    'alert': '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    'history': '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
    'bookmark': '<path d="M6 3h12v18l-6-4-6 4z"/>',
}


@register.simple_tag
def icon(name, size=18, cls=''):
    body = ICONS.get(name, ICONS['atom'])
    return mark_safe(
        f'<svg class="ic {escape(cls)}" width="{int(size)}" height="{int(size)}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


@register.filter
def chem(value):
    """H2SO4 -> H<sub>2</sub>SO<sub>4</sub>; leading coefficients stay normal size; '->' becomes an arrow."""
    raw = str(value if value is not None else '')
    out, prev = [], ''
    for i, part in enumerate(re.split(r'(\d+)', raw)):
        if i % 2 == 1 and prev and (prev.isalpha() or prev in ')]'):
            out.append(f'<sub>{part}</sub>')
        else:
            out.append(escape(part))
        if part:
            prev = part[-1]
    return mark_safe(''.join(out).replace('-&gt;', '→'))


@register.filter
def temp(value, note=''):
    """Format a temperature in °C, or 'Not available'."""
    if value is None or value == '':
        return mark_safe('<span class="text-secondary">Not available</span>')
    return format_html('{} °C', f'{value:g}' if isinstance(value, float) else value)


@register.filter
def safe_json(value):
    """JSON-encode a value for use inside an HTML attribute."""
    import json
    return escape(json.dumps(value))


@register.filter
def get_item(d, key):
    try:
        return d.get(key)
    except AttributeError:
        return None
