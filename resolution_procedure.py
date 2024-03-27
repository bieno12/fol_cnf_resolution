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


def remove_existential(expression):
    if isinstance(expression, lg.ExistsExpression):
            return expression.formula
    return expression

def remove_universal(expression):
    if isinstance(expression, lg.AllExpression):
        return expression.formula
    return expression

def remove_quantifiers(expression):
    expression = remove_existential(expression)
    expression = remove_universal(expression)
    return expression

class Resolution:
    def __init__(self, expr: lg.Expression):
        self.expression = expr.copy()
        
    def __str__(self):
        return str(self.expression)

    def implication_elimination(self):
        self.expression = self.expression.copy().apply(eliminate_implication)
    
    def apply_demorgans(self):
        self.expression = self.expression.copy().simplify()

    def standardize_variable_scope(self, var_count=0, var_mapping={}):
        self.expression = self.expression.copy().rename(var_count, var_mapping)
    
    def prenex_normal_form(self):
        all_quantifiers = self.expression.copy().get_quantifiers([])
        self.expression = self.expression.copy().apply(remove_quantifiers)
        for i in range(len(all_quantifiers) - 1):
            all_quantifiers[i].formula = all_quantifiers[i + 1]
        
        all_quantifiers[-1].formula = self.expression
        self.expression = all_quantifiers[0].copy()
