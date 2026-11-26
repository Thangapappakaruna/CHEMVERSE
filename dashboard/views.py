import json

from django.contrib import messages
from django.core.mail import mail_admins
from django.db.models import Avg, Sum
from django.shortcuts import redirect, render

from accounts.utils import get_profile
from chemistry_games.models import Game, GameScore
from chemistry_learning.models import Lesson, LessonProgress
from chemistry_quiz.models import QuizResult
from compound_search.models import Compound, FavoriteCompound, SearchHistory
from molecular_structure.models import Structure
from periodic_table.models import Element
from reaction_builder.models import Reaction

from . import guest
from .forms import ContactForm
from .models import Activity
from .utils import achievements

TOOLS = [
    ('book', 'Chemistry Lessons', 'Concepts, definitions and tutorials from atoms to gas laws.', 'chemistry_learning:list'),
    ('table', 'Periodic Table', 'All 118 elements, colour-coded and searchable.', 'periodic_table:table'),
    ('search', 'Compound Search', 'Formula, molecular weight, properties and safety.', 'compound_search:search'),
    ('thermo', 'Boiling & Melting', 'Filter, compare and chart physical properties.', 'boiling_melting:index'),
    ('hexagon', 'Structure Lab', 'Draw 2D molecules with single, double and triple bonds.', 'molecular_structure:editor'),
    ('zap', 'Reaction Builder', 'Create your own reactions with balancing help.', 'reaction_builder:list'),
    ('scale', 'Equation Balancer', 'Step-by-step balancing of any equation.', 'reaction_balancer:index'),
    ('gamepad', 'Chemistry Games', 'Seven games from element guessing to boiling points.', 'chemistry_games:index'),
    ('help', 'Chemistry Quiz', 'MCQ quizzes by topic and difficulty, with leaderboards.', 'chemistry_quiz:index'),
    ('calculator', 'Molecular Weight', 'Molar mass, composition and gram–mole conversion.', 'molecular_weight:index'),
    ('beaker', 'Lab Simulator', 'Safe virtual titration, flame tests, gas laws and more.', 'lab_simulator:index'),
    ('dictionary', 'Dictionary', 'Search 65 chemistry terms with examples.', 'chemistry_dictionary:index'),
    ('users', 'Community', 'Ask questions, discuss and share reactions.', 'community:list'),
]


def home(request):
    from chemistry_dictionary.models import Term
    stats = [('Elements', Element.objects.count()), ('Compounds', Compound.objects.count()),
             ('Dictionary terms', Term.objects.count()), ('Lessons', Lesson.objects.count())]
    return render(request, 'dashboard/home.html', {'tools': TOOLS, 'stats': stats,
                                                   'seeded': Element.objects.exists()})


def dashboard(request):
    if not request.user.is_authenticated:
        return guest_dashboard(request)
    user = request.user
    prof = get_profile(user)
    lessons_total = Lesson.objects.count()
    lessons_done = LessonProgress.objects.filter(user=user).count()
    results = list(QuizResult.objects.filter(user=user).order_by('-created_at')[:10])[::-1]
    game_points = GameScore.objects.filter(user=user).aggregate(s=Sum('points'))['s'] or 0
    per_game = []
    for g in Game.objects.all():
        total = GameScore.objects.filter(user=user, game=g).aggregate(s=Sum('points'))['s'] or 0
        per_game.append({'title': g.title, 'points': total})
    by_cat = []
    for cat in Lesson.objects.values_list('category', flat=True).distinct():
        tot = Lesson.objects.filter(category=cat).count()
        done = LessonProgress.objects.filter(user=user, lesson__category=cat).count()
        by_cat.append({'category': cat, 'done': done, 'total': tot, 'pct': round(100 * done / tot) if tot else 0})
    badges = achievements(user)
    ctx = {
        'prof': prof,
        'lessons_done': lessons_done, 'lessons_total': lessons_total,
        'lesson_pct': round(100 * lessons_done / lessons_total) if lessons_total else 0,
        'quiz_avg': round(QuizResult.objects.filter(user=user).aggregate(a=Avg('percent'))['a'] or 0),
        'quiz_count': QuizResult.objects.filter(user=user).count(),
        'game_points': game_points,
        'structures': Structure.objects.filter(user=user)[:5],
        'structure_count': Structure.objects.filter(user=user).count(),
        'favorites': FavoriteCompound.objects.filter(user=user).select_related('compound')[:5],
        'recent_searches': SearchHistory.objects.filter(user=user)[:6],
        'recent_tools': Activity.objects.filter(user=user, kind='visit')[:6],
        'recent_activity': Activity.objects.filter(user=user).exclude(kind='visit')[:8],
        'reactions': Reaction.objects.filter(user=user)[:4],
        'by_cat': by_cat,
        'badges': badges, 'badges_earned': sum(b['earned'] for b in badges),
        'quiz_chart': json.dumps({'labels': [r.created_at.strftime('%d %b') for r in results],
                                  'data': [r.percent for r in results]}),
        'game_chart': json.dumps({'labels': [g['title'] for g in per_game], 'data': [g['points'] for g in per_game]}),
        'tools': TOOLS,
    }
    return render(request, 'dashboard/dashboard.html', ctx)


def guest_dashboard(request):
    data = guest.summary(request)
    lessons_total = Lesson.objects.count()
    quiz = data['quiz'][-10:]
    games = list(data['games'].values())
    return render(request, 'dashboard/guest_dashboard.html', {
        'data': data, 'lessons_done': len(data['lessons']), 'lessons_total': lessons_total,
        'lesson_pct': round(100 * len(data['lessons']) / lessons_total) if lessons_total else 0,
        'quiz_avg': round(sum(q['percent'] for q in quiz) / len(quiz)) if quiz else 0,
        'game_points': sum(g['total'] for g in games),
        'recent_tools': [a for a in data['activity'] if a['kind'] == 'visit'][:6],
        'recent_activity': [a for a in data['activity'] if a['kind'] != 'visit'][:8],
        'quiz_chart': json.dumps({'labels': [q['at'] for q in quiz], 'data': [q['percent'] for q in quiz]}),
        'game_chart': json.dumps({'labels': [g['title'] for g in games], 'data': [g['total'] for g in games]}),
        'tools': TOOLS,
    })


def about(request):
    return render(request, 'dashboard/about.html', {'tools': TOOLS})


def contact(request):
    initial = {}
    if request.user.is_authenticated:
        initial = {'name': get_profile(request.user).display_name, 'email': request.user.email}
    form = ContactForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        msg = form.save(commit=False)
        if request.user.is_authenticated:
            msg.user = request.user
        msg.save()
        try:
            mail_admins(f'[CHEMVERSE contact] {msg.subject}', f'From {msg.name} <{msg.email}>\n\n{msg.message}')
        except Exception:
            pass
        messages.success(request, 'Thanks! Your message has been received.')
        return redirect('dashboard:contact')
    return render(request, 'dashboard/contact.html', {'form': form})


def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
