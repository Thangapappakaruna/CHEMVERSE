import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from compound_search.models import Compound
from periodic_table.models import Element

from .models import SavedComparison


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def index(request):
    p = request.GET
    qs = Compound.objects.all()
    for key, lookup in [('mp_min', 'melting_point__gte'), ('mp_max', 'melting_point__lte'),
                        ('bp_min', 'boiling_point__gte'), ('bp_max', 'boiling_point__lte')]:
        v = _num(p.get(key))
        if v is not None:
            qs = qs.filter(**{lookup: v})
    if p.get('state') in ('solid', 'liquid', 'gas'):
        qs = qs.filter(state=p['state'])
    t = _num(p.get('t'))
    rows = list(qs.order_by('boiling_point'))
    for c in rows:
        if t is not None:
            c.state_t = c.state_at(t)
        c.liquid_range = (round(c.boiling_point - c.melting_point, 1)
                          if c.melting_point is not None and c.boiling_point is not None else None)
    elements = []
    if p.get('elements'):
        elements = Element.objects.exclude(melting_point=None, boiling_point=None)
        for k, lk in [('mp_min', 'melting_point__gte'), ('mp_max', 'melting_point__lte'),
                      ('bp_min', 'boiling_point__gte'), ('bp_max', 'boiling_point__lte')]:
            v = _num(p.get(k))
            if v is not None:
                elements = elements.filter(**{lk: v})
    return render(request, 'boiling_melting/index.html', {
        'rows': rows, 'params': p, 't': t, 'elements': elements, 'all_compounds': Compound.objects.all(),
        'saved': SavedComparison.objects.filter(user=request.user) if request.user.is_authenticated else []})


def compare(request):
    ids = [int(i) for i in request.GET.getlist('c') if i.isdigit()][:8]
    compounds = list(Compound.objects.filter(id__in=ids))
    chart = {'labels': [c.name for c in compounds],
             'mp': [c.melting_point for c in compounds], 'bp': [c.boiling_point for c in compounds]}
    return render(request, 'boiling_melting/compare.html', {'compounds': compounds, 'chart': json.dumps(chart),
                                                            'all_compounds': Compound.objects.all(), 'ids': ids})


@login_required
@require_POST
def save_comparison(request):
    ids = [int(i) for i in request.POST.getlist('c') if i.isdigit()][:8]
    name = request.POST.get('name', '').strip()[:80] or 'My comparison'
    if len(ids) < 2:
        messages.error(request, 'Pick at least two compounds to save a comparison.')
        return redirect('boiling_melting:index')
    sc = SavedComparison.objects.create(user=request.user, name=name)
    sc.compounds.set(Compound.objects.filter(id__in=ids))
    messages.success(request, f'Comparison “{name}” saved.')
    return redirect(reverse('boiling_melting:compare') + '?' + '&'.join(f'c={i}' for i in ids))


@login_required
@require_POST
def delete_comparison(request, pk):
    get_object_or_404(SavedComparison, pk=pk, user=request.user).delete()
    messages.info(request, 'Comparison deleted.')
    return redirect('boiling_melting:index')


def api_data(request):
    data = list(Compound.objects.values('id', 'name', 'formula', 'melting_point', 'mp_note', 'boiling_point', 'bp_note', 'state'))
    return JsonResponse({'count': len(data), 'compounds': data})
