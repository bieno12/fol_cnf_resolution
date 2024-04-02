import re




class Expression:
    def __init__(self, token):
        self.token = token
    def str(self, reduced_brackets = False):
        return ""
    def simplify(self):
        return self
    def apply(self, fn, order='post'):
        pass
    def copy(self):
        pass
    def children(self):
        pass
    def __str__(self) -> str:
        return self.str()
    def rename(self, var_count, var_mapping):
        return self
    def conjunctive_form(self):
        return self
    def bracket(self, term):
        if Tokens.has_priority(self.token, term.token):
            return f'({term.str(True)})'
        return f'{term.str(True)}'


class VariableExpression(Expression):
    CONSTANT = 'constant'
    QUANT_VARIABLE = 'quan_variable'
    SKOLEM = 'skolem'
    def __init__(self, symbol, type = 'constant'):
        self.symbol: str = symbol
        self.type = type
        self.token = Tokens.IDENTIFIER
    def str(self, reduced_brackets= False):
        return self.symbol
    def apply(self, fn, order='post'):
        return fn(self)
    def copy(self):
        return VariableExpression(self.symbol, self.type)
    def children(self):
        return []
    def rename(self, var_count, var_mapping):
        if not self.symbol in var_mapping:
            return self
        self.symbol = f'{var_mapping[self.symbol]}'
        return self


class PredicateExpression(Expression):
    def __init__(self, symbol, var_nodes: list[VariableExpression]):
        self.var_nodes = var_nodes
        self.symbol: str = symbol
        self.token = Tokens.IDENTIFIER
    def str(self, reduced_brackets = False):
        return f'{self.symbol}({", ".join(map(lambda x: x.symbol, self.var_nodes))})'
    def apply(self, fn, order='post'):
        if order == 'post':
            var_list = [node.apply(fn) for node in self.var_nodes]
            self.var_nodes = var_list
            expr = fn(self)
            return expr
        elif order == 'pre':
            expr = fn(self)
            var_list = [node.apply(fn) for node in expr.var_nodes]
            expr.var_nodes = var_list
            return expr
    def copy(self):
        var_nodes_cpy = [node.copy() for node in self.var_nodes]
        return PredicateExpression(self.symbol, var_nodes_cpy)
    def children(self):
        return self.var_nodes
    
    def rename(self, var_count, var_mapping):
        self.var_nodes = [node.rename(var_count, var_mapping) for node in self.var_nodes]
        return self


class AndExpression(Expression):
    def __init__(self, left_operand, right_operand):
        self.left: Expression = left_operand
        self.right: Expression = right_operand
        self.token = '&'
    
    def str(self, reduced_brackets = False):
        if not reduced_brackets:
            return f'({self.left.str(reduced_brackets)}) & ({self.right.str(reduced_brackets)})'
        else:
             return f'{self.bracket(self.left)} & {self.bracket(self.right)}'
            
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self
    
    def apply(self, fn, order = 'post'):
        if order == 'post':
            self.left = self.left.apply(fn, order)
            self.right = self.right.apply(fn, order)
            expr = fn(self)
            return expr
        elif order == 'pre':
            expr = fn(self)
            expr.left = expr.left.apply(fn, order)
            expr.right = expr.right.apply(fn, order)
            return expr
    def copy(self):
        return AndExpression(self.left.copy(), self.right.copy())
    def children(self):
        return [self.left, self.right]
    
    def rename(self, var_count, var_mapping):
        self.left = self.left.rename(var_count, var_mapping)
        self.right = self.right.rename(var_count, var_mapping)
        return self
    
    def conjunctive_form(self):
        self.left = self.left.conjunctive_form()
        self.right = self.right.conjunctive_form()
        return self
    
class OrExpression(Expression):
    def __init__(self, left_operand, right_operand):
        self.left: Expression = left_operand
        self.right: Expression = right_operand
        self.token: str = '|'
    
    def str(self, reduced_brackets = False):
        if not reduced_brackets:
            return f'({self.left.str(reduced_brackets)}) | ({self.right.str(reduced_brackets)})'
        else:
             return f'{self.bracket(self.left)} | {self.bracket(self.right)}'
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self
    
    def apply(self, fn, order = 'post'):
        if order == 'post':
            self.left = self.left.apply(fn, order)
            self.right = self.right.apply(fn, order)
            expr = fn(self)
            return expr
        elif order == 'pre':
            expr = fn(self)
            expr.left = expr.left.apply(fn, order)
            expr.right = expr.right.apply(fn, order)
            return expr
    
    def copy(self):
        return OrExpression(self.left.copy(), self.right.copy())
    
    def children(self):
        return [self.left, self.right]

    def rename(self, var_count, var_mapping):
        self.left = self.left.rename(var_count, var_mapping)
        self.right = self.right.rename(var_count, var_mapping)
        return self
    
    def conjunctive_form(self):
        if isinstance(self.left, AndExpression):
            andexpr = self.left
            new_left = OrExpression(andexpr.left, self.right)
            new_right = OrExpression(andexpr.right, self.right)
            return AndExpression(new_left, new_right).conjunctive_form()
        if isinstance(self.right, AndExpression):
            andexpr = self.right
            new_left = OrExpression(self.left, andexpr.left)
            new_right = OrExpression(self.left, andexpr.right)
            return AndExpression(new_left, new_right).conjunctive_form()
        self.left = self.left.conjunctive_form()
        self.right = self.right.conjunctive_form()
        return self
    
