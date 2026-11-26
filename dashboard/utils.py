from datetime import timedelta

from django.utils import timezone


def log_activity(user, kind, label, url=''):
    if not getattr(user, 'is_authenticated', False):
        return
    from .models import Activity
    Activity.objects.create(user=user, kind=kind, label=str(label)[:200], url=str(url)[:300])


def recent_visit_exists(user, label, minutes=20):
    from .models import Activity
    since = timezone.now() - timedelta(minutes=minutes)
    return Activity.objects.filter(user=user, kind='visit', label=label, created_at__gte=since).exists()


def achievements(user):
    """List of (icon, title, description, earned) computed from the user's data."""
    from accounts.models import Profile
    from chemistry_games.models import GameScore
    from chemistry_learning.models import LessonProgress
    from chemistry_quiz.models import QuizResult
    from community.models import Post
    from compound_search.models import FavoriteCompound
    from lab_simulator.models import ExperimentLog
    from molecular_structure.models import Structure
    from reaction_builder.models import Reaction

    prof = Profile.objects.filter(user=user).first()
    best_quiz = QuizResult.objects.filter(user=user).order_by('-percent').values_list('percent', flat=True).first() or 0
    rules = [
        ('mail', 'Verified Chemist', 'Verify your email address', bool(prof and prof.email_verified)),
        ('book', 'First Lesson', 'Complete a lesson', LessonProgress.objects.filter(user=user).exists()),
        ('sparkles', 'Scholar', 'Complete 5 lessons', LessonProgress.objects.filter(user=user).count() >= 5),
        ('help', 'Quiz Whiz', 'Score 80% or more in a quiz', best_quiz >= 80),
        ('gamepad', 'Gamer', 'Play 10 games', GameScore.objects.filter(user=user).count() >= 10),
        ('hexagon', 'Molecule Maker', 'Save a molecular structure', Structure.objects.filter(user=user).exists()),
        ('zap', 'Reaction Engineer', 'Create a reaction', Reaction.objects.filter(user=user).exists()),
        ('star', 'Collector', 'Save 5 favourite compounds', FavoriteCompound.objects.filter(user=user).count() >= 5),
        ('beaker', 'Lab Explorer', 'Record 3 virtual experiments', ExperimentLog.objects.filter(user=user).count() >= 3),
        ('users', 'Community Voice', 'Publish a community post', Post.objects.filter(author=user).exists()),
    ]
    return [{'icon': i, 'title': t, 'desc': d, 'earned': e} for i, t, d, e in rules]
