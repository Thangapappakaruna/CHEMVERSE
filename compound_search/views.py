from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from config.chem import composition
from dashboard.utils import log_activity

from .forms import CompoundForm
from .models import Compound, FavoriteCompound, SearchHistory

SORTS = {'name': 'name', 'formula': 'formula', 'mass': 'molar_mass', '-mass': '-molar_mass',
         'mp': 'melting_point', '-mp': '-melting_point', 'bp': 'boiling_point', '-bp': '-boiling_point'}


def filter_compounds(params):
    q = params.get('q', '').strip()
    qs = Compound.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(formula__icontains=q) | Q(category__icontains=q))
    if params.get('category'):
        qs = qs.filter(category=params['category'])
    if params.get('state') in ('solid', 'liquid', 'gas'):
        qs = qs.filter(state=params['state'])
    return qs.order_by(SORTS.get(params.get('sort'), 'name'), 'name'), q


def search(request):
    qs, q = filter_compounds(request.GET)
    if q and request.user.is_authenticated and request.GET.get('page') in (None, '1'):
        n = qs.count()
        SearchHistory.objects.create(user=request.user, query=q[:100], results=n)
        log_activity(request.user, 'search', f'Searched compounds for “{q}” ({n} results)', request.get_full_path())
    page = Paginator(qs, 15).get_page(request.GET.get('page'))
    favs = set()
    if request.user.is_authenticated:
        favs = set(FavoriteCompound.objects.filter(user=request.user).values_list('compound_id', flat=True))
    return render(request, 'compound_search/search.html', {
        'page': page, 'q': q, 'params': request.GET, 'favs': favs,
        'categories': Compound.objects.values_list('category', flat=True).distinct().order_by('category')})


def detail(request, pk):
    c = get_object_or_404(Compound, pk=pk)
    try:
        comp = composition(c.formula)
    except Exception:
        comp = None
    is_fav = request.user.is_authenticated and FavoriteCompound.objects.filter(user=request.user, compound=c).exists()
    return render(request, 'compound_search/detail.html', {'c': c, 'comp': comp, 'is_fav': is_fav,
                                                            'props': c.properties.all()})


@login_required
@require_POST
def toggle_favorite(request, pk):
    c = get_object_or_404(Compound, pk=pk)
    fav = FavoriteCompound.objects.filter(user=request.user, compound=c).first()
    if fav:
        fav.delete()
        state = False
    else:
        FavoriteCompound.objects.create(user=request.user, compound=c)
        state = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept', '').startswith('application/json'):
        return JsonResponse({'ok': True, 'favorite': state})
    messages.success(request, f'{c.name} {"added to" if state else "removed from"} favourites.')
    nxt = request.POST.get('next', '')
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect('compound_search:detail', pk=pk)


@login_required
def add(request):
    form = CompoundForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        c = form.save(commit=False)
        c.added_by = request.user
        c.save()
        messages.success(request, f'{c.name} was added. It is labelled “User submitted”.')
        return redirect('compound_search:detail', pk=c.pk)
    return render(request, 'compound_search/form.html', {'form': form})


def api_search(request):
    qs, _ = filter_compounds(request.GET)
    data = list(qs.values('id', 'name', 'formula', 'molar_mass', 'melting_point', 'mp_note', 'boiling_point',
                          'bp_note', 'state', 'category', 'data_quality')[:100])
    return JsonResponse({'count': len(data), 'results': data})
