import json

from django.http import JsonResponse
from django.shortcuts import render

from config.chem import ChemError, composition

from .models import WeightCalculation

EXAMPLES = ['H2O', 'C6H12O6', 'NaCl', 'H2SO4', 'Ca(OH)2', 'CuSO4·5H2O', 'C8H10N4O2', 'Fe2(SO4)3']


def _num(v):
    try:
        f = float(v)
        return f if f >= 0 else None
    except (TypeError, ValueError):
        return None


def index(request):
    formula = (request.GET.get('formula') or '').strip()
    grams, moles = _num(request.GET.get('grams')), _num(request.GET.get('moles'))
    result = error = None
    conv = {}
    if formula:
        try:
            result = composition(formula)
            mm = result['molar_mass']
            if grams is not None:
                conv['moles_from_g'] = round(grams / mm, 6)
                conv['particles'] = f'{grams / mm * 6.02214076e23:.4e}'
            if moles is not None:
                conv['grams_from_mol'] = round(moles * mm, 4)
            if request.user.is_authenticated:
                last = WeightCalculation.objects.filter(user=request.user).first()
                if not last or last.formula != formula:
                    WeightCalculation.objects.create(user=request.user, formula=formula[:60], molar_mass=mm)
        except ChemError as exc:
            error = str(exc)
    chart = json.dumps({'labels': [r['element'] for r in result['rows']], 'data': [r['percent'] for r in result['rows']]}) if result else 'null'
    history = WeightCalculation.objects.filter(user=request.user)[:10] if request.user.is_authenticated else []
    return render(request, 'molecular_weight/index.html', {
        'formula': formula, 'grams': request.GET.get('grams', ''), 'moles': request.GET.get('moles', ''),
        'result': result, 'error': error, 'conv': conv, 'chart': chart, 'examples': EXAMPLES, 'history': history})


def api(request):
    try:
        return JsonResponse({'ok': True, **composition(request.GET.get('formula', ''))})
    except ChemError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)})
