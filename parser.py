import ast
import os
import builtins

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.function_calls = {}
        self.imports = {}
        self.current_module = ""
        self.current_function = ""
        self.builtin_methods = set(dir(builtins))

    def visit_FunctionDef(self, node):
        func_name = f"{self.current_module}.{node.name}"
        self.functions.append(func_name)
        self.function_calls[func_name] = []
        self.current_function = func_name
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            called_func_name = self.resolve_name(node.func.id)
            # Check if the function is not a built-in method
            if node.func.id not in self.builtin_methods:
                self.function_calls[self.current_function].append(called_func_name)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name

    def visit_ImportFrom(self, node):
        module = node.module
        for alias in node.names:
            full_name = f"{module}.{alias.name}"
            self.imports[alias.asname or alias.name] = full_name

    def resolve_name(self, name):
        return self.imports.get(name, f"{self.current_module}.{name}")

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

functions, function_calls = parse_repo('/Users/Gowtham/Algorithm')

def get_function_code(function_name, repo_path):
    module, func = function_name.rsplit('.', 1)
    file_path = os.path.join(repo_path, *module.split('.')) + '.py'
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func:
                return ast.get_source_segment(f.read(), node)
    return None

def get_function_code(function_name, repo_path):
    module, func = function_name.rsplit('.', 1)
    file_path = os.path.join(repo_path, *module.split('.')) + '.py'
    
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
            tree = ast.parse(file_content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == func:
                    start_line = node.lineno - 1  # lineno is 1-based, converting to 0-based
                    end_line = node.end_lineno  # end_lineno is 1-based

                    # Extract the lines corresponding to the function definition
                    function_lines = file_content.splitlines()[start_line:end_line]
                    return '\n'.join(function_lines)
    except Exception as e:
        print(f"Error reading function {function_name} in {file_path}: {e}")
    
    return None

function_code = get_function_code('sorting.selection_sort.util.swap', '/Users/Gowtham/Algorithm')
print(function_code)

function, function_calls = parse_repo('/Users/Gowtham/Algorithm')
