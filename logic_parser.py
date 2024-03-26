import re

class Expression:
    def __init__(self, token):
        self.token = token
    # TODO: __str__
    # TODO: simplify
    def __str__(self):
        return ""

    def simplify(self):
        return self

class VariableExpression(Expression):
    def __init__(self, symbol):
        self.symbol = symbol
    def __str__(self):
        return self.symbol

class PredicateExpression(Expression):
    def __init__(self, symbol, var_nodes: list[VariableExpression]):
        self.var_nodes = var_nodes
        self.symbol = symbol
    def __str__(self):
        return f'{self.symbol}({", ".join(map(lambda x: x.symbol, self.var_nodes))})'

class AndExpression(Expression):
    def __init__(self, left_operand, right_operand):
        self.left = left_operand
        self.right = right_operand
        self.token = '&'
    
    def __str__(self):
        return f'({self.left}) & ({self.right})'
    
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self

class OrExpression(Expression):
    def __init__(self, left_operand, right_operand):
        self.left = left_operand
        self.right = right_operand
        self.token = '|'
    
    def __str__(self):
        return f'({self.left}) | ({self.right})'
    
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self

class NegationExpression(Expression):
    def __init__(self, operand):
        self.operand = operand
        self.token = '-'
    
    def __str__(self):
        return f'-({self.operand})'
    
    def simplify(self):
        if isinstance(self.operand, NegationExpression):
            return self.operand.operand.simplify()
        return self.operand.simplify()

class ExistsExpression(Expression):
    def __init__(self, variable, formula):
        self.variable = variable
        self.formula = formula
        self.token = 'exists'
    
    def __str__(self):
        return f'exists {self.variable} ({self.formula})'
    
    def simplify(self):
        self.formula = self.formula.simplify()
        return self

class ImplicationExpression(Expression):
    def __init__(self, left_operand, right_operand):
        self.left = left_operand
        self.right = right_operand
        self.token = '->'

    def __str__(self):
        return f'({self.left}) -> ({self.right})'

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self

class AllExpression(Expression):
    def __init__(self, variable, formula):
        self.variable = variable
        self.formula = formula
        self.token = 'all'

    def __str__(self):
        return f'all {self.variable} ({self.formula})'

    def simplify(self):
        self.formula = self.formula.simplify()
        return self

class EquivalenceExpression(Expression):
    def __init__(self, left_operand, right_operand):
        self.left = left_operand
        self.right = right_operand
        self.token = '<->'

    def __str__(self):
        return f'({self.left}) <-> ({self.right})'

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self & AndExpression(ImplicationExpression(self.left, self.right), ImplicationExpression(self.right, self.left))


class Tokens:
    class Token:
        def __init__(self, type, value = None) -> None:
            self.type = type
            self.value = value
        def __str__(self):
            if self.type == Tokens.IDENTIFIER:
                return f'{self.type}({self.value})'
            return self.type
    IDENTIFIER = "Identifier"
    EXISTS = "exists"
    ALL = "all"
    OPEN = "("
    CLOSE = ")"
    COMMA = ","
    NOT = "-"
    AND = "&"
    OR = "|"
    IMP = "->"
    IFF = "<->"
    BINOPS = [AND, OR, IMP, IFF]
    QUANTS = [ALL, EXISTS]
    PUNCT = [ OPEN, CLOSE, COMMA]

    TOKENS = QUANTS + PUNCT + BINOPS + [NOT]

    # Special
    SYMBOLS = [x for x in TOKENS if re.match(r"^[-\\.(),!&^|>=<]*$", x)]


class LogicParser:
    def __init__(self, expression: str) -> None:
        self.expression = expression

        self.tokens = self.tokenize(self.expression)
        self.operator_precedence = [
            Tokens.NOT,
            Tokens.QUANTS,
            Tokens.AND,
            Tokens.OR,
            Tokens.IMP,
            Tokens.IFF,
        ]

    def tokenize(self, expression: str) -> list[Tokens.Token]:
        tokens = []
        while len(expression) > 0:
            expression = expression.strip()
            found = False
            for token in Tokens.TOKENS:
                if expression.startswith(token):
                    tokens.append(Tokens.Token(type=token))
                    expression = expression[len(token):]
                    found = True
                    break; 
            if not found:
                match = re.match(r'^[a-zA-Z0-9]+', expression)
                if match:
                    tokens.append(Tokens.Token(Tokens.IDENTIFIER, value= match.group()))
                    expression = expression[len(match.group()):].strip()
                else:
                    print(tokens)
                    raise ValueError("Invalid expression")
        return tokens

    def consume_token(self, type):
        if(self._current_index >= len(self.tokens)) or self.tokens[self._current_index].type != type:
            raise Exception(f"Missing Token of type({type})")
        t = self.tokens[self._current_index]
        self._current_index += 1;
        return t
    
    def token(self, location = None) -> Tokens.Token:
        try:
            if location is None:
                tok = self._buffer[self._currentIndex]
                self._currentIndex += 1
            else:
                tok = self._buffer[self._currentIndex + location]
            return tok
        except IndexError as e:
            raise Exception(f"Ran out of tokens at index {self._currentIndex + 1}")

    def parse(self) -> Expression:
        self._current_index = 0;
        expr = self.parse_expression()
        return expr
    
    def parse_expression(self) -> Expression:
        #get next token
        tok = self.token()
        if tok.type == Tokens.IDENTIFIER:
            self.handle_identifier(tok)
        elif tok.type == Tokens.NOT:
            self.parse_negation(tok)
        elif tok.type in Tokens.QUANTS:
            self.parse_quantifier(tok)
        elif tok.type == Tokens.OPEN:
            self.parse_open(tok)
        raise Exception("didn't expect to be here")
    
    def handle_identifier(self, tok: Tokens.Token):
        # It's either: 1) a predicate expression: sees(x,y)
        #             2) an application expression: P(x)
        #             3) a solo variable: john OR x
        return VariableExpression(symbol=tok.value)
    def parse_negation(self, tok: Tokens.Token):
        return NegationExpression(self.parse_expression())
    def parse_quantifier(self, tok: Tokens.Token):
        pass
    def parse_quantifier(self, tok: Tokens.Token):
        pass