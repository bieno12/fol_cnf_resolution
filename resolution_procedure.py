import logic_parser as lg
"""
    Resolution object takes an expr
    fn1: applies implication elimination to the expression
    fn2: applies demorgan's law
"""



def eliminate_implication(expression):
    if isinstance(expression, lg.ImplicationExpression):
        expression = lg.OrExpression(lg.NegationExpression(expression.left), expression.right)
    return expression

class Resolution:
    def __init__(self, expr: lg.Expression):
        self.expression = expr.copy()
        self.quantifier_variables = {}
    def __str__(self):
        return str(self.expression)

    def implication_elimination(self,):
        self.expression = self.expression.copy().apply(eliminate_implication)
    
    def apply_demorgans(self):
        self.expression = self.expression.copy().simplify()
    def standardize_variable_scope(self):
         pass