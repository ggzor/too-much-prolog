from dataclasses import dataclass
from typing import cast
from functools import reduce
import operator
import itertools
import re


@dataclass(frozen=True, order=True)
class Var:
    name: str

    def free_vars(self):
        return {self}

    def replace(self, subst: "Substitutions"):
        return subst.get(self, self)

    def __str__(self):
        return self.name


@dataclass
class Func:
    name: str
    terms: list["Term"]

    def free_vars(self):
        return reduce(operator.or_, map(lambda x: x.free_vars(), self.terms), set())

    def replace(self, subst: "Substitutions"):
        for i in range(len(self.terms)):
            self.terms[i] = self.terms[i].replace(subst)
        return self

    def __str__(self):
        if self.terms:
            return f"{self.name}({', '.join(map(str, self.terms))})"
        else:
            return self.name


Term = Var | Func


@dataclass
class Equation:
    lhs: Term
    rhs: Term

    def replace(self, subst: "Substitutions"):
        self.lhs = self.lhs.replace(subst)
        self.rhs = self.rhs.replace(subst)
        return self

    def __str__(self):
        return f"{self.lhs} = {self.rhs}."


Substitutions = dict[Var, Term]


def unify(equations: list[Equation]) -> dict[Var, Term] | None:
    subst: dict[Var, Term] = {}

    while equations:
        item = equations.pop()
        match (item.lhs, item.rhs):
            # delete
            case (t1, t2) if t1 == t2:
                pass
            case (Func(n1, t1), Func(n2, t2)):
                # decompose
                if n1 == n2:
                    equations.extend(map(Equation, t1, t2))
                # conflict
                else:
                    return None
            # swap
            case (Func() as f, Var() as x):
                equations.append(Equation(x, f))
            # eliminate
            case (Var() as x, t) if not x in t.free_vars():
                subst[x] = t
                for item in itertools.chain(equations, subst.values()):
                    item.replace(subst)
            case (Var(), Func()):
                return None

    return subst


# Lexing and parsing


def lex(s: str):
    TOKEN_RE = re.compile(r"\s*((?:\w|\d|[_])+)|([\.\(\)=,])")
    for ident, op in TOKEN_RE.findall(s):
        if ident:
            if ident.isupper():
                yield "var", ident
            else:
                yield "ident", ident
        elif op:
            yield op, None


EOF = None, None
ParseError = RuntimeError("Parse error")


class Parser:
    def __init__(self, tokens: list[tuple[str, str]]):
        self.tokens = tokens
        self.cursor = 0

    @property
    def eof(self):
        return self.cursor >= len(self.tokens)

    @property
    def current(self):
        if self.eof:
            return EOF
        else:
            return self.tokens[self.cursor]

    @property
    def previous(self):
        if self.cursor == 0 or self.eof:
            return EOF
        return self.tokens[self.cursor - 1]

    def advance(self):
        self.cursor += 1

    def check(self, ty):
        return self.current[0] == ty

    def match(self, expected):
        ty, _ = self.current
        if ty == expected:
            self.advance()
            return True
        return False

    def consume(self, ty):
        if self.check(ty):
            self.advance()
        else:
            raise ParseError

    def functor(self):
        name = cast(str, self.previous[1])
        terms = []
        if self.match("("):
            terms.append(self.term())
            while not self.check(")"):
                self.consume(",")
                terms.append(self.term())
            self.consume(")")
        return Func(name, terms)

    def term(self) -> Term:
        if self.match("ident"):
            return self.functor()
        elif self.match("var"):
            return Var(cast(str, self.previous[1]))
        else:
            raise ParseError

    def statement(self):
        lhs = self.term()
        self.consume("=")
        rhs = self.term()
        self.consume(".")
        return Equation(lhs, rhs)

    def parse(self):
        result: list[Equation] = []
        while self.cursor < len(self.tokens):
            result.append(self.statement())
        return result


def solve(input: str):
    return unify(Parser(list(lex(INPUT1))).parse())


if __name__ == "__main__":
    INPUT1 = """
    cons(X, cons(X, nil)) = cons(2, Y).
    """

    result = solve(INPUT1)
    if result is None:
        print("No solution was found")
    else:
        for k, v in sorted(list(result.items())):
            print(Equation(k, v))
