"""CHEMVERSE chemistry engine: formula parsing, molar mass, equation balancing with explanations."""
import json
import re
from fractions import Fraction
from functools import lru_cache, reduce
from math import gcd

from django.conf import settings


class ChemError(ValueError):
    pass


@lru_cache(maxsize=None)
def load_seed(name):
    with open(settings.SEED_DIR / name, encoding='utf-8') as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def atomic_masses():
    return {e['symbol']: e['atomic_mass'] for e in load_seed('elements.json')}


def _read_num(s, i):
    j = i
    while j < len(s) and s[j].isdigit():
        j += 1
    return (int(s[i:j]) if j > i else 1), j


def _parse_group(s):
    stack, i = [{}], 0
    while i < len(s):
        ch = s[i]
        if ch in '([':
            stack.append({})
            i += 1
        elif ch in ')]':
            if len(stack) == 1:
                raise ChemError('Unmatched closing bracket')
            num, i = _read_num(s, i + 1)
            for el, n in stack.pop().items():
                stack[-1][el] = stack[-1].get(el, 0) + n * num
        elif ch.isupper():
            j = i + 1
            while j < len(s) and s[j].islower():
                j += 1
            num, k = _read_num(s, j)
            stack[-1][s[i:j]] = stack[-1].get(s[i:j], 0) + num
            i = k
        else:
            raise ChemError(f"Unexpected character '{ch}' in formula")
    if len(stack) != 1:
        raise ChemError('Unclosed bracket in formula')
    return stack[0]


def parse_formula(formula):
    """'Ca(OH)2' -> {'Ca': 1, 'O': 2, 'H': 2}. Supports brackets and hydrates such as CuSO4·5H2O."""
    formula = (formula or '').strip().replace(' ', '')
    if not formula:
        raise ChemError('Formula is empty')
    if len(formula) > 60:
        raise ChemError('Formula is too long')
    total = {}
    for part in re.split(r'[·.*]', formula):
        if not part:
            continue
        mult = 1
        m = re.match(r'^(\d+)(.+)$', part)
        if m:
            mult, part = int(m.group(1)), m.group(2)
        for el, n in _parse_group(part).items():
            total[el] = total.get(el, 0) + n * mult
    unknown = [el for el in total if el not in atomic_masses()]
    if unknown:
        raise ChemError('Unknown element symbol: ' + ', '.join(unknown))
    return total


def molar_mass(formula):
    return round(sum(atomic_masses()[el] * n for el, n in parse_formula(formula).items()), 3)


def composition(formula):
    counts = parse_formula(formula)
    masses = atomic_masses()
    total = sum(masses[el] * n for el, n in counts.items())
    rows = [{'element': el, 'count': n, 'atomic_mass': masses[el], 'mass': round(masses[el] * n, 3),
             'percent': round(100 * masses[el] * n / total, 2)} for el, n in counts.items()]
    return {'formula': formula.strip(), 'molar_mass': round(total, 3), 'atoms': sum(counts.values()), 'rows': rows}


ARROW = re.compile(r'\s*(?:->|→|=>|=)\s*')


def split_equation(equation):
    parts = ARROW.split((equation or '').strip())
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ChemError("Write the equation as 'A + B -> C + D'")
    left = [s.strip() for s in parts[0].split('+') if s.strip()]
    right = [s.strip() for s in parts[1].split('+') if s.strip()]
    if not left or not right:
        raise ChemError('Both sides need at least one substance')
    if len(left) + len(right) > 10:
        raise ChemError('Too many substances (max 10)')
    return left, right


def strip_coefficient(species):
    m = re.match(r'^(\d+)\s*([A-Z(\[].*)$', species.strip())
    if m:
        return int(m.group(1)), m.group(2).strip()
    return 1, species.strip()


