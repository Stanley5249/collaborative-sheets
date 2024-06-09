import ast

__all__ = ["arithmetics_eval"]


def ast_eval(node: ast.Module | ast.Expression | ast.Interactive) -> float:
    return eval(compile(node, "<string>", "eval"))


def arithmetics_eval(line: str) -> float | None:
    try:
        expr = ast.parse(line, mode="eval")
    except SyntaxError:
        print("invalid syntax")
        return

    match expr:
        # arithmetics operations
        case ast.Expression(
            body=ast.BinOp(
                left=ast.Constant(value=int() | float()),
                op=ast.Add()
                | ast.Sub()
                | ast.Mult()
                | ast.Div()
                | ast.Mod()
                | ast.Pow(),
                right=ast.Constant(value=int() | float()),
            )
        ):
            try:
                value = ast_eval(expr)
            except ArithmeticError as e:
                print(e)
                return
            else:
                print(f"expression (={value}) is an arithmetic operation")
                return value

        # constants
        case ast.Expression(body=ast.Constant(value=int() | float() as value)):
            if value == 42:
                print(
                    '"The answer to the Ultimate Question of Life, the Universe, and Everything"'
                )
            else:
                print(f"expression ({value}) is a constant")

            return value

        case _:
            print("invalid expression")
            return

    raise AssertionError("unreachable")
