from django.http import JsonResponse
from django.shortcuts import render

from config.chem import ChemError, balance_equation
from dashboard.utils import log_activity

from .models import BalanceRecord

EXAMPLES = ['H2 + O2 -> H2O', 'CH4 + O2 -> CO2 + H2O', 'Fe + O2 -> Fe2O3', 'C3H8 + O2 -> CO2 + H2O',
            'Al + HCl -> AlCl3 + H2', 'KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2', 'Ca(OH)2 + H3PO4 -> Ca3(PO4)2 + H2O',
            'C6H12O6 + O2 -> CO2 + H2O']


def index(request):
    eq = (request.POST.get('equation') or request.GET.get('equation') or '').strip()
    result = error = None
    if eq:
        try:
            result = balance_equation(eq)
            if request.user.is_authenticated and request.method == 'POST':
                BalanceRecord.objects.create(user=request.user, equation=eq[:300], balanced=result['balanced'][:400])
                log_activity(request.user, 'reaction', f'Balanced {result["balanced"]}', '/balancer/')
        except ChemError as exc:
            error = str(exc)
    history = BalanceRecord.objects.filter(user=request.user)[:10] if request.user.is_authenticated else []
    return render(request, 'reaction_balancer/index.html', {'equation': eq, 'result': result, 'error': error,
                                                            'examples': EXAMPLES, 'history': history})


def api_balance(request):
    try:
        return JsonResponse({'ok': True, **balance_equation(request.GET.get('equation', ''))})
    except ChemError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)})
