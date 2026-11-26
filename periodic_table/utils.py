ORDER = ['1s', '2s', '2p', '3s', '3p', '4s', '3d', '4p', '5s', '4d', '5p', '6s', '4f', '5d', '6p', '7s', '5f', '6d', '7p']
CAP = {'s': 2, 'p': 6, 'd': 10, 'f': 14}
# Well-known exceptions where s electrons move into the d subshell
S_TO_D = {24: 1, 29: 1, 41: 1, 42: 1, 44: 1, 45: 1, 47: 1, 78: 1, 79: 1, 46: 2}
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')


def electron_configuration(z):
    """Aufbau-order configuration with the common d-block exceptions. f-block exceptions are not modelled."""
    left, filled = z, []
    for orb in ORDER:
        if left <= 0:
            break
        n = min(CAP[orb[-1]], left)
        filled.append([orb, n])
        left -= n
    move = S_TO_D.get(z)
    if move:
        s_orb = next(o for o in reversed(filled) if o[0].endswith('s'))
        d_orb = next((o for o in filled if o[0] == f'{int(s_orb[0][0]) - 1}d'), None)
        if d_orb:
            s_orb[1] -= move
            d_orb[1] += move
    return ' '.join(f'{o}{str(n).translate(SUP)}' for o, n in filled if n > 0)


def shells(z):
    cfg = electron_configuration(z).translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789'))
    out = {}
    for part in cfg.split():
        out[int(part[0])] = out.get(int(part[0]), 0) + int(part[2:])
    return [out[k] for k in sorted(out)]
