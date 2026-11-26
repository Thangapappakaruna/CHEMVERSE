import re

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from compound_search.models import Compound

from .models import CATEGORY_LABELS, Element
from .utils import electron_configuration, shells


def table(request):
    q = request.GET.get('q', '').strip()
    if q:
        match = Element.objects.filter(Q(symbol__iexact=q) | Q(name__iexact=q) | Q(number=q if q.isdigit() else -1)).first()
        if match:
            return redirect('periodic_table:detail', symbol=match.symbol)
    return render(request, 'periodic_table/table.html', {'elements': Element.objects.all(),
                                                         'categories': CATEGORY_LABELS, 'q': q})


def detail(request, symbol):
    e = get_object_or_404(Element, symbol__iexact=symbol)
    related = [c for c in Compound.objects.exclude(data_quality='user') if e.symbol in re.findall(r'[A-Z][a-z]?', c.formula)][:10]
    return render(request, 'periodic_table/detail.html', {
        'e': e, 'config': electron_configuration(e.number), 'shells': shells(e.number),
        'neutrons': round(e.atomic_mass) - e.number,
        'prev': Element.objects.filter(number=e.number - 1).first(),
        'next': Element.objects.filter(number=e.number + 1).first(),
        'same_group': Element.objects.filter(group=e.group).exclude(pk=e.pk) if e.group else [],
        'related': related})


def api_elements(request):
    return JsonResponse({'count': Element.objects.count(), 'elements': [e.to_dict() for e in Element.objects.all()]})


def api_element(request, symbol):
    e = Element.objects.filter(symbol__iexact=symbol).first()
    if not e:
        return JsonResponse({'error': 'Element not found'}, status=404)
    data = e.to_dict()
    data.update({'electron_configuration': electron_configuration(e.number), 'shells': shells(e.number)})
    return JsonResponse(data)
