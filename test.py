from logic_parser import *


# expr = AllExpression(VariableExpression("y"), ExistsExpression(VariableExpression("x"), NegationExpression(AndExpression(ImplicationExpression(VariableExpression("C"), VariableExpression("D")), PredicateExpression("father", [VariableExpression("A"), VariableExpression("B")])))))

# print(expr)
# parser = LogicParser(str(expr));
# print(parser.tokens)
# print(list(map(lambda x : str(x), parser.tokens)))
exps = [
	"x | y | z | a",
	"x & y & z & a",
	"x & y | z",
	" x | y & z",
	"w | x | y & z",
	"w & x & y | z",
	"x | y & z -> a",
	"a -> x | y & z ",
	"a | x | y -> z ",
	"a & x | y -> z <-> -hah ",
	"all y exists x -C -> D & father(A, B)",
	]
for exp in exps:
	parser = LogicParser(exp)
	print(exp, "_____________parsed: ", parser.parse())

expr = AllExpression(VariableExpression("y"), ExistsExpression(VariableExpression("x"), NegationExpression(AndExpression(ImplicationExpression(VariableExpression("C"), VariableExpression("D")), PredicateExpression("father", [VariableExpression("A"), VariableExpression("B")])))))

print(expr)
parser = LogicParser(str(expr));
print(parser.parse())