import ast
import astor

def add_decorator(file_path, decorator_name) -> str:
    """
    Automatically    adds the specified decorator to all functions defined in the given file.

    Args:
        file_path (str): The path to the Python file.
        decorator_name (str): The name of the decorator to apply.
    """

    with open(file_path, 'r') as f:
        source_code = f.read()

    tree = ast.parse(source_code)

    tree.body.insert(0, ast.parse('from line_profiler import profile').body[0])

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            node.decorator_list.insert(0, ast.Name(id=decorator_name, ctx=ast.Load()))

    with open(file_path, 'w') as f:
        f.write(astor.to_source(tree))