from django.db.models import Max, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from accounts.utils import add_xp
from config.http import bad, json_body
from dashboard import guest
from dashboard.utils import log_activity

from .models import Game, GameScore


def index(request):
    games = list(Game.objects.all())
    if request.user.is_authenticated:
        best = dict(GameScore.objects.filter(user=request.user).values('game_id').annotate(b=Max('points')).values_list('game_id', 'b'))
        for g in games:
            g.best = best.get(g.id)
    if request.user.is_authenticated:
        total = GameScore.objects.filter(user=request.user).aggregate(s=Sum('points'))['s']
    else:
        mine = guest.summary(request)['games']
        for g in games:
            g.best = mine[g.slug]['best'] if g.slug in mine else None
        total = sum(v['total'] for v in mine.values())
    return render(request, 'chemistry_games/index.html', {'games': games, 'total': total or 0})


def play(request, slug):
    game = get_object_or_404(Game, slug=slug)
    top = (GameScore.objects.filter(game=game).values('user__username').annotate(best=Max('points')).order_by('-best')[:5])
    return render(request, 'chemistry_games/play.html', {'game': game, 'top': top})


@require_POST
def submit(request):
    data = json_body(request)
    if data is None:
        return bad('Invalid JSON')
    game = Game.objects.filter(slug=data.get('game')).first()
    if not game:
        return bad('Unknown game')
    try:
        points = int(data.get('points'))
    except (TypeError, ValueError):
        return bad('Points must be a number')
    if not 0 <= points <= game.max_points:
        return bad(f'Points must be between 0 and {game.max_points}')
    details = str(data.get('details', ''))[:120]
    if not request.user.is_authenticated:
        best = guest.add_game(request, game.slug, game.title, points)
        return JsonResponse({'ok': True, 'best': best, 'points': points, 'guest': True})
    GameScore.objects.create(user=request.user, game=game, points=points, details=details)
    add_xp(request.user, min(points // 20, 60))
    log_activity(request.user, 'game', f'{game.title}: {points} points', f'/games/{game.slug}/')
    best = GameScore.objects.filter(user=request.user, game=game).aggregate(m=Max('points'))['m']
    return JsonResponse({'ok': True, 'best': best, 'points': points})
