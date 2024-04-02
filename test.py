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

expr = parse_from_str('exists x -P(x) -> (exists y all z P(x, y, z, x) & -Q(x, y))')
print(expr)

new_expr = Resolution(expr)
new_expr = new_expr.apply_all_steps(True)

print('--------------------------------------------------------------------------------\n\n')

expr = parse_from_str("exists x -P(x) -> (exists y all z P(x, y, z, x) & -Q(x, y))")
r = Resolution(expr).apply_all_steps()
print(expr.str(True))
print(expr.str(False))

dot = Resolution(expr).visualize_tree(expr)
dot.render(outfile='tree.png')

# print("after steps: ", r)
# print("clauses = ", [[str(y) for y in x] for x in r.clauses])

# expr = parse_from_str("a | c & d")
# r = Resolution(expr).apply_all_steps()
# print(expr)
# print("after steps: ", r)
# print("clauses = ", [[str(y) for y in x] for x in r.clauses])

# expr = parse_from_str("-a & b | -c & d")
# r = Resolution(expr).apply_all_steps()
# print(expr)
# print("after steps: ", r)
# print("clauses = ", [[str(y) for y in x] for x in r.clauses])


# expr = parse_from_str("-a & b & c & d")
# r = Resolution(expr).apply_all_steps()
# print(expr)
# print("after steps: ", r)
# print("clauses = ", [[str(y) for y in x] for x in r.clauses])


# expr = parse_from_str("a | b | P(x)")
# r = Resolution(expr).apply_all_steps()
# print(expr)
# print("after steps: ", r)
# print("clauses = ", [[str(y) for y in x] for x in r.clauses])

expr = parse_from_str('exists x -P(x) -> (all x exists y P(x, y) & Q(x, y))')
print(expr)

new_expr = Resolution(expr)
new_expr = new_expr.apply_all_steps(True)

print('--------------------------------------------------------------------------------\n\n')

expr = parse_from_str("a & (b | c & d) | e ")
r = Resolution(expr).conjunctive_form()
print("expr: ", r.expression.str(True))

