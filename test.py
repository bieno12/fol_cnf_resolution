from logic_parser import *


expr = AllExpression(VariableExpression("y"), ExistsExpression(VariableExpression("x"), NegationExpression(AndExpression(ImplicationExpression(VariableExpression("C"), VariableExpression("D")), PredicateExpression("father", [VariableExpression("A"), VariableExpression("B")])))))

print(expr)
parser = LogicParser(str(expr));
print(parser.tokens)
print(list(map(lambda x : str(x), parser.tokens)))
