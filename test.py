from logic_parser import *


expr = AllNode(VariableNode("y"), ExistsNode(VariableNode("x"), NegateNode(AndNode(ImplicationNode(VariableNode("C"), VariableNode("D")), PredicateNode("father", [VariableNode("A"), VariableNode("B")])))))

print(expr)
print(Tokens.tokenize(expr.__str__()))