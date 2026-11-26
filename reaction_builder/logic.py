"""Validation, classification and explanations for user-built reactions."""
from config.chem import ChemError, balance_equation, check_balance, molar_mass, parse_formula, strip_coefficient

TYPE_INFO = {
    'synthesis': 'Synthesis (combination): two or more substances combine to form one product. A + B → AB.',
    'decomposition': 'Decomposition: one substance breaks down into two or more simpler substances. AB → A + B. Usually needs heat, light or electricity.',
    'single': 'Single displacement: a more reactive element replaces a less reactive one in a compound. A + BC → AC + B.',
    'double': 'Double displacement: two compounds swap partners, often forming a precipitate, gas or water. AB + CD → AD + CB.',
    'combustion': 'Combustion: a fuel reacts with oxygen, releasing heat and light. Hydrocarbons give carbon dioxide and water.',
    'neutralisation': 'Neutralisation: an acid reacts with a base to form a salt and water.',
    'redox': 'Redox: one substance is oxidised (loses electrons) while another is reduced (gains electrons).',
    'other': 'This reaction does not fit one simple pattern – many real reactions combine several types.',
}


def parse_side(text):
    """'2H2 + O2' -> [{'coef': 2, 'formula': 'H2'}, {'coef': 1, 'formula': 'O2'}]"""
    items = [s.strip() for s in (text or '').split('+') if s.strip()]
    if not items:
        raise ChemError('Add at least one substance.')
    if len(items) > 6:
        raise ChemError('Use at most 6 substances per side.')
    out = []
    for s in items:
        c, f = strip_coefficient(s)
        if c < 1 or c > 99:
            raise ChemError(f'Coefficient {c} is out of range (1–99).')
        parse_formula(f)  # validates
        out.append({'coef': c, 'formula': f})
    return out


def side_text(items):
    return ' + '.join((str(i['coef']) if i['coef'] != 1 else '') + i['formula'] for i in items)


def equation_text(reactants, products):
    return side_text(reactants) + ' -> ' + side_text(products)


def _is_element(f):
    return len(parse_formula(f)) == 1


def _is_acid(f):
    if f in ('H2', 'H2O', 'H2O2'):
        return False
    return (f.startswith('H') and len(parse_formula(f)) > 1) or f.endswith('COOH')


def _is_base(f):
    return f == 'NH3' or (f.endswith('OH') and not f.endswith('COOH') and not f.startswith('C')) or f.endswith('(OH)2') or f.endswith('(OH)3')


def classify(reactants, products):
    r = [i['formula'] for i in reactants]
    p = [i['formula'] for i in products]
    if 'O2' in r and 'CO2' in p and 'H2O' in p:
        return 'combustion', 'Oxygen is a reactant and the products are CO₂ and H₂O.'
    if any(_is_acid(f) for f in r) and any(_is_base(f) for f in r) and 'H2O' in p:
        return 'neutralisation', 'An acid and a base react and water is produced.'
    if len(r) >= 2 and len(p) == 1:
        return 'synthesis', 'Several reactants form a single product.'
    if len(r) == 1 and len(p) >= 2:
        return 'decomposition', 'A single reactant breaks into several products.'
    if len(r) == 2 and len(p) == 2:
        er, ep = sum(_is_element(f) for f in r), sum(_is_element(f) for f in p)
        if er == 1 and ep == 1:
            return 'single', 'An element and a compound give a different element and compound.'
        if er == 0 and ep == 0:
            return 'double', 'Two compounds exchange their parts.'
    return 'other', 'No simple pattern detected.'


def analyse(reactants, products):
    eq = equation_text(reactants, products)
    ok, table = check_balance(eq)
    suggestion, suggestion_error = None, None
    if not ok:
        try:
            suggestion = balance_equation(eq)['balanced']
        except ChemError as exc:
            suggestion_error = str(exc)
    masses = []
    tot = [0.0, 0.0]
    for side, items in enumerate((reactants, products)):
        for i in items:
            m = molar_mass(i['formula'])
            masses.append({'side': 'Reactant' if side == 0 else 'Product', 'formula': i['formula'], 'coef': i['coef'],
                           'molar_mass': m, 'total': round(m * i['coef'], 3)})
            tot[side] += m * i['coef']
    kind, why = classify(reactants, products)
    return {'equation': eq, 'is_balanced': ok, 'table': table, 'suggestion': suggestion,
            'suggestion_error': suggestion_error, 'masses': masses,
            'mass_left': round(tot[0], 3), 'mass_right': round(tot[1], 3),
            'detected_type': kind, 'detected_reason': why, 'type_info': TYPE_INFO[kind]}
