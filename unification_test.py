import pytest

from prolog import Term, Var, parse, unify

# Taken from: https://en.m.wikipedia.org/wiki/Unification_(computer_science)
WIKI_CASES = [
    (
        "a = a.",
        "",
    ),
    (
        "a = b.",
        None,
    ),
    (
        "X = X.",
        "",
    ),
    (
        "a = X.",
        "X = a.",
    ),
    (
        "X = Y.",
        "X = Y.",
    ),
    (
        "f(a, X) = f(a, b).",
        "X = b.",
    ),
    (
        "f(a) = g(a).",
        None,
    ),
    (
        "f(X) = f(Y).",
        "X = Y.",
    ),
    (
        "f(X) = g(Y).",
        None,
    ),
    (
        "f(X) = f(Y, Z).",
        None,
    ),
    (
        "f(g(X)) = f(Y).",
        "Y = g(X).",
    ),
    (
        "f(g(X), X) = f(Y, a).",
        "X = a. Y = g(a).",
    ),
    (
        "X = f(X).",
        None,
    ),
    (
        "X = Y. Y = a.",
        "X = a. Y = a.",
    ),
    (
        "a = Y. X = Y.",
        "X = a. Y = a.",
    ),
    (
        "X = a. b = X.",
        None,
    ),
]

TRICKY_CASES = [
    (
        "Order of evaluation should not matter",
        "X = f(a, b). g(X, y) = g(Z, y).",
        "X = f(a, b). Z = f(a, b).",
    ),
    (
        "No terms",
        "X = Y.",
        "X = Y.",
    ),
    (
        "No terms, but transitive.",
        "X = Y. Y = Z.",
        "X = Z. Y = Z.",
    ),
]


SAMPLE_CASES = [
    (
        "cons(X, cons(X, nil)) = cons(2, Y).",
        "X = 2. Y = cons(2, nil).",
    ),
]


def tag_cases(tag, cases):
    return [(f"{tag} {i}", x, y) for i, (x, y) in enumerate(cases, start=1)]


CASES = (
    tag_cases("Wiki cases", WIKI_CASES)
    + TRICKY_CASES
    + tag_cases("Sample case", SAMPLE_CASES)
)

test_cases = [pytest.param(inp, out, id=name) for name, inp, out in CASES]


SubstitutionsList = list[tuple[Var, Term]] | None


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

    print(result)
    print(expected)
    assert result == expected
