import pytest

from prolog import Term, Var, parse, unify

SubstitutionsList = list[tuple[Var, Term]] | None


BASE_CASES = [
    (
        "Simple var",
        "X = 10.",
        "X = 10.",
    ),
    (
        "No substitutions",
        "a = a.",
        "",
    ),
    (
        "Decomposition",
        "f(A, B, C) = f(a, b, c).",
        "A = a. B = b. C = c.",
    ),
    (
        "Conflict: Wrong functor",
        "f(x, y) = g(x, y).",
        None,
    ),
    (
        "Conflict: Arity mismatch",
        "f(x, y) = f(x).",
        None,
    ),
    (
        "Swap",
        "f(a, b) = X.",
        "X = f(a, b).",
    ),
    (
        "Eliminate",
        "g(X, y) = g(Z, y). X = f(a, b).",
        "X = f(a, b). Z = f(a, b).",
    ),
    (
        "Occurs check",
        "X = f(a, X).",
        None,
    ),
]


CASES = BASE_CASES

test_cases = [pytest.param(inp, out, id=name) for name, inp, out in CASES]


@pytest.mark.parametrize("input_str,expected_str", test_cases)
def test_unification(input_str: str, expected_str: str | None):
    result_dict = unify(parse(input_str))

    result: SubstitutionsList = None
    if result_dict is not None:
        result = sorted(list(result_dict.items()))

    expected: SubstitutionsList = None
    if expected_str is not None:
        expected = []
        for eq in parse(expected_str):
            if isinstance(eq.lhs, Var):
                expected.append((eq.lhs, eq.rhs))
            else:
                pytest.fail("Expected outputs must have only vars on its left")
        expected.sort()

    assert result == expected
