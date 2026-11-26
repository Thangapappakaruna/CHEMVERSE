import string

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from dashboard.utils import log_activity

from .models import Term


def index(request):
    q = request.GET.get('q', '').strip()
    letter = request.GET.get('letter', '').upper()[:1]
    cat = request.GET.get('category', '')
    terms = Term.objects.all()
    if q:
        terms = terms.filter(Q(term__icontains=q) | Q(definition__icontains=q))
        if request.user.is_authenticated:
            log_activity(request.user, 'search', f'Dictionary search “{q}”', request.get_full_path())
    if letter:
        terms = terms.filter(term__istartswith=letter)
    if cat:
        terms = terms.filter(category=cat)
    present = {t[0].upper() for t in Term.objects.values_list('term', flat=True)}
    return render(request, 'chemistry_dictionary/index.html', {
        'terms': terms, 'q': q, 'letter': letter, 'cat': cat, 'letters': [(c, c in present) for c in string.ascii_uppercase],
        'categories': Term.objects.values_list('category', flat=True).distinct().order_by('category')})


def detail(request, slug):
    term = get_object_or_404(Term, slug=slug)
    related = Term.objects.filter(category=term.category).exclude(pk=term.pk)[:8]
    return render(request, 'chemistry_dictionary/detail.html', {'term': term, 'related': related})


def api_search(request):
    q = request.GET.get('q', '').strip()
    qs = Term.objects.filter(term__icontains=q) if q else Term.objects.all()
    return JsonResponse({'results': list(qs.values('term', 'slug', 'category', 'definition')[:20])})
