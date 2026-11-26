from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.utils import add_xp
from dashboard import guest
from dashboard.utils import log_activity

from .models import Lesson, LessonProgress


def lesson_list(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('category', '')
    lessons = Lesson.objects.all()
    if q:
        lessons = lessons.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(content__icontains=q))
    if cat:
        lessons = lessons.filter(category=cat)
    if request.user.is_authenticated:
        done = set(LessonProgress.objects.filter(user=request.user).values_list('lesson_id', flat=True))
    else:
        done = set(Lesson.objects.filter(slug__in=guest.summary(request)['lessons']).values_list('id', flat=True))
    total = Lesson.objects.count()
    return render(request, 'chemistry_learning/list.html', {
        'lessons': lessons, 'done': done, 'q': q, 'cat': cat,
        'categories': Lesson.objects.values_list('category', flat=True).distinct().order_by('category'),
        'pct': round(100 * len(done) / total) if total else 0})


def lesson_detail(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)
    if request.user.is_authenticated:
        done = LessonProgress.objects.filter(user=request.user, lesson=lesson).exists()
    else:
        done = lesson.slug in guest.summary(request)['lessons']
    return render(request, 'chemistry_learning/detail.html', {
        'lesson': lesson, 'done': done,
        'next': Lesson.objects.filter(order__gt=lesson.order).first(),
        'prev': Lesson.objects.filter(order__lt=lesson.order).order_by('-order').first()})


@require_POST
def complete(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)
    if not request.user.is_authenticated:
        if guest.complete_lesson(request, lesson.slug, lesson.title):
            messages.success(request, 'Lesson complete! Sign in to keep your progress permanently.')
        nxt = Lesson.objects.filter(order__gt=lesson.order).first()
        return redirect('chemistry_learning:detail', slug=nxt.slug) if nxt else redirect('chemistry_learning:list')
    _, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    if created:
        add_xp(request.user, 25)
        log_activity(request.user, 'lesson', f'Completed lesson: {lesson.title}', request.path.replace('complete/', ''))
        messages.success(request, 'Lesson complete – +25 XP!')
    nxt = Lesson.objects.filter(order__gt=lesson.order).first()
    return redirect('chemistry_learning:detail', slug=nxt.slug) if nxt else redirect('chemistry_learning:list')
