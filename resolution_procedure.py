import logic_parser as lg
"""
    Resolution object takes an expr
    fn1: applies implication elimination to the expression
    fn2: applies demorgan's law
"""



def eliminate_implication(expression):
    def is_implication(expr):
        return isinstance(expr, lg.ImplicationExpression)
    
    if is_implication(expression):
        expression = lg.OrExpression(lg.NegationExpression(expression.left), expression.right)
    
    expression.apply(eliminate_implication)

    return expression

class Resolution:
    def __init__(self, expr: lg.Expression):
        self.expression = expr.copy()
    
    def __str__(self):
        return str(self.expression)

    def implication_elimination(self):
        return self.expression.apply(eliminate_implication)