class ImplicationExpression(Expression):
    def __init__(self, left_operand, right_operand):
        self.left: Expression = left_operand
        self.right: Expression = right_operand
        self.token: str = '->'

    def str(self, reduced_brackets = False):
        if not reduced_brackets:
            return f'({self.left.str(reduced_brackets)}) -> ({self.right.str(reduced_brackets)})'
        else:
             return f'{self.bracket(self.left)} -> {self.bracket(self.right)}'

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self
    
    def apply(self, fn, order = 'post'):
        if order == 'post':
            self.left = self.left.apply(fn, order)
            self.right = self.right.apply(fn, order)
            expr = fn(self)
            return expr
        elif order == 'pre':
            expr = fn(self)
            expr.left = expr.left.apply(fn, order)
            expr.right = expr.right.apply(fn, order)
            return expr
    def copy(self):
        return ImplicationExpression(self.left.copy(), self.right.copy())
    
    def children(self):
        return [self.left, self.right]
    
    def rename(self, var_count, var_mapping):
        self.left = self.left.rename(var_count, var_mapping)
        self.right = self.right.rename(var_count, var_mapping)
        return self
    
    def conjunctive_form(self):
        self.left = self.left.conjunctive_form()
        self.right = self.right.conjunctive_form()
        return self
    
class EquivalenceExpression(Expression):
    def __init__(self, left_operand, right_operand):
        self.left: Expression = left_operand
        self.right: Expression = right_operand
        self.token: str = '<->'

    def str(self, reduced_brackets = False):
        if not reduced_brackets:
            return f'({self.left}) <-> ({self.right})'
        else:
             return f'{self.bracket(self.left)} <-> {self.bracket(self.right)}'

    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        return self & AndExpression(ImplicationExpression(self.left, self.right), ImplicationExpression(self.right, self.left))
    
    def apply(self, fn, order = 'post'):
        if order == 'post':
            self.left = self.left.apply(fn, order)
            self.right = self.right.apply(fn, order)
            expr = fn(self)
            return expr
        elif order == 'pre':
            expr = fn(self)
            expr.left = expr.left.apply(fn, order)
            expr.right = expr.right.apply(fn, order)
            return expr
    def copy(self):
        return EquivalenceExpression(self.left.copy(), self.right.copy())
    
    def children(self):
        return [self.left, self.right]
    
    def rename(self, var_count, var_mapping):
        self.left = self.left.rename(var_count, var_mapping)
        self.right = self.right.rename(var_count, var_mapping)
        return self
    
    def conjunctive_form(self):
        self.left = self.left.conjunctive_form()
        self.right = self.right.conjunctive_form()
        return self
    
class NegationExpression(Expression):
    def __init__(self, operand):
        self.operand: Expression = operand
        self.token: str = '-'
    
    def str(self, reduced_brackets= False):
        if not reduced_brackets:
            return f'-({self.operand.str(reduced_brackets)})'
        else:
             return f'-{self.bracket(self.operand)}'
    
    def simplify(self):
        if isinstance(self.operand, NegationExpression):
            return self.operand.operand.simplify()
        if isinstance(self.operand, AndExpression):
            return OrExpression(NegationExpression(self.operand.left).simplify(), NegationExpression(self.operand.right).simplify())
        if isinstance(self.operand, OrExpression):
            return AndExpression(NegationExpression(self.operand.left).simplify(), NegationExpression(self.operand.right).simplify())
        return self
    
    def apply(self, fn, order = 'post'):
        if order == 'post':
            self.operand = self.operand.apply(fn, order)
            expr = fn(self)
            return expr
        elif order == 'pre':
            expr = fn(self)
            expr.operand = expr.operand.apply(fn, order)
            return expr
    def copy(self):
        return NegationExpression(self.operand.copy())
    
    def children(self):
        return [self.operand]
    
    def rename(self, var_count, var_mapping):
        self.operand = self.operand.rename(var_count, var_mapping)
        return self
    
    def conjunctive_form(self):
        self.operand = self.operand.conjunctive_form()
        return self
    
