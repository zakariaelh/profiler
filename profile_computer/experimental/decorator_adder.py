import ast
import astor
import os

def add_decorator(file_path, decorator_name) -> str:
    """
    Automatically adds the specified decorator to all functions defined in the given file.

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

    # TODO: Add a timestamp to reduce collisions.
    file_path_to_profile = os.path.splitext(file_path)[0] + '_profile_decorated' + os.path.splitext(file_path)[1]

    with open(file_path_to_profile, 'w') as f:
        f.write(astor.to_source(tree))
    
    return file_path_to_profile


# if __name__ == '__main__':
#     # Example usage:
#     decorator_to_add = "profile"  # Replace with your desired decorator
#     file_path = "base_file_no_decorator.py"  # Replace with the path to your file

#     add_decorator(file_path, decorator_to_add)
#     # os.listdir('/profile_computer/experimental')