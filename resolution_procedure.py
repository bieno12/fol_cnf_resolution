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
        self.all_quantifiers = self.expression.copy().get_quantifiers([])
        
    def __str__(self):
        return str(self.expression)

    def apply_all_steps(self):
        return self.implication_elimination()   \
                .apply_demorgans().standardize_variable_scope() \
                .prenex_normal_form()   \
                .skolemize()    \
                .conjunctive_form()
    
    def implication_elimination(self):
        self.expression = self.expression.copy().apply(eliminate_implication)
        return self
    def apply_demorgans(self):
        self.expression = self.expression.copy().simplify()
        return self
    def standardize_variable_scope(self):
        var_count=0
        var_mapping={}
        self.expression = self.expression.copy().rename(var_count, var_mapping)
        return self
    def prenex_normal_form(self):
        self.all_quantifiers = self.expression.get_quantifiers([])

        if(len(self.all_quantifiers) == 0):
            return self

        self.expression = self.expression.copy().apply(remove_quantifiers)
        for i in range(len(self.all_quantifiers) - 1):
            self.all_quantifiers[i].formula = self.all_quantifiers[i + 1]
        
        self.all_quantifiers[-1].formula = self.expression
        self.expression = self.all_quantifiers[0].copy()
        return self
    def skolemize(self):
        def get_new_names():
            count: int = 0
            var_to_constant = {}
            for quant in self.all_quantifiers:
                if isinstance(quant, lg.ExistsExpression):
                    var_to_constant[quant.variable.symbol] = "f" + str(count) + "()"
                    count += 1

            return var_to_constant

        existential_var_to_constant: dict[str, str] = get_new_names()

        def rename_variable_names(expression):
            if isinstance(expression, lg.VariableExpression):
                if expression.symbol in existential_var_to_constant:
                    expression.symbol = existential_var_to_constant[expression.symbol]

            return expression
        
        self.expression = self.expression.copy().apply(rename_variable_names).apply(remove_quantifiers)
        return self

    def conjunctive_form(self):
        self.expression = self.expression.conjunctive_form()
        return self

    #what is a leaf
    #1 - lone variable or predicate
    #2 - negated variable or predicate
    def is_leaf(self, exp):
        return isinstance(exp, lg.VariableExpression)   \
                or isinstance(exp, lg.NegationExpression)  \
                or isinstance(exp, lg.PredicateExpression)
    def collect_leafs(self, expression):
        leafs = []
        memo = set()
        def addtomemo(exp):
            memo.add(exp)
            return exp
        def find_leaf(exp):
            if exp in memo:
                return exp
            if self.is_leaf(exp):
                leafs.append(exp)
                exp.apply(addtomemo)

            return exp
        expression.copy().apply(find_leaf, 'pre')
        return leafs

    #what is a clause
    #1 - a leaf
    #2 - leafs of an Or
    
    def collect_clauses(self):
        return [self.collect_leafs(self.expression)]
        clauses = []
        memo = set()
        def addtomemo(exp):
            memo.add(exp)
            return exp
        
        def find_orclause(expression):
            if expression in memo:
                return expression
            if isinstance(expression, lg.OrExpression):
                clauses.append(self.collect_leafs(expression))
                print("found: ",expression)
                expression.apply(addtomemo)
                return expression
            return expression
        self.expression.copy().apply(find_orclause, 'pre');
        return clauses
    