class ExistsExpression(Expression):
    def __init__(self, variable, formula):
        self.variable: Expression = variable
        def update_var_type(exp):
            if isinstance(exp, VariableExpression):
                if self.variable.symbol == exp.symbol:
                    exp.type = VariableExpression.QUANT_VARIABLE
            return exp
        if formula != None:
            self.formula: Expression = formula.apply(update_var_type)
        else:
            self.formula = None
        self.token: str = 'exists'
    
    def str(self, reduced_brackets = False):
        return f'exists {self.variable} ({self.formula.str(reduced_brackets)})'
    
    def simplify(self):
        self.formula = self.formula.simplify()
        return self
    
    def apply(self, fn, order = 'post'):
        if order == 'post':
            self.variable = self.variable.apply(fn, order)
            self.formula = self.formula.apply(fn, order)
            return fn(self)
        elif order == 'pre':
            expr = fn(self)
            expr.variable = expr.variable.apply(fn, order)
            expr.formula = expr.formula.apply(fn, order)
            return expr
    def copy(self):
        if self.formula == None:
            return ExistsExpression(self.variable.copy(), None)
        return ExistsExpression(self.variable.copy(), self.formula.copy())
    
    def children(self):
        return [self.variable, self.formula]
    
    def rename(self, var_count, var_mapping):
        var_mapping[self.variable.symbol] = f'x{var_count + 1}'
        self.variable = self.variable.rename(var_count + 1, var_mapping)
        self.formula = self.formula.rename(var_count + 1, var_mapping)
        return self
    
    def conjunctive_form(self):
        self.formula = self.formula.conjunctive_form()
        return self

class AllExpression(Expression):
    def __init__(self, variable, formula):
        self.variable: Expression = variable
        def update_var_type(exp):
            if isinstance(exp, VariableExpression):
                if self.variable.symbol == exp.symbol:
                    exp.type = VariableExpression.QUANT_VARIABLE
            return exp
        if formula != None:
            self.formula: Expression = formula.apply(update_var_type)
        else:
            self.formula = None
        self.token: str = 'all'

    def str(self, reduced_brackets = False):
        return f'all {self.variable} ({self.formula.str(reduced_brackets)})'

    def simplify(self):
        self.formula = self.formula.simplify()
        return self
    
    def apply(self, fn, order = 'post'):
        if order == 'post':
            self.variable = self.variable.apply(fn, order)
            self.formula = self.formula.apply(fn, order)
            return fn(self)
        elif order == 'pre':
            expr = fn(self)
            expr.variable = expr.variable.apply(fn, order)
            expr.formula = expr.formula.apply(fn, order)
            return expr
    def copy(self):
        return AllExpression(self.variable.copy(), self.formula.copy())

    def children(self):
        return [self.variable, self.formula]
    
    def rename(self, var_count, var_mapping):
        var_mapping[self.variable.symbol] = f'x{var_count + 1}'
        self.variable = self.variable.rename(var_count + 1, var_mapping)
        self.formula = self.formula.rename(var_count + 1, var_mapping)
        return self

    def conjunctive_form(self):
        self.formula = self.formula.conjunctive_form()
        return self

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

    operator_precedence = [
            [IDENTIFIER],
            [NOT],
            QUANTS,
            [AND],
            [OR],
            [IMP],
            [IFF],
        ]
    def get_priority(token_type: str):
        for i,l in enumerate(Tokens.operator_precedence):
            if token_type in l: return i
        return 999
    def has_priority( tok: str, another):
        return Tokens.get_priority(tok) < Tokens.get_priority(another)
    
def parse_from_str(string: str):
    parser = LogicParser(string)
    return parser.parse()
