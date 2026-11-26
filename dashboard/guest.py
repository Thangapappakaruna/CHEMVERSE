"""Guest mode: visitors can use every tool without signing in.

Their progress is kept in the session (for this browser visit only) so the guest
dashboard can show it. Signing in keeps progress permanently in the database.
"""
from django.utils import timezone

KEY = 'guest'
MAX_ITEMS = 30


def _data(request):
    data = request.session.get(KEY)
    if not isinstance(data, dict):
        data = {'quiz': [], 'games': {}, 'lessons': [], 'experiments': [], 'activity': []}
    for k, default in (('quiz', []), ('games', {}), ('lessons', []), ('experiments', []), ('activity', [])):
        data.setdefault(k, default)
    return data


def _save(request, data):
    request.session[KEY] = data
    request.session.modified = True


def log(request, kind, label, url=''):
    data = _data(request)
    data['activity'].insert(0, {'kind': kind, 'label': str(label)[:200], 'url': url, 'at': timezone.now().isoformat()})
    del data['activity'][MAX_ITEMS:]
    _save(request, data)


def add_quiz(request, category, score, total, percent):
    data = _data(request)
    data['quiz'].append({'category': category or 'Mixed', 'score': score, 'total': total, 'percent': percent,
                         'at': timezone.now().strftime('%d %b %H:%M')})
    del data['quiz'][:-MAX_ITEMS]
    _save(request, data)
    log(request, 'quiz', f'Quiz {category or "Mixed"}: {score}/{total} ({percent}%)', '/quiz/')


def add_game(request, slug, title, points):
    """Stores the total points per game. Returns the guest's best single score for that game."""
    data = _data(request)
    g = data['games'].setdefault(slug, {'title': title, 'total': 0, 'best': 0, 'plays': 0})
    g['total'] += points
    g['plays'] += 1
    g['best'] = max(g['best'], points)
    _save(request, data)
    log(request, 'game', f'{title}: {points} points', f'/games/{slug}/')
    return g['best']


def complete_lesson(request, slug, title):
    data = _data(request)
    if slug in data['lessons']:
        return False
    data['lessons'].append(slug)
    _save(request, data)
    log(request, 'lesson', f'Completed lesson: {title}', f'/learn/{slug}/')
    return True


def add_experiment(request, title, result):
    data = _data(request)
    data['experiments'].insert(0, {'title': title, 'result': result[:250]})
    del data['experiments'][MAX_ITEMS:]
    _save(request, data)
    log(request, 'experiment', f'{title}: {result}')


def visit(request, label, url):
    data = _data(request)
    if data['activity'] and data['activity'][0].get('label') == label and data['activity'][0].get('kind') == 'visit':
        return
    log(request, 'visit', label, url)


def summary(request):
    return _data(request)
