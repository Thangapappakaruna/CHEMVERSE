from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.utils import add_xp
from config.chem import ChemError, balance_equation
from dashboard.utils import log_activity

from .forms import ReactionForm
from .logic import TYPE_INFO, analyse, equation_text, parse_side, side_text
from .models import Reaction

QUICK_ADD = ['H2', 'O2', 'H2O', 'CO2', 'CH4', 'NaCl', 'HCl', 'NaOH', 'Fe', 'Cu', 'Zn', 'N2', 'NH3']


def _visible(request):
    q = Q(is_public=True) | Q(is_sample=True)
    if request.user.is_authenticated:
        q |= Q(user=request.user)
    return Reaction.objects.filter(q)


def reaction_list(request):
    qs = _visible(request).select_related('user')
    rtype, q, show = request.GET.get('type', ''), request.GET.get('q', '').strip(), request.GET.get('show', '')
    if rtype:
        qs = qs.filter(reaction_type=rtype)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(equation__icontains=q))
    if show == 'mine' and request.user.is_authenticated:
        qs = qs.filter(user=request.user)
    elif show == 'samples':
        qs = qs.filter(is_sample=True)
    return render(request, 'reaction_builder/list.html', {
        'reactions': qs, 'types': Reaction._meta.get_field('reaction_type').choices, 'rtype': rtype, 'q': q, 'show': show})


def create(request, pk=None):
    if pk and not request.user.is_authenticated:
        return redirect(f"{reverse('accounts:login')}?next={request.path}")
    inst = get_object_or_404(Reaction, pk=pk, user=request.user) if pk else None
    initial = {}
    if inst:
        initial = {'title': inst.title, 'reactants': side_text(inst.reactants), 'products': side_text(inst.products),
                   'reaction_type': inst.reaction_type, 'conditions': inst.conditions, 'explanation': inst.explanation,
                   'is_public': inst.is_public}
    elif request.GET.get('from', '').isdigit():
        src = _visible(request).filter(pk=request.GET['from']).first()
        if src:
            initial = {'title': f'{src.title} (my version)', 'reactants': side_text(src.reactants),
                       'products': side_text(src.products), 'conditions': src.conditions}
    form = ReactionForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        info = analyse(d['reactants'], d['products'])
        if not request.user.is_authenticated:
            kind = info['detected_type'] if d['reaction_type'] == 'auto' else d['reaction_type']
            return render(request, 'reaction_builder/form.html', {
                'form': form, 'editing': None, 'type_info': TYPE_INFO, 'quick_add': QUICK_ADD,
                'guest_result': info, 'guest_type_text': TYPE_INFO.get(kind, '')})
        r = inst or Reaction(user=request.user)
        r.title, r.reactants, r.products = d['title'], d['reactants'], d['products']
        r.equation = info['equation']
        r.reaction_type = info['detected_type'] if d['reaction_type'] == 'auto' else d['reaction_type']
        r.conditions, r.explanation, r.is_public = d['conditions'], d['explanation'], d['is_public']
        r.is_balanced = info['is_balanced']
        r.save()
        if not inst:
            log_activity(request.user, 'reaction', f'Created reaction: {r.title}', f'/reactions/{r.pk}/')
            add_xp(request.user, 15 if r.is_balanced else 5)
        if r.is_balanced:
            messages.success(request, 'Reaction saved – it is balanced!')
        else:
            messages.warning(request, 'Reaction saved, but it is not balanced yet. See the balancing help below.')
        return redirect('reaction_builder:detail', pk=r.pk)
    return render(request, 'reaction_builder/form.html', {'form': form, 'editing': inst, 'type_info': TYPE_INFO,
                                                          'quick_add': QUICK_ADD})


def detail(request, pk):
    r = get_object_or_404(_visible(request).select_related('user'), pk=pk)
    try:
        info = analyse(r.reactants, r.products)
    except ChemError as exc:
        info = {'error': str(exc)}
    return render(request, 'reaction_builder/detail.html', {
        'r': r, 'info': info, 'type_text': TYPE_INFO.get(r.reaction_type, ''),
        'own': request.user.is_authenticated and r.user_id == request.user.id})


@login_required
@require_POST
def apply_balance(request, pk):
    r = get_object_or_404(Reaction, pk=pk, user=request.user)
    try:
        res = balance_equation(r.equation)
    except ChemError as exc:
        messages.error(request, str(exc))
        return redirect('reaction_builder:detail', pk=pk)
    r.reactants = [{'coef': c, 'formula': f} for c, f in res['reactants']]
    r.products = [{'coef': c, 'formula': f} for c, f in res['products']]
    r.equation = equation_text(r.reactants, r.products)
    r.is_balanced = True
    r.save()
    add_xp(request.user, 5)
    messages.success(request, 'Coefficients updated – the reaction is now balanced.')
    return redirect('reaction_builder:detail', pk=pk)


@login_required
@require_POST
def delete(request, pk):
    r = get_object_or_404(Reaction, pk=pk, user=request.user)
    r.delete()
    messages.info(request, f'“{r.title}” deleted.')
    return redirect('reaction_builder:list')


def api_check(request):
    try:
        info = analyse(parse_side(request.GET.get('reactants', '')), parse_side(request.GET.get('products', '')))
    except ChemError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)})
    info['ok'] = True
    return JsonResponse(info)
