import random
import time

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Max, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render

from accounts.models import Profile
from accounts.utils import add_xp
from chemistry_games.models import GameScore
from dashboard import guest
from dashboard.utils import log_activity

from .models import Question, QuizResult

DIFFICULTIES = [('', 'Any difficulty'), ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]


def index(request):
    cats = Question.objects.values('category').annotate(n=Count('id')).order_by('category')
    diffs = dict(Question.objects.values_list('difficulty').annotate(n=Count('id')))
    recent = QuizResult.objects.filter(user=request.user)[:6] if request.user.is_authenticated else []
    return render(request, 'chemistry_quiz/index.html', {'categories': cats, 'difficulties': DIFFICULTIES,
                                                         'diff_counts': diffs, 'recent': recent})


def play(request):
    if request.method == 'POST':
        ids = request.session.get('quiz_ids') or []
        if not ids:
            messages.warning(request, 'That quiz has already been submitted. Start a new one.')
            return redirect('chemistry_quiz:index')
        qmap = {q.id: q for q in Question.objects.filter(id__in=ids)}
        review, score = [], 0
        for qid in ids:
            q = qmap.get(qid)
            if q:
                given = request.POST.get(f'q{qid}', '')
                ok = given == q.answer
                score += ok
                review.append({'q': q, 'given': given, 'ok': ok})
        total = len(review)
        pct = round(100 * score / total) if total else 0
        duration = int(time.time() - request.session.get('quiz_start', time.time()))
        if request.user.is_authenticated:
            QuizResult.objects.create(user=request.user, category=request.session.get('quiz_cat', ''),
                                      difficulty=request.session.get('quiz_diff', ''), score=score, total=total,
                                      percent=pct, duration_seconds=max(duration, 0))
            add_xp(request.user, score * 5)
            log_activity(request.user, 'quiz', f'Quiz {request.session.get("quiz_cat") or "Mixed"}: {score}/{total} ({pct}%)', '/quiz/')
        else:
            guest.add_quiz(request, request.session.get('quiz_cat', ''), score, total, pct)
        for k in ('quiz_ids', 'quiz_cat', 'quiz_diff', 'quiz_start'):
            request.session.pop(k, None)
        return render(request, 'chemistry_quiz/result.html', {'review': review, 'score': score, 'total': total,
                                                              'pct': pct, 'duration': duration})
    cat, diff = request.GET.get('category', ''), request.GET.get('difficulty', '')
    try:
        n = max(5, min(20, int(request.GET.get('n', 10))))
    except ValueError:
        n = 10
    qs = Question.objects.all()
    if cat:
        qs = qs.filter(category=cat)
    if diff:
        qs = qs.filter(difficulty=diff)
    ids = list(qs.values_list('id', flat=True))
    if not ids:
        messages.warning(request, 'No questions match that topic and difficulty. Try another combination.')
        return redirect('chemistry_quiz:index')
    picked = random.sample(ids, min(n, len(ids)))
    request.session.update({'quiz_ids': picked, 'quiz_cat': cat, 'quiz_diff': diff, 'quiz_start': time.time()})
    qmap = {q.id: q for q in Question.objects.filter(id__in=picked)}
    return render(request, 'chemistry_quiz/play.html', {'questions': [qmap[i] for i in picked], 'cat': cat, 'diff': diff,
                                                        'seconds': 45 * len(picked)})


def leaderboard(request):
    board = request.GET.get('board', 'quiz')
    User = get_user_model()
    if board == 'games':
        rows = (GameScore.objects.values('user__username').annotate(value=Sum('points'), n=Count('id')).order_by('-value')[:25])
        label = 'Total game points'
    elif board == 'xp':
        rows = [{'user__username': p.user.username, 'value': p.xp, 'n': p.level}
                for p in Profile.objects.select_related('user').order_by('-xp')[:25]]
        label = 'XP'
    else:
        board = 'quiz'
        rows = (QuizResult.objects.values('user__username').annotate(value=Max('percent'), n=Count('id')).order_by('-value', '-n')[:25])
        label = 'Best quiz score (%)'
    return render(request, 'chemistry_quiz/leaderboard.html', {'rows': rows, 'board': board, 'label': label,
                                                               'players': User.objects.count()})


def api_questions(request):
    try:
        n = max(1, min(50, int(request.GET.get('n', 20))))
    except ValueError:
        n = 20
    qs = list(Question.objects.all())
    random.shuffle(qs)
    return JsonResponse({'questions': [{'id': q.id, 'text': q.text, 'options': [o for _, o in q.options],
                                        'answer': 'abcd'.index(q.answer), 'explanation': q.explanation,
                                        'difficulty': q.difficulty} for q in qs[:n]]})
