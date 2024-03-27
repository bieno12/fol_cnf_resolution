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
# expr = AllExpression(VariableExpression("y"), ExistsExpression(VariableExpression("x"), NegationExpression(AndExpression(ImplicationExpression(VariableExpression("C"), VariableExpression("D")), PredicateExpression("father", [VariableExpression("A"), VariableExpression("B")])))))
# exprstr = "A & C -> B -> D"
# parser = LogicParser(str(exprstr))
# expr = parser.parse()
# print(expr.copy())
# resol = Resolution(expr)
# resol.implication_elimination()

# print(resol.expression)

print("-----------------------------------------------------------")
print("-----------------------------------------------------------")
print("-----------------------------------------------------------")
print()

# expr = parse_from_str('-(a | b) ')
# print(expr)
# print(expr.simplify())
# print()

# all y exists x -C -> D & father(A, B)
# expr = parse_from_str('-(-a & b -> c) ')

expr = parse_from_str('exists x -P(x) -> (all x exists y P(x, y))')
print(expr)

new_expr = Resolution(expr)

new_expr.implication_elimination()
print(new_expr)
new_expr.apply_demorgans()
print(new_expr)

new_expr.standardize_variable_scope()
print(new_expr)

new_expr.prenex_normal_form()
print(new_expr)

new_expr.skolemize()
print(new_expr)
