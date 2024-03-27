from logic_parser import *
from resolution_procedure import Resolution

# expr = AllExpression(VariableExpression("y"), ExistsExpression(VariableExpression("x"), NegationExpression(AndExpression(ImplicationExpression(VariableExpression("C"), VariableExpression("D")), PredicateExpression("father", [VariableExpression("A"), VariableExpression("B")])))))

# print(expr)
# parser = LogicParser(str(expr));
# print(parser.tokens)
# print(list(map(lambda x : str(x), parser.tokens)))
# exps = [
# 	"x | y | z | a",
# 	"x & y & z & a",
# 	"x & y | z",
# 	" x | y & z",
# 	"w | x | y & z",
# 	"w & x & y | z",
# 	"x | y & z -> a",
# 	"a -> x | y & z ",
# 	"a | x | y -> z ",
# 	"a & x | y -> z <-> -hah ",
# 	"all y exists x -C -> D & father(A, B)",
# 	]
# for exp in exps:
# 	parser = LogicParser(exp)
# 	print(exp, "_____________parsed: ", parser.parse())
# print("-----------------------------------------------------------")
# print("-----------------------------------------------------------")
# print("-----------------------------------------------------------")
# print()
expr = AllExpression(VariableExpression("y"), ExistsExpression(VariableExpression("x"), NegationExpression(AndExpression(ImplicationExpression(VariableExpression("C"), VariableExpression("D")), PredicateExpression("father", [VariableExpression("A"), VariableExpression("B")])))))
exprstr = "A & C -> B -> D"
parser = LogicParser(str(exprstr))
expr = parser.parse()
print(expr.copy())
print(Resolution.implication_elimination(expr))

print("-----------------------------------------------------------")
print("-----------------------------------------------------------")
print("-----------------------------------------------------------")
print()

expr = parse_from_str('-(a | b) ')
print(expr)
print(expr.simplify())
print()
expr = parse_from_str('-(-a & b -> c) ')
print(expr)
expr = Resolution.implication_elimination(expr)
print(expr)
print(Resolution.apply_demorgans(expr))



