# back up before 12AM
import logic_parser as lg
from graphviz import Digraph

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

    def apply_all_steps(self, verbose = False):
        def myprint(string):
            if not verbose: return;
            print(string)
        
        self = self.implication_elimination() 
        myprint("after implication elimination :-")
        myprint(self)
        self = self.apply_demorgans() 
        myprint("\nafter apply_demorgans :-")
        myprint(self)
        self = self.standardize_variable_scope() 
        myprint("\nafter standardize_variable_scope :-")
        myprint(self)
        self = self.prenex_normal_form() 
        myprint("\nafter prenex_normal_form :-")
        myprint(self)
        self = self.skolemize() 
        myprint("\nafter skolemize :-")
        myprint(self)
        self = self.conjunctive_form() 
        myprint("\nafter conjunctive_form :-")
        myprint(self)
        self = self.compute_clauses() 
        myprint("\nafter compute_clauses :-")
        for clause in self.clauses:
            myprint('{ ' + ", ".join([str(x) for x in clause]) + ' }')
        self = self.standardize_clauses() 
        myprint("\nafter standardize_clauses :-")
        for clause in self.clauses:
            myprint('{ ' + ", ".join([str(x) for x in clause]) + ' }')

        return self
    
    def implication_elimination(self):
        self.expression = self.expression.copy().apply(eliminate_implication)
        return self
    
    def apply_demorgans(self):
        self.expression = self.expression.copy().simplify()
        return self
    
    #TODO: Do the renaming in a better way.
    def standardize_variable_scope(self):
        var_count=0
        var_mapping={}
        self.expression = self.expression.copy().rename(var_count, var_mapping)
        return self
    
    def get_quantifiers(expression):
        quantifiers = []
        def get_quant(expr):
            if isinstance(expr, lg.AllExpression) or isinstance(expr, lg.ExistsExpression):
                quantifiers.append(expr.copy())
            return expr
        expression.copy().apply(get_quant)
        return quantifiers
    def prenex_normal_form(self):
        self.all_quantifiers : list[lg.AllExpression | lg.ExistsExpression] = Resolution.get_quantifiers(self.expression)
        self.expression = self.expression.copy().apply(remove_quantifiers)
        for quant in self.all_quantifiers:
            quant.formula = self.expression
            self.expression = quant
        return self
    
    def skolemize(self):
        vars_of_alls = []
        for quant in self.all_quantifiers:
            if isinstance(quant, lg.AllExpression):
                vars_of_alls.append(quant.variable.symbol)
        def get_new_names():
            count: int = 0
            var_to_constant = {}

            for quant in self.all_quantifiers:
                if isinstance(quant, lg.ExistsExpression):
                    var_to_constant[quant.variable.symbol] = "f" + str(count)
                    count += 1

            return var_to_constant

        existential_var_to_constant: dict[str, str] = get_new_names()

        def rename_variable_names(expression):
            if isinstance(expression, lg.VariableExpression):
                if expression.symbol in existential_var_to_constant:
                    expression.symbol = existential_var_to_constant[expression.symbol]
                    expression.type = lg.VariableExpression.SKOLEM
                    expression.skolem_vars = list(vars_of_alls)
            return expression
        self.expression = self.expression.copy().apply(rename_variable_names).apply(remove_quantifiers)
        return self
    #TODO: Redo the conjunctive form using the apply function to reduce redundunt code
    
    def conjunctive_form(self):
        still_simplifable = True
        def do_conjuntive(expr):
            nonlocal still_simplifable
            if isinstance(expr, lg.OrExpression):
                if isinstance(expr.left, lg.AndExpression):
                    still_simplifable = True
                    andexp = expr.left
                    otherfactor = expr.right
                    left = lg.OrExpression(andexp.left,otherfactor)
                    right = lg.OrExpression(andexp.right,otherfactor)
                    expr =  lg.AndExpression(left, right)
                if isinstance(expr.right, lg.AndExpression):
                    still_simplifable = True
                    andexp = expr.right
                    otherfactor = expr.left
                    left = lg.OrExpression(otherfactor, andexp.left)
                    right = lg.OrExpression(otherfactor, andexp.right)
                    expr = lg.AndExpression(left, right)
            return expr
        
        while still_simplifable:
            still_simplifable = False
            self.expression = self.expression.apply(do_conjuntive, 'pre')

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
    def compute_clauses(self):
        self.clauses = self.collect_clauses()
        return self
    def collect_clauses(self):
        clauses = []
        memo = set()
        def addtomemo(exp):
            memo.add(exp)
            return exp
        
        def find_orclause(expression):
            if expression in memo:
                return expression
            if isinstance(expression, lg.OrExpression) or self.is_leaf(expression):
                clauses.append(self.collect_leafs(expression))
                expression.apply(addtomemo)
                return expression
            
            return expression
        self.expression.copy().apply(find_orclause, 'pre');
        return clauses
    

    def standardize_clauses(self):
        count = 0
        def get_next_name():
            count
            return f'var_{count}'

        def change_name(exp):
            if isinstance(exp, lg.VariableExpression):
                if exp.type == lg.VariableExpression.SKOLEM:
                    new_vars = []
                    for var in exp.skolem_vars:
                        if var in name_mapping:
                            new_vars.append(name_mapping[var])
                    exp.skolem_vars = new_vars
                    return exp
                if exp.symbol in name_mapping:
                    exp.symbol = name_mapping[exp.symbol]
            return exp
        
        def get_name(exp):
            if isinstance(exp, lg.VariableExpression) and exp.type == lg.VariableExpression.QUANT_VARIABLE:
                names.append(exp.symbol)
            return exp
        
        new_clauses = []

        for clause in self.clauses:
            names = []
            for leaf in clause:
                leaf.apply(get_name)
            name_mapping = {}
            for name in names:
                name_mapping[name] = get_next_name()
                count += 1
            new_clause = []
            for leaf in clause:
                new_clause.append(leaf.apply(change_name))
            new_clauses.append(new_clause)
        self.clauses = new_clauses
        return self
    
    def visualize_tree(self, root):
        dot = Digraph()

        def add_edge(parent, to_connect, edge_label=""):
            if to_connect is not None:
                dot.edge(str(id(parent)), str(id(to_connect)), label=edge_label)

        def add_node(node):
            if node is None:
                return


            node_content: str = ""
            if isinstance(node, lg.VariableExpression):
                node_content = str(node.symbol)
            elif isinstance(node, lg.PredicateExpression):
                node_content = f'Predicate: {node.symbol}'
            else:
                node_content = str(node.token)

            dot.node(str(id(node)), label=node_content)
            if isinstance(node, lg.AllExpression) or isinstance(node, lg.ExistsExpression):
                add_node(node.variable)
                add_edge(node, node.variable)
                
                add_node(node.formula)
                add_edge(node.variable, node.formula)
                return

            for n in node.children():
                add_node(n)
                add_edge(node, n)
                
        add_node(root)
        return dot
        
