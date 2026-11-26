import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from config.chem import atomic_masses, hill_formula
from config.http import bad, json_body
from dashboard.utils import log_activity

from .models import Structure

PALETTE = ['C', 'H', 'O', 'N', 'S', 'P', 'F', 'Cl', 'Br', 'I', 'B', 'Si', 'Na', 'Mg']
VALENCE = {'H': 1, 'C': 4, 'N': 3, 'O': 2, 'S': 2, 'P': 3, 'F': 1, 'Cl': 1, 'Br': 1, 'I': 1, 'B': 3, 'Si': 4, 'Na': 1, 'Mg': 2}


def _visible(request):
    if request.user.is_authenticated:
        return Structure.objects.filter(Q(is_public=True) | Q(user=request.user))
    return Structure.objects.filter(is_public=True)


def editor(request):
    struct = None
    sid = request.GET.get('id', '')
    if sid.isdigit():
        struct = _visible(request).filter(pk=sid).first()
        if not struct:
            messages.warning(request, 'That structure is private or does not exist.')
    return render(request, 'molecular_structure/editor.html', {
        'struct': struct, 'initial': struct.data if struct else None, 'palette': PALETTE,
        'valence': VALENCE, 'masses': {s: atomic_masses()[s] for s in PALETTE},
        'own': bool(struct and struct.user_id == request.user.id)})


def gallery(request):
    return render(request, 'molecular_structure/gallery.html', {
        'mine': Structure.objects.filter(user=request.user) if request.user.is_authenticated else [],
        'public': Structure.objects.filter(is_public=True).select_related('user')[:40]})


@login_required
@require_POST
def save(request):
    data = json_body(request)
    if data is None:
        return bad('Invalid JSON')
    atoms, bonds = data.get('atoms'), data.get('bonds', [])
    if not isinstance(atoms, list) or not atoms:
        return bad('Draw at least one atom before saving.')
    if not isinstance(bonds, list) or len(atoms) > 300 or len(bonds) > 600:
        return bad('Structure is too large (max 300 atoms).')
    clean_atoms, counts = [], {}
    for a in atoms:
        if not isinstance(a, dict):
            return bad('Bad atom data')
        el = str(a.get('el', ''))
        if el not in VALENCE or not re.fullmatch(r'[A-Z][a-z]?', el):
            return bad(f'Unsupported element: {el}')
        try:
            x, y = float(a.get('x', 0)), float(a.get('y', 0))
        except (TypeError, ValueError):
            return bad('Bad coordinates')
        clean_atoms.append({'el': el, 'x': round(x, 1), 'y': round(y, 1)})
        counts[el] = counts.get(el, 0) + 1
    clean_bonds, seen = [], set()
    for b in bonds:
        try:
            i, j, order = int(b.get('a')), int(b.get('b')), int(b.get('order', 1))
        except (TypeError, ValueError, AttributeError):
            continue
        key = tuple(sorted((i, j)))
        if 0 <= i < len(clean_atoms) and 0 <= j < len(clean_atoms) and i != j and order in (1, 2, 3) and key not in seen:
            seen.add(key)
            clean_bonds.append({'a': i, 'b': j, 'order': order})
    masses = atomic_masses()
    mm = round(sum(masses[el] * n for el, n in counts.items()), 3)
    formula = hill_formula(counts)
    name = str(data.get('name', '')).strip()[:80] or formula or 'Untitled molecule'
    payload = {'atoms': clean_atoms, 'bonds': clean_bonds}
    sid = data.get('id')
    if sid:
        s = get_object_or_404(Structure, pk=sid, user=request.user)
        s.name, s.data, s.formula, s.molar_mass, s.is_public = name, payload, formula, mm, bool(data.get('is_public'))
        s.save()
    else:
        s = Structure.objects.create(user=request.user, name=name, data=payload, formula=formula, molar_mass=mm,
                                     is_public=bool(data.get('is_public')))
        log_activity(request.user, 'structure', f'Saved structure {name} ({formula})', f'/structure-lab/?id={s.id}')
    return JsonResponse({'ok': True, 'id': s.id, 'formula': formula, 'molar_mass': mm, 'name': s.name})


@login_required
@require_POST
def delete(request, pk):
    s = get_object_or_404(Structure, pk=pk, user=request.user)
    s.delete()
    messages.info(request, f'“{s.name}” deleted.')
    return redirect('molecular_structure:gallery')


def api_structure(request, pk):
    s = _visible(request).filter(pk=pk).first()
    if not s:
        return bad('Not found', 404)
    return JsonResponse({'id': s.id, 'name': s.name, 'formula': s.formula, 'molar_mass': s.molar_mass, 'data': s.data})
