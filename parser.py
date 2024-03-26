class FOLNode:
    def __init__(self, token):
        self.token = token
    # TODO: __str__
    # TODO: simplify
    def __str__(self):
        pass

    def simplify(self):
        pass

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
        return f'{self.symbol}({self.var_nodes.join(', ')})'


class AndNode(FOLNode):
    def __init__(self, left_operand, right_operand):
        self.left = left_operand
        self.right = right_operand
        self.token = '&'
    
    def __str__(self):
        return f'({self.left} & {self.right})'
    
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
        return f'({self.left} | {self.right})'
    
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self

class NegateNode(FOLNode):
    def __init__(self, operand):
        self.operand = operand
        self.token = '-'
    
    def __str__(self):
        return f'-{self.left}'
    
    def simplify(self):
        if isinstance(self.operand, NegateNode):
            return self.operand.operand.simplify()
        return self.operand.simplify()

class ExistsNode(FOLNode):
    def __init__(self, variable, formula):
        self.variable = variable
        self.formula = formula
        self.token = '∃'
    
    def __str__(self):
        return f'∃{self.variable}({self.formula})'
    
    def simplify(self):
        self.formula = self.formula.simplify()
        return self

class ImplicationNode(FOLNode):
    def __init__(self, left_operand, right_operand):
        self.left = left_operand
        self.right = right_operand
        self.token = '->'

    def __str__(self):
        return f'({self.left} -> {self.right})'

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self


class AllNode(FOLNode):
    def __init__(self, variable, formula):
        self.variable = variable
        self.formula = formula
        self.token = '∀'

    def __str__(self):
        return f'∀{self.variable}({self.formula})'

    def simplify(self):
        self.formula = self.formula.simplify()
        return self

class EquivalenceNode(FOLNode):
    def __init__(self, left_operand, right_operand):
        self.left = left_operand
        self.right = right_operand
        self.token = '<->'

    def __str__(self):
        return f'({self.left} <-> {self.right})'

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self & AndNode(ImplicationNode(self.left, self.right), ImplicationNode(self.right, self.left))
