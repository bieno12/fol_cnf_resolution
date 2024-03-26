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
            return self.parse_variable()
        
    def parse_predicate(self):
        perdicate_name = self.consume_token(Tokens.IDENTIFIER).value;
        variables_list = []
        self.consume_token(Tokens.OPEN)
        #parsing variable list
        variables_list.append(self.parse_variable())
        try:
            while self.token(0).type == Tokens.COMMA:
                self.consume_token(Tokens.COMMA)
                variables_list.append(self.parse_variable())
        except:
            pass
        #parse closing bracket
        self.consume_token(Tokens.CLOSE)
        return PredicateExpression(perdicate_name, variables_list)

    def parse_variable(self):
        tok = self.consume_token(Tokens.IDENTIFIER)
        return VariableExpression(tok.value)
    def parse_negation(self):
        t = self.consume_token(Tokens.NOT)
        return NegationExpression(self.parse_expression(t))
    def handle_quantifier(self):
        print("type:" , self.token(0))
        if self.token(0).type == Tokens.ALL:
            return self.parse_all_exp()
        elif self.token(0).type == Tokens.EXISTS:
            return self.parse_exists_exp()
        else:
            raise Exception("Shouldnt be here")

    def parse_all_exp(self):
        t= self.consume_token(Tokens.ALL)
        variable = self.parse_variable()
        formula = self.parse_expression()
        return AllExpression(variable, formula)
    def parse_exists_exp(self):
        t = self.consume_token(Tokens.EXISTS)
        variable = self.parse_variable()
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