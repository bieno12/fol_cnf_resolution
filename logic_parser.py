import re

class FOLNode:
    def __init__(self, token):
        self.token = token
    # TODO: __str__
    # TODO: simplify
    def __str__(self):
        return ""

    def simplify(self):
        return self

class VariableNode(FOLNode):
    def __init__(self, symbol):
        self.symbol = symbol
    def __str__(self):
        return self.symbol

class PredicateNode(FOLNode):
    def __init__(self, symbol, var_nodes: list[VariableNode]):
        self.var_nodes = var_nodes
        self.symbol = symbol
    def __str__(self):
        return f'{self.symbol}({", ".join(map(lambda x: x.symbol, self.var_nodes))})'

class AndNode(FOLNode):
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

class OrNode(FOLNode):
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

class NegateNode(FOLNode):
    def __init__(self, operand):
        self.operand = operand
        self.token = '-'
    
    def __str__(self):
        return f'-({self.operand})'
    
    def simplify(self):
        if isinstance(self.operand, NegateNode):
            return self.operand.operand.simplify()
        return self.operand.simplify()

class ExistsNode(FOLNode):
    def __init__(self, variable, formula):
        self.variable = variable
        self.formula = formula
        self.token = 'exists'
    
    def __str__(self):
        return f'exists {self.variable} ({self.formula})'
    
    def simplify(self):
        self.formula = self.formula.simplify()
        return self

class ImplicationNode(FOLNode):
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

class AllNode(FOLNode):
    def __init__(self, variable, formula):
        self.variable = variable
        self.formula = formula
        self.token = 'all'

    def __str__(self):
        return f'all {self.variable} ({self.formula})'

    def simplify(self):
        self.formula = self.formula.simplify()
        return self

class EquivalenceNode(FOLNode):
    def __init__(self, left_operand, right_operand):
        self.left = left_operand
        self.right = right_operand
        self.token = '<->'

    def __str__(self):
        return f'({self.left}) <-> ({self.right})'

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self & AndNode(ImplicationNode(self.left, self.right), ImplicationNode(self.right, self.left))



class Tokens:

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
    
    def tokenize(expression: str):
        tokens = []
        while len(expression) > 0:
            expression = expression.strip()
            found = False
            for token in Tokens.TOKENS:
                if expression.startswith(token):
                    tokens.append(token)
                    expression = expression[len(token):].strip()
                    found = True
                    break; 
            if not found:
                # Handle other cases, like identifiers or numbers
                # Here you need to define how to extract them
                # For simplicity, let's assume identifiers can be alphanumeric
                match = re.match(r'^[a-zA-Z0-9]+', expression)
                if match:
                    tokens.append(match.group())
                    expression = expression[len(match.group()):].strip()
                else:
                    print(tokens)
                    raise ValueError("Invalid expression")
        return tokens