class LogicParser:
    def __init__(self, expression: str) -> None:
        self.expression = expression

        self.tokens = self.tokenize(self.expression)
        self.operator_precedence = [
            [Tokens.NOT],
            Tokens.QUANTS,
            [Tokens.AND],
            [Tokens.OR],
            [Tokens.IMP],
            [Tokens.IFF],
        ]
    def get_priority(self, type: str):
        for i,l in enumerate(self.operator_precedence):
            if type in l: return i
        return 999
    def has_priority(self, tok: str, context):
        if context == None:
            return True
        return self.get_priority(tok) < self.get_priority(context.type)
    
    def print_tokens(self):
        print(list(map(lambda x: str(x), self.tokens)))

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
        if(self.current_index >= len(self.tokens)) or self.tokens[self.current_index].type != type:
            raise Exception(f"Missing Token of type({type})")
        t = self.tokens[self.current_index]
        self.current_index += 1;
        return t
    def in_range(self, loc = 0):
        return self.current_index + loc < len(self.tokens)
    def token(self, location = None) -> Tokens.Token:
        try:
            if location is None:
                tok = self.tokens[self.current_index]
                self.current_index += 1
            else:
                tok = self.tokens[self.current_index + location]
            return tok
        except IndexError as e:
            raise Exception(f"Ran out of tokens at index {self.current_index + 1}")

    def parse(self) -> Expression:
        self.current_index = 0;
        expr = self.parse_expression()
        return expr
    
    def parse_expression(self, context = None) -> Expression:
        #get next token
        tok = self.token(0)
        accum = self.handle(context)

        return self.handle_binops(accum, context)
    
    def handle(self, context):
        tok = self.token(0)
        if tok.type == Tokens.IDENTIFIER:
            return self.handle_identifier()
        elif tok.type == Tokens.NOT:
            return self.parse_negation()
        elif tok.type in Tokens.QUANTS:
            return self.handle_quantifier()
        elif tok.type == Tokens.OPEN:
            return self.handle_open()
        raise Exception("didn't expect to be here")

    def handle_identifier(self):
        # It's either: 1) a predicate expression: sees(x,y)
        #             3) a solo variable: john OR x
        if self.in_range(1) and self.token(1).type == Tokens.OPEN:
            return self.parse_predicate()
        else:
            return self.parse_variable(VariableExpression.CONSTANT)
        
    def parse_predicate(self):
        perdicate_name = self.consume_token(Tokens.IDENTIFIER).value;
        variables_list = []
        self.consume_token(Tokens.OPEN)
        #parsing variable list
        variables_list.append(self.parse_variable(VariableExpression.CONSTANT))
        try:
            while self.token(0).type == Tokens.COMMA:
                self.consume_token(Tokens.COMMA)
                variables_list.append(self.parse_variable(VariableExpression.CONSTANT))
        except:
            pass
        # parse closing bracket
        self.consume_token(Tokens.CLOSE)
        return PredicateExpression(perdicate_name, variables_list)

    def parse_variable(self, type):
        tok = self.consume_token(Tokens.IDENTIFIER)
        return VariableExpression(tok.value, type)
    
    def parse_negation(self):
        t = self.consume_token(Tokens.NOT)
        return NegationExpression(self.parse_expression(t))
    
    def handle_quantifier(self):
        if self.token(0).type == Tokens.ALL:
            return self.parse_all_exp()
        elif self.token(0).type == Tokens.EXISTS:
            return self.parse_exists_exp()
        else:
            raise Exception("Shouldnt be here")

    def parse_all_exp(self):
        t= self.consume_token(Tokens.ALL)
        variable = self.parse_variable(VariableExpression.QUANT_VARIABLE)
        formula = self.parse_expression()
        return AllExpression(variable, formula)
    
    def parse_exists_exp(self):
        t = self.consume_token(Tokens.EXISTS)
        variable = self.parse_variable(VariableExpression.QUANT_VARIABLE)
        formula = self.parse_expression()

        return ExistsExpression(variable, formula)
    def handle_open(self):
        self.consume_token(Tokens.OPEN)
        exp = self.parse_expression()
        self.consume_token(Tokens.CLOSE)
        return exp
   
    def handle_binops(self,expression: Expression,  context: Tokens.Token):
        cur_idx = None
        while cur_idx != self.current_index:  # while adjuncts are added
            cur_idx = self.current_index

            expression = self.attempt_AndExpression(expression, context)
            expression = self.attempt_OrExpression(expression, context)
            expression = self.attempt_ImplicationExpression(expression, context)
            expression = self.attempt_EquivExpression(expression, context)
        return expression
    
    def attempt_AndExpression(self, expression: Expression,context: Tokens.Token):
        if not self.in_range(0) or not self.has_priority(Tokens.AND, context): 
            return expression
        if self.token(0).type == Tokens.AND:
            return AndExpression(expression, self.parse_expression(self.token()))
        else:
            return expression
        
    def attempt_OrExpression(self, expression: Expression, context: Tokens.Token):
        if not self.in_range(0) or not self.has_priority(Tokens.OR, context): 
            return expression
        if self.token(0).type == Tokens.OR:
            return OrExpression(expression, self.parse_expression(self.token()))
        else:
            return expression

    def attempt_ImplicationExpression(self, expression: Expression, context: Tokens.Token):
        if not self.in_range(0) or not self.has_priority(Tokens.IMP, context): 
            return expression
        if self.token(0).type == Tokens.IMP:
            return ImplicationExpression(expression, self.parse_expression(self.token()))
        else:
            return expression
        
    def attempt_EquivExpression(self, expression: Expression, context: Tokens.Token):
        if not self.in_range(0) or not self.has_priority(Tokens.IFF, context): 
            return expression
        if self.token(0).type == Tokens.IFF:
            return EquivalenceExpression(expression, self.parse_expression(self.token()))
        else:
            return expression
