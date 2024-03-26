from logic_parser import *


expr = AllNode(VariableNode("y"), ExistsNode(VariableNode("x"), NegateNode(AndNode(ImplicationNode(VariableNode("C"), VariableNode("D")), PredicateNode("father", [VariableNode("A"), VariableNode("B")])))))

print(expr)
parser = LogicParser(str(expr));
print(parser.tokens)
print(list(map(lambda x : str(x), parser.tokens)))