def _solve(matrix):
    """Return (fraction_vector_with_last_free_var_1, integer_vector)."""
    rows, cols = len(matrix), len(matrix[0])
    A = [[Fraction(x) for x in r] for r in matrix]
    pivots, r = [], 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    free = [c for c in range(cols) if c not in pivots]
    if len(free) != 1:
        raise ChemError('This equation cannot be balanced in a unique way. Check the formulas and sides.')
    fc = free[0]
    vec = [Fraction(0)] * cols
    vec[fc] = Fraction(1)
    for i, pc in enumerate(pivots):
        vec[pc] = -A[i][fc]
    if all(v <= 0 for v in vec):
        vec = [-v for v in vec]
    if any(v <= 0 for v in vec):
        raise ChemError('No positive solution – a substance may be on the wrong side, or the reaction is impossible as written.')
    lcm = reduce(lambda a, b: a * b // gcd(a, b), [v.denominator for v in vec], 1)
    ints = [int(v * lcm) for v in vec]
    g = reduce(gcd, ints)
    return vec, [v // g for v in ints], lcm


def _fmt(c, s):
    return (str(c) if c != 1 else '') + s


def balance_equation(equation):
    left, right = split_equation(equation)
    left = [strip_coefficient(s)[1] for s in left]
    right = [strip_coefficient(s)[1] for s in right]
    species = left + right
    parsed = [parse_formula(s) for s in species]
    elements = sorted({el for p in parsed for el in p})
    nl = len(left)
    matrix = [[p.get(el, 0) for p in parsed[:nl]] + [-p.get(el, 0) for p in parsed[nl:]] for el in elements]
    fracs, coeffs, lcm = _solve(matrix)
    letters = 'abcdefghij'
    lc, rc = coeffs[:nl], coeffs[nl:]
    balanced = ' + '.join(_fmt(c, s) for c, s in zip(lc, left)) + ' → ' + ' + '.join(_fmt(c, s) for c, s in zip(rc, right))

    # ---- step-by-step explanation ----
    steps = []
    steps.append({'title': 'Identify reactants and products',
                  'text': 'Reactants: ' + ', '.join(left) + '. Products: ' + ', '.join(right) + '.'})
    count_rows = [{'species': s, 'side': 'Reactant' if i < nl else 'Product',
                   'counts': ', '.join(f'{el}: {n}' for el, n in parsed[i].items())} for i, s in enumerate(species)]
    steps.append({'title': 'Count the atoms in each formula', 'rows': count_rows})
    unknown = ' + '.join(f'{letters[i]}·{s}' for i, s in enumerate(left)) + ' → ' + \
              ' + '.join(f'{letters[nl + i]}·{s}' for i, s in enumerate(right))
    steps.append({'title': 'Give every substance an unknown coefficient', 'text': unknown})
    eqs = []
    for el in elements:
        lhs = ' + '.join(f"{parsed[i][el] if parsed[i][el] != 1 else ''}{letters[i]}" for i in range(nl) if el in parsed[i]) or '0'
        rhs = ' + '.join(f"{parsed[i][el] if parsed[i][el] != 1 else ''}{letters[i]}" for i in range(nl, len(species)) if el in parsed[i]) or '0'
        eqs.append(f'{el}:  {lhs} = {rhs}')
    steps.append({'title': 'Write one equation per element (atoms are conserved)', 'lines': eqs})
    steps.append({'title': 'Solve the equations, setting one coefficient to 1',
                  'lines': [f'{letters[i]} = {f}' for i, f in enumerate(fracs)]})
    if lcm != 1:
        steps.append({'title': f'Multiply every coefficient by {lcm} to remove fractions',
                      'lines': [f'{letters[i]} = {c}' for i, c in enumerate(coeffs)]})
    else:
        steps.append({'title': 'All coefficients are already whole numbers',
                      'lines': [f'{letters[i]} = {c}' for i, c in enumerate(coeffs)]})
    table = []
    for el in elements:
        l_cnt = sum(c * p.get(el, 0) for c, p in zip(lc, parsed[:nl]))
        r_cnt = sum(c * p.get(el, 0) for c, p in zip(rc, parsed[nl:]))
        table.append({'element': el, 'left': l_cnt, 'right': r_cnt})
    steps.append({'title': 'Check: every element has the same count on both sides', 'table': table})
    return {'input': equation, 'balanced': balanced, 'coefficients': coeffs, 'reactants': list(zip(lc, left)),
            'products': list(zip(rc, right)), 'table': table, 'steps': steps}


def check_balance(equation):
    """Check the equation exactly as written, coefficients included. Returns (is_balanced, table)."""
    left, right = split_equation(equation)
    counts = [{}, {}]
    for side, items in enumerate((left, right)):
        for s in items:
            c, f = strip_coefficient(s)
            for el, n in parse_formula(f).items():
                counts[side][el] = counts[side].get(el, 0) + c * n
    els = sorted(set(counts[0]) | set(counts[1]))
    table = [{'element': e, 'left': counts[0].get(e, 0), 'right': counts[1].get(e, 0)} for e in els]
    return all(r['left'] == r['right'] for r in table), table


def hill_formula(counts):
    """{'C':2,'H':6,'O':1} -> 'C2H6O' (Hill order: C, H, then alphabetical)."""
    keys = list(counts)
    order = (['C', 'H'] if 'C' in counts else []) + sorted(k for k in keys if not ('C' in counts and k in ('C', 'H')))
    return ''.join(f"{el}{counts[el] if counts[el] > 1 else ''}" for el in order if counts.get(el))
