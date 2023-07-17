# Based on https://gist.github.com/versesrev/0f994f70c6de20344f6f44893adb80b0
from dataclasses import dataclass
from typing import Any, Callable, List, Mapping

SOLVER_PATH = 'https://raw.githubusercontent.com/rkm0959/Inequality_Solving_with_CVP/main/solver.sage'
# SOLVER_PATH = 'rkm_solver.sage'

@dataclass
class Constraint:
    """ Constraint on a linear function
    The corresponding formula is:
        lower_bound <= sum(coefficients[var] * var, for all var) <= upper_bound
    """
    coefficients: Mapping[str, int]
    lower_bound: int
    upper_bound: int

    def __str__(self):
        formula = ' + '.join(f'{c}*{x}' for x, c in self.coefficients.items())
        return f'{self.lower_bound} <= {formula} <= {self.upper_bound}'


def constraints_to_lattice(
    constraints: List[Constraint],
    debug: bool = False
) -> (List[List[int]], List[str]):
    from itertools import chain

    if debug:
        print('constraints = [')
        print(',\n'.join(f'\t{c}' for c in constraints))
        print(']')

    variables = sorted(list(set(chain.from_iterable(
        c.coefficients.keys() for c in constraints
    ))))

    lattice = [[0] * len(constraints) for _ in range(len(variables))]
    for i, c in enumerate(constraints):
        for var, coef in c.coefficients.items():
            lattice[variables.index(var)][i] = coef

    if debug:
        print(f'variables = {variables}')
        print(f'lattice_nrows = {len(variables)} variables')
        print(f'lattice_ncols = {len(constraints)} constraints')
        print('lattice =')
        for row in lattice:
            print(''.join('*' if v else '.' for v in row))

    return lattice, variables


# ===== rkm solver =====


def load_rkm_solver(
    filename: str = None
) -> Callable:
    """ Load rkm's solver without overwriting solve() in globals() """
    from copy import copy

    if filename is None:
        print('No solver source provided.')
        filename = 'https://raw.githubusercontent.com/rkm0959/Inequality_Solving_with_CVP/main/solver.sage'  # noqa
    context = copy(globals())
    sage.repl.load.load(filename, context)
    return context['solve']


def rkm_wrapper(
    constraints: List[Constraint],
    debug: bool = False,
    solver: Callable = load_rkm_solver(filename=SOLVER_PATH),
    **kwargs: Any,
) -> Mapping[str, int]:
    """ Wrapper for rkm's inequalities solver """
    lattice, variables = constraints_to_lattice(constraints, debug)

    # Call solver
    if debug:
        print('Start solving...')
    weighted_close_vec, weights, sol_vec = \
        solver(matrix(lattice),
               [c.lower_bound for c in constraints],
               [c.upper_bound for c in constraints],
               **kwargs)

    # Get solution
    if sol_vec is None:
        weighted_lattice = matrix(lattice) * matrix.diagonal(weights)
        H, U = weighted_lattice.hermite_form(transformation=True)
        sol_vec = H.solve_left(weighted_close_vec).change_ring(ZZ) * U
    solution = dict(zip(variables, sol_vec))
    if debug:
        print(f'solution = {solution}')

    # Check solution
    for c in constraints:
        coefs, lb, ub = c.coefficients, c.lower_bound, c.upper_bound
        val = sum(coef * solution[var] for var, coef in coefs.items())
        if not lb <= val <= ub:
            raise Exception('Constrained value out-of-bound, '
                            f'lb={lb}, ub={ub}, value={val}, coefs={coefs}, '
                            f'solution={solution}')

    return solution

def match_strings(s1, s2, p):
    """
    s1, s2 = encoded strings with holes represented by b'?' (strings) and b'#' (numbers)
    p = prime number

    return = s1, s2 such that the ?/# are filled and s1-s2 == 0 (mod p)
    """

    # Check strings are bytes
    if type(s1) == str: s1 = s1.encode()
    if type(s2) == str: s2 = s2.encode()

    a_vars = []
    b_vars = []
    constraints = []

    a_string = []
    b_string = []

    final_coeffs = {}
    final_sum = 0
    
    # First string to constraints
    for i, c in enumerate(s1[::-1]):
        if c == ord('?'): # '?' -> fill the hole with a printable ascii
            a_vars.append(f'a_{len(a_vars)}')
            a_string.append(a_vars[-1])
            constraints.append(Constraint({a_vars[-1]:1}, 32, 126))
            final_coeffs[a_vars[-1]] = 2**(8*i)
        
        elif c == ord('#'): # '#' -> fill the hole with a number
            a_vars.append(f'a_{len(a_vars)}')
            a_string.append(a_vars[-1])
            constraints.append(Constraint({a_vars[-1]:1}, 48, 57))
            final_coeffs[a_vars[-1]] = 2**(8*i)

        else: # Otherwise keep the current char
            a_string.append(chr(c))
            final_sum += c * 2**(8*i)

     # Second string to constraints (change sign)
    for i, c in enumerate(s2[::-1]):
        if c == ord('?'): # '?' -> fill the hole with a printable ascii
            b_vars.append(f'b_{len(b_vars)}')
            b_string.append(b_vars[-1])
            constraints.append(Constraint({b_vars[-1]:1}, 32, 126))
            final_coeffs[b_vars[-1]] = -(2**(8*i))

        elif c == ord('#'): # '#' -> fill the hole with a number
            b_vars.append(f'b_{len(b_vars)}')
            b_string.append(b_vars[-1])
            constraints.append(Constraint({b_vars[-1]:1}, 48, 57))
            final_coeffs[b_vars[-1]] = -(2**(8*i))

        else: # Otherwise keep the current char
            b_string.append(chr(c))
            final_sum -= c * 2**(8*i)

    final_coeffs['z'] = p # modulo equality
    constraints.append(Constraint(final_coeffs, -final_sum, -final_sum))
    
    solver = load_rkm_solver(filename='rkm_solver.sage')
    solution = rkm_wrapper(constraints, debug=False, solver=solver)
    
    # Print the solution
    # print(f'a = {[solution[x] for x in a_vars]}')
    # print(f'b = {[solution[x] for x in b_vars]}')
    # print(f'z = {[solution["z"]]}')

    # Rebuild string
    s1 = ''
    for c in a_string:
        if len(c) == 1:
            s1 = c + s1
        else:
            s1 = chr(solution[c]) + s1

    s2 = ''
    for c in b_string:
        if len(c) == 1:
            s2 = c + s2
        else:
            s2 = chr(solution[c]) + s2

    s1 = s1.encode()
    s2 = s2.encode()
    return s1, s2



if __name__ == '__main__':
    p = 26189572440233739420990528170531051459310363621928135990243626537967
    s1 = b'{"admin": 1################################}'
    s2 = b'{"username": "????????????????????????????????", "admin": false}'

    s1, s2 = match_strings(s1, s2, p)
    print(f'{s1 = }')
    print(f'{s2 = }')