def compile_op(op):
    if isinstance(op, ast.Lt):
        return "<"
    elif isinstance(op, ast.LtE):
        return "<="
    elif isinstance(op, ast.Gt):
        return ">"
    elif isinstance(op, ast.GtE):
        return ">="

def resolve_fun(n):
    if isinstance(n, ast.Name):
        return n.id
    elif isinstance(n, ast.Attribute):
        if n.value.id == 'math':
            return n.attr
        else:
            raise NotImplemented()

def compile_expr(n):
    s=""
    if isinstance(n, ast.BinOp):
        s+="("
        if isinstance(n.op, ast.Mult):
            s+= "* "
        elif isinstance(n.op, ast.Add):
            s+= "+ "
        elif isinstance(n.op, ast.Div):
            s+= "/ "
        elif isinstance(n.op, ast.Sub):
            s+= "- "
        s+= compile_expr(n.left) + " "
        s+= compile_expr(n.right) + ")"
    if isinstance(n, ast.UnaryOp):
        s+="("
        if isinstance(n.op, ast.UAdd):
            s+= "+ "
        elif isinstance(n.op, ast.USub):
            s+= "- "
        elif isinstance(n.op, ast.Not):
            s+= "not "
        elif isinstance(n.op, ast.Invert):
            raise NotImplemented()
        s+= compile_expr(n.operand) + ")"
    if isinstance(n, ast.Compare):
        left_val = compile_expr(n.left)
        args = [compile_expr(arg) for arg in n.comparators]
        if len(set(n.ops)) == 1:
            s+= "(" + compile_op(n.ops[0]) + " " + " ".join([left_val] + args) + ")"
        else:
            cs = []
            for op,left,right in zip(n.ops, [left_val] + args, args):
                c = "(" + compile_op(op) + " " + left + " " + right + ")"
                cs.append(c)
            s+= "(and " + " ".join(cs) + ")"
    if isinstance(n, ast.Constant):
        val = str(n.value)
        s+= val
    if isinstance(n, ast.Call):
        s+="("
#         s+= resolve_func(n.func)
        s+= resolve_fun(n.func)
        s+=" "
        s+= " ".join([
        compile_expr(item)
        for item 
        in n.args
        ])
        s+=")"
    elif isinstance(n, ast.Name):
        s+=n.id
    return s

import ast
import argparse
from re import L
parser = argparse.ArgumentParser()
parser.add_argument('-file', help="File to pass") # to handle command line arguments
args = parser.parse_args()
# print(args.file.readlines())
input_file = open(args.file, 'r')
line = ""
for l in input_file:
    line += l

node = ast.parse(line)
# print(ast.dump(node, indent=2))
import array
listArgs=[] # to store the argument values
s = "(FPCore ("
s += " ".join([
    item.arg
    for item
    in node.body[0].args.args
])
s+=')\n  '
end= ""
for n in node.body[0].body:
    if isinstance(n, ast.Expr):
        s+=compile_expr(n.value)
    if isinstance(n, ast.Assign):
        s+="(let* (["
        s+= ",".join([
            item.id
            for item
            in n.targets
        ])
        s+=" "
        s+=compile_expr(n.value)
        s+="]) "
        end+=")"
    if isinstance(n, ast.Return):
        s+=compile_expr(n.value)
s+=end
s+=')'
print(s)
