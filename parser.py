import ast
import os

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.function_calls = {}

    def visit_FunctionDef(self, node):
        current_module = self.current_module
        func_name = f"{current_module}.{node.name}"
        self.functions.append(func_name)
        self.function_calls[func_name] = []
        self.current_function = func_name
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            current_func = self.current_function
            self.function_calls[current_func].append(node.func.id)
        self.generic_visit(node)


def parse_repo(repo_path):
    visitor = FunctionVisitor()
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                module_name = os.path.relpath(os.path.join(root, file), repo_path)[:-3].replace(os.sep, '.')
                visitor.current_module = module_name
                with open(os.path.join(root, file), 'r') as f:
                    tree = ast.parse(f.read())
                    visitor.visit(tree)
    return visitor.functions, visitor.function_calls


def get_function_code(function_name, repo_path):
    module, func = function_name.rsplit('.', 1)
    file_path = os.path.join(repo_path, *module.split('.')) + '.py'
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func:
                return ast.get_source_segment(f.read(), node)
    return